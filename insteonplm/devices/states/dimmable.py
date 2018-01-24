from .stateBase import StateBase
from insteonplm.constants import *

class DimmableSwitch(StateBase):
    """Device state representing an On/Off switch that is controllable.

    Available methods are:
    on(self, onlevel)
    set_level(self, onlevel)
    off()
    async_refresh_state()
    connect()
    update(self, val)
    async_refresh_state()
    """

    def __init__(self, plm, device, statename, group, defaultvalue=None):
        State.__init__(self, plm, device, statename, group, self._status_request, defaultvalue)

    def on(self, onlevel=0xff):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_0X11_NONE, onlevel)

    def set_level(self, onlevel=0xff):
        self.on(onlevel)

    def off(self):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_0X13_0X00)

    def _status_request(self):
        self._device.set_status_callback(self._status_received)
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)

    def _status_received(self, msg):
        self.update(msg.cmd2)

class DimmableSwitch_Fan(DimmableSwitch):
    """Device state representing a the fan switch that is controllable.

    Available methods are:
    on(self, onlevel)
    set_level(self, onlevel)
    off(self)
    async_refresh_state(self)
    connect(self, call_back)
    update(self, val)
    async_refresh_state(self)
    """

    def _status_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting SwitchedLightingControl_2663_222._status_update_received')
        self._nextCommandIsStatus = False
        if msg.cmd2 == 0x00 or msg.cmd2 == 0x02:
            self.log.debug('Sending Top Outlet %s Off', self._device.address)
            device2.lightOnLevel.update(0x00)
        elif msg.cmd2 == 0x01 or msg.cmd2 == 0x03:
            self.log.debug('Sending Top Outlet %s On', self._device.address)
            self.update(device2.id, 0xff)
        else:
            raise ValueError
        self.log.debug('Starting SwitchedLightingControl_2663_222._status_update_received')


class OnOffSwitch_OutletBottom(StateBase):
    """Device state representing a the bottom outlet On/Off switch that is controllable.

    Available methods are:
    on(self)
    off(self)
    async_refresh_state(self)
    connect(self, call_back)
    update(self, val)
    async_refresh_state(self)
    """

    def __init__(self, plm, device, statename, group, defaultvalue=None):
        State.__init__(self, plm, device, statename, group, self._status_request, defaultvalue)

    def on(self):
        userdata = {'d1':self._group}
        self._plm.send_extended(self._address.hex, COMMAND_LIGHT_ON_0X11_NONE, 0xff, **userdata)

    def off(self):
        userdata = {'d1':self._group}
        self._plm.send_extended(self._address.hex, COMMAND_LIGHT_OFF_0X13_0X00, **userdata)

    def _status_request(self):
        self._device.set_status_callback(self._status_received)
        self._plm.send_standard(self.address.hex, {'cmd1':0x19, 'cmd2':0x01})

    def _status_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting SwitchedLightingControl_2663_222._status_update_received')
        self._nextCommandIsStatus = False
        if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
            self.log.debug('Sending Bottom Outlet %s Off', self._device.address)
            device2.lightOnLevel.update(0x00)
        elif msg.cmd2 == 0x02 or msg.cmd2 == 0x03:
            self.log.debug('Sending Bottom Outlet %s On', self._device.address)
            self.update(device2.id, 0xff)
        else:
            raise ValueError
        self.log.debug('Starting SwitchedLightingControl_2663_222._status_update_received')


