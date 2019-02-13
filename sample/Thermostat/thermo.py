"""Just a Sample of how to use Thermostats in insteaonplm."""
import logging
import asyncio
import argparse
import datetime
from decimal import Decimal
import yaml
import insteonplm
from insteonplm.constants import ThermostatMode

_LOGGING = logging.getLogger(__name__)


class thermo:
    """Will control the loops that monitor and update Thermostats."""

    def __init__(self, loop, args=None):
        """Constructor that will add the loop and the args to the class."""
        self.loop = loop
        self.aldbloaded = False
        self.load_lock = asyncio.Lock(loop=loop)

        self.plm = insteonplm.PLM()

        self.logfile = None
        self.workdir = None
        self.configfile = args.config

        if args.verbose:
            self.loglevel = logging.DEBUG
        else:
            self.loglevel = logging.INFO
        if hasattr(args, "workdir"):
            self.workdir = args.workdir
        if hasattr(args, "logfile"):
            self.logfile = args.logfile

        logging.basicConfig(level=self.loglevel, filename=self.logfile)
        _LOGGING.info(
            "Starting Up with logging set to: {0}.".format(self.loglevel))
        self.loadconfig()

    def loadconfig(self):
        """Will cause the tool to load it's configuration."""
        with open(self.configfile, 'r') as cfgfile:
            cfgsettings = yaml.load(cfgfile)
        _LOGGING.debug(cfgsettings)

        if 'device' not in cfgsettings:
            self.device = '/dev/ttyUSB0'
        else:
            self.device = cfgsettings['device']

        if 'overridetime' not in cfgsettings:
            self.overridetime = 3600
        else:
            self.overridetime = cfgsettings['overridetime']

        if 'cycletime' not in cfgsettings:
            self.cycletime = 30
        else:
            self.cycletime = cfgsettings['cycletime']

        # cycletime * theshold = how long to wait for forced refresh
        if 'cyclesperrefresh' not in cfgsettings:
            self.refreshcyclethreshold = 2
        else:
            self.refreshcyclethreshold = cfgsettings['cyclesperrefresh']

        self.zones = cfgsettings['zones']
        _LOGGING.debug(self.zones)

        for zone in self.zones:
            self.zones[zone]["allreporting"] = False
            for thermo in self.zones[zone]['thermos']:
                thermo["temp"] = Decimal(0)
                thermo["humidity"] = 0
                thermo["setpointheat"] = 0
                thermo["setpointcool"] = 0
                thermo["mode"] = None
                thermo["fan"] = None
                thermo["discovered"] = False
                thermo["reporting"] = False
                thermo["lasttimeset"] = None
                thermo["overridetime"] = None
                thermo["desiredpoint"] = 0
                thermo["desiredmode"] = None
                thermo["modeoverride"] = False
                thermo["tempoverride"] = False
                thermo["configrunning"] = False

    def start(self):
        """Starts the tool running.

        Should only be called after it is configured.
        """
        self.loop.create_task(self.connect())
        self.loop.create_task(self._myschedular())
        self.loop.create_task(self._myrefreshschedular())

    def async_new_device_callback(self, device):
        """Log that our new device callback worked."""
        _LOGGING.debug(
            'New Device: %s cat: 0x%02x subcat: 0x%02x desc: %s, model: %s',
            device.id, device.cat, device.subcat,
            device.description, device.model)

        for zone in self.zones:
            for thermo in self.zones[zone]['thermos']:
                if device.id == thermo['address']:
                    _LOGGING.info("Adding Callbacks for thermostat: {0}/{1}"
                                  .format(zone, thermo['name']))
                    thermo['discovered'] = True
                    device.temperature.register_updates(
                        self.async_thermo_state_change_callback)
                    device.humidity.register_updates(
                        self.async_thermo_state_change_callback)
                    device.system_mode.register_updates(
                        self.async_thermo_state_change_callback)
                    device.fan_mode.register_updates(
                        self.async_thermo_state_change_callback)
                    device.heat_set_point.register_updates(
                        self.async_thermo_state_change_callback)
                    device.cool_set_point.register_updates(
                        self.async_thermo_state_change_callback)

    def async_thermo_state_change_callback(self, addr, state, value):
        """Log the state change."""
        _LOGGING.debug('themo %s state %s value is changed to %s',
                       addr, state, value)
        for zone in self.zones:
            for thermo in self.zones[zone]['thermos']:
                if thermo["address"] == addr.id:
                    _LOGGING.debug("Setting it to: {0}/{1}"
                                   .format(zone, thermo["name"]))
                    if state == 0x01:
                        _LOGGING.debug("Setting Cool Set Point")
                        oldsetpoint = thermo["setpointcool"]
                        if value > 100:
                            newsetpoint = value / 2
                        else:
                            newsetpoint = value * 2
                        if newsetpoint != oldsetpoint:
                            thermo["setpointcool"] = newsetpoint
                            if (thermo["mode"] == ThermostatMode.COOL and
                                    thermo["desiredpoint"] != 0 and
                                    thermo["setpointcool"] !=
                                    thermo["desiredpoint"]):
                                thermo["tempoverride"] = True
                                if thermo["overridetime"] is None:
                                    thermo["overridetime"] \
                                        = datetime.datetime.now()
                            else:
                                thermo["tempoverride"] = False
                    if state == 0x02:
                        _LOGGING.debug("Setting Heat Set Point")
                        oldsetpoint = thermo["setpointheat"]
                        if value > 100:
                            newsetpoint = value / 2
                        else:
                            newsetpoint = value * 2
                        if newsetpoint != oldsetpoint:
                            thermo["setpointheat"] = newsetpoint
                            if (thermo["mode"] == ThermostatMode.HEAT and
                                    thermo["desiredpoint"] != 0 and
                                    thermo["setpointheat"] !=
                                    thermo["desiredpoint"]):
                                thermo["tempoverride"] = True
                                if thermo["overridetime"] is None:
                                    thermo["overridetime"] \
                                        = datetime.datetime.now()
                            else:
                                thermo["tempoverride"] = False
                    if state == 0x10:
                        _LOGGING.debug("Setting Mode")
                        oldmode = thermo["mode"]
                        newmode = value
                        if oldmode != newmode:
                            thermo["mode"] = newmode
                            if (thermo["desiredmode"] is not None and
                                    thermo["mode"] != thermo["desiredmode"]):
                                thermo["modeoverride"] = True
                                if thermo["overridetime"] is None:
                                    thermo["overridetime"] \
                                        = datetime.datetime.now()
                            else:
                                thermo["modeoverride"] = False
                    if state == 0x11:
                        _LOGGING.debug("Setting Fan")
                        thermo["fan"] = value
                    if state == 0x12:
                        _LOGGING.debug("Setting Temp")
                        thermo["temp"] = round(Decimal(value), 1)
                    if state == 0x13:
                        _LOGGING.debug("Setting Humidity")
                        thermo["humidity"] = value

                    thermo["reporting"] = True

    def async_aldb_loaded_callback(self):
        """Unlock the ALDB load lock when loading is complete."""
        if self.load_lock.locked():
            self.load_lock.release()
        _LOGGING.info('ALDB Loaded')
        self.aldbloaded = True

    def _determinethermo(self, zone, coolpoint, heatpoint):
        masterdesiredmode = None
        ismain = True
        for thermo in self.zones[zone]["thermos"]:
            _LOGGING.info("Now setting desired state for Thermo {0}/{1}"
                          " (is main: {2})"
                          .format(zone, thermo["name"], ismain))
            coolhighlow = (thermo[coolpoint] + thermo["tempbuffer"],
                           thermo[coolpoint] - thermo["tempbuffer"])
            heathighlow = (thermo[heatpoint] + thermo["tempbuffer"],
                           thermo[heatpoint] - thermo["tempbuffer"])
            if thermo["mode"] == ThermostatMode.COOL:
                if thermo["temp"] > coolhighlow[1]:
                    _LOGGING.info("      Cool should still be good. ({0}/{1})"
                                  .format(thermo["temp"], coolhighlow[1]))
                    thermo["desiredmode"] = ThermostatMode.COOL
                    thermo["desiredpoint"] = thermo[coolpoint]
                else:
                    _LOGGING.info("      Probably done with cooling ({0}/{1})"
                                  .format(thermo["temp"], coolhighlow[1]))
                    thermo["desiredmode"] = ThermostatMode.OFF
            elif thermo["mode"] == ThermostatMode.HEAT:
                if thermo["temp"] < heathighlow[0]:
                    _LOGGING.info("      Heat should still be good. ({0}/{1})"
                                  .format(thermo["temp"], heathighlow[0]))
                    thermo["desiredmode"] = ThermostatMode.HEAT
                    thermo["desiredpoint"] = thermo[heatpoint]
                else:
                    _LOGGING.info("      Probably done with heating ({0}/{1})"
                                  .format(thermo["temp"], heathighlow[0]))
                    thermo["desiredmode"] = ThermostatMode.OFF
            else:
                if thermo["temp"] > coolhighlow[0]:
                    _LOGGING.info("      Probably time to cool. ({0}/{1})"
                                  .format(thermo["temp"], coolhighlow[0]))
                    thermo["desiredmode"] = ThermostatMode.COOL
                    thermo["desiredpoint"] = thermo[coolpoint]
                elif thermo["temp"] < heathighlow[1]:
                    _LOGGING.info("      Probably time to heat. ({0}/{1})"
                                  .format(thermo["temp"], heathighlow[1]))
                    thermo["desiredmode"] = ThermostatMode.HEAT
                    thermo["desiredpoint"] = thermo[heatpoint]
                else:
                    _LOGGING.info("      Current Mode should"
                                  " still be good.")
                    thermo["desiredmode"] = thermo["mode"]
                    if thermo["mode"] == ThermostatMode.COOL:
                        thermo["desiredpoint"] = thermo[coolpoint]
                        _LOGGING.info("      ({0}/{1}/{2})".format(
                            coolhighlow[0], thermo["temp"], coolhighlow[1]))
                    else:
                        thermo["desiredpoint"] = thermo[heatpoint]
                        _LOGGING.info("      ({0}/{1}/{2})".format(
                            heathighlow[0], thermo["temp"], heathighlow[1]))
            if ismain is True:
                masterdesiredmode = thermo["desiredmode"]
                ismain = False
            else:
                if (masterdesiredmode == ThermostatMode.COOL and
                        thermo["desiredmode"] == ThermostatMode.HEAT):
                    _LOGGING.info("      Overriding to Off since Master is"
                                  " Cool and sub is Heat.")
                    thermo["desiredmode"] = ThermostatMode.OFF
                if (masterdesiredmode == ThermostatMode.HEAT and
                        thermo["desiredmode"] == ThermostatMode.COOL):
                    _LOGGING.info("      Overriding to Off since Master is"
                                  " Heat and sub is Cool.")
                    thermo["desiredmode"] = ThermostatMode.OFF
            _LOGGING.info("Will set to {0} with a set point of: {1}"
                          .format(thermo["desiredmode"],
                                  thermo["desiredpoint"]))

    async def connect(self):
        """Connect to the IM."""
        _LOGGING.info("Awaiting Lock to Load.")
        await self.load_lock.acquire()
        _LOGGING.info('Connecting to Insteon Modem at %s', self.device)
        conn = await insteonplm.Connection.create(
            device=self.device,
            loop=self.loop,
            workdir=self.workdir)
        _LOGGING.info('Connecton made to Insteon Modem at %s', self.device)
        conn.protocol.add_device_callback(self.async_new_device_callback)
        conn.protocol.add_all_link_done_callback(
            self.async_aldb_loaded_callback)

        self.plm = conn.protocol

    def _thermolog(self, zonename, thermo):
        if thermo['reporting'] is True:
            _LOGGING.info("Reporting on Zone/Thermo: {0}/{1}"
                          .format(zonename, thermo["name"]))
            _LOGGING.info("      Temp is: {0}".format(thermo["temp"]))
            _LOGGING.info("      Humidity is: {0}".format(thermo["humidity"]))
            _LOGGING.info("      Mode is: {0}".format(thermo["mode"]))
            _LOGGING.info("      Fan is: {0}".format(thermo["fan"]))
            _LOGGING.info("      Heat Set Point is: {0}"
                          .format(thermo["setpointheat"]))
            _LOGGING.info("      Cool Set Point is: {0}"
                          .format(thermo["setpointcool"]))
            _LOGGING.info("      Desired Mode is: {0}"
                          .format(thermo["desiredmode"]))
            _LOGGING.info("      Desired Set Point is: {0}"
                          .format(thermo["desiredpoint"]))
            _LOGGING.info("      Mode Override: {0}"
                          .format(thermo["modeoverride"]))
            _LOGGING.info("      Temp Override: {0}"
                          .format(thermo["tempoverride"]))
            _LOGGING.info("      Last Set Time: {0}"
                          .format(thermo["lasttimeset"]))
            _LOGGING.info("      Over Ride Start Time: {0}"
                          .format(thermo["overridetime"]))
        else:
            _LOGGING.info("The following isn't reporting yet: {0}/{1}"
                          .format(zonename, thermo["name"]))

    async def _thermorefresh(self, zone, thermo):
        if thermo["discovered"] is True:
            _LOGGING.info("Refreshing Thermo: {0}/{1}:{2}"
                          .format(zone, thermo["name"], thermo["address"]))
            thermodevice = self.plm.devices[thermo["address"]]

            # thermodevice.temperature.async_refresh_state()
            # await asyncio.sleep(2, loop=self.loop)
            # thermodevice.humidity.async_refresh_state()
            # await asyncio.sleep(2, loop=self.loop)
            # thermodevice.system_mode.async_refresh_state()
            # await asyncio.sleep(2, loop=self.loop)

            thermodevice.async_refresh_state()
        else:
            _LOGGING.info("Can't Refresh Thermo: {0}/{1}:{2},"
                          " it isn't discovered yet."
                          .format(zone, thermo["name"], thermo["address"]))
        await asyncio.sleep(4, loop=self.loop)

    async def _setthermos(self, zone):
        _LOGGING.info("Will set thermos.")
        now = datetime.datetime.now().time()
        daytime = self.zones[zone]["daystart"].split(':')
        daystart = datetime.time(int(daytime[0]), int(daytime[1]))
        nighttime = self.zones[zone]["nightstart"].split(':')
        nightstart = datetime.time(int(nighttime[0]), int(nighttime[1]))
        if daystart < now and now < nightstart:
            _LOGGING.info("Using Day Time Values")
            coolpoint = "daycool"
            heatpoint = "dayheat"
        else:
            _LOGGING.info("Using Night Time Values")
            coolpoint = "nightcool"
            heatpoint = "nightheat"
        self._determinethermo(zone, coolpoint, heatpoint)
        for thermo in self.zones[zone]["thermos"]:
            if thermo["configrunning"] is False:
                self.loop.create_task(self._configthermo(thermo))
            else:
                _LOGGING.info("Skipping config loop as its running for:"
                              " {0}/{1}".format(zone, thermo['name']))

    async def _configthermo(self, thermo):
        _LOGGING.info("Setting up Config loop for {0}".format(thermo["name"]))
        thermo["configrunning"] = True
        modeoverride = False
        tempoverride = False
        if thermo["overridetime"] is not None:
            timesinceoverride = (datetime.datetime.now()
                                 - thermo["overridetime"])
            if timesinceoverride.seconds > self.overridetime:
                _LOGGING.info("Time to reset override {0}/{1}."
                              .format(timesinceoverride.seconds,
                                      self.overridetime))
            else:
                _LOGGING.info("Will use overrides {0}/{1}."
                              .format(timesinceoverride.seconds,
                                      self.overridetime))
                modeoverride = thermo["modeoverride"]
                tempoverride = thermo["tempoverride"]
        else:
            _LOGGING.info("No Overrides to use.")
        thermocorrect = False
        while thermocorrect is False:
            _LOGGING.info("Now Checking Thermo config for {0}"
                          .format(thermo["name"]))
            thermodevice = self.plm.devices[thermo["address"]]
            thermocorrect = True
            if (modeoverride is False or
                    thermo["desiredmode"] != ThermostatMode.OFF):
                if thermo["mode"] != thermo["desiredmode"]:
                    _LOGGING.info("      Need to update mode.")
                    thermodevice.system_mode.set(thermo["desiredmode"])
                    await asyncio.sleep(2, loop=self.loop)
                    thermocorrect = False
            else:
                _LOGGING.info("Mode override in effect.")
            if tempoverride is False:
                if (thermo["desiredmode"] == ThermostatMode.COOL and
                        thermo["setpointcool"] != thermo["desiredpoint"]):
                    _LOGGING.info("      Need to update cool set point.")
                    thermodevice.cool_set_point.set(thermo["desiredpoint"])
                    await asyncio.sleep(2, loop=self.loop)
                    thermocorrect = False
                if (thermo["desiredmode"] == ThermostatMode.HEAT and
                        thermo["setpointheat"] != thermo["desiredpoint"]):
                    _LOGGING.info("      Need to update heat set point.")
                    thermodevice.heat_set_point.set(thermo["desiredpoint"])
                    await asyncio.sleep(2, loop=self.loop)
                    thermocorrect = False
            else:
                _LOGGING.info("Temp override in effect.")
            if thermocorrect is False:
                await asyncio.sleep(5, loop=self.loop)
        if modeoverride is False and tempoverride is False:
            thermo["overridetime"] = None
        thermo["configrunning"] = False
        thermo["lasttimeset"] = datetime.datetime.now()
        _LOGGING.info("Finished config loop for {0}".format(thermo["name"]))

    async def _myschedular(self):
        while self.loop.is_running():
            if self.aldbloaded is True:
                _LOGGING.info("Logging Loop started")
                for zone in self.zones:
                    self.zones[zone]["allreporting"] = True
                    for thermo in self.zones[zone]["thermos"]:
                        if thermo["reporting"] is False or thermo["temp"] == 0:
                            self.zones[zone]["allreporting"] = False
                        self._thermolog(zone, thermo)
                    if self.zones[zone]["allreporting"] is True:
                        await self._setthermos(zone)
            await asyncio.sleep(self.cycletime, loop=self.loop)

    async def _myrefreshschedular(self):
        while self.loop.is_running():
            if self.aldbloaded is True:
                _LOGGING.info("Refresh Loop started")
                for zone in self.zones:
                    for thermo in self.zones[zone]["thermos"]:
                        await self._thermorefresh(zone, thermo)
            await asyncio.sleep(
                (self.cycletime * self.refreshcyclethreshold),
                loop=self.loop)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('-v', '--verbose', action='count',
                        help='Set logging level to verbose')
    parser.add_argument('-l', '--logfile', default='', help='Log file name')
    parser.add_argument('--workdir', default='',
                        help='Working directory for device cache.')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    thermocontrol = thermo(loop, args)
    thermocontrol.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        _LOGGING.info("User killed...")
        # if thermocontrol.plm:
        #     if thermocontrol.plm.transport:
        #         _LOGGING.info('Closing the session')
        #         asyncio.ensure_future(
        #               thermocontrol.plm.transport.close(),
        #               loop=loop
        #               )
        loop.stop()
        pending = asyncio.Task.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                pass
        loop.close()
    _LOGGING.info("See you later.")
