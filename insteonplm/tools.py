"""Provides a raw console to test module and demonstrate usage."""
import argparse
import asyncio
from asynccmd import Cmd
import logging

import insteonplm
from insteonplm.address import Address
from insteonplm.devices import Device, ALDBStatus

__all__ = ('Tools', 'monitor', 'all_linking')

_LOGGING = logging.getLogger()


class Tools(Cmd):
    def __init__(self, loop, args=None):
        super().__init__(mode="Reader")
        # common variables
        self.loop = loop
        self.plm = None
        self.device = args.device
        self.workdir = args.workdir

        # all-link variables
        self.address = None
        self.linkcode = None
        self.group = None
        self.wait_time = 10

        if args:
            if args.verbose:
                level = logging.DEBUG
            else:
                level = logging.INFO

            if hasattr(args, 'address'):
                self.address = args.address
            if hasattr(args, 'group'):
                self.group = int(args.group)
            if hasattr(args, 'linkcode'):
                self.linkcode = int(args.linkcode)
            if hasattr(args, 'wait'):
                self.wait_time = int(args.wait)

        logging.basicConfig(level=level)

    @asyncio.coroutine
    def connect(self, poll_devices):
        _LOGGING.info('Connecting to Insteon PLM at %s', self.device)
        workdir = None if self.workdir == '' else self.workdir
        conn = yield from insteonplm.Connection.create(
            device=self.device, loop=self.loop,
            poll_devices=poll_devices,
             workdir=workdir)
        print('Setting up new device callback')
        conn.protocol.add_device_callback(self.async_new_device_callback)
        print('Setting up ALDB loaded callback')
        conn.protocol.add_all_link_done_callback(
            self.async_aldb_loaded_callback)
        self.plm = conn.protocol

    def async_new_device_callback(self, device):
        """Log that our new device callback worked."""
        _LOGGING.info('New Device: %s %02x %02x %s, %s',
                      device.id, device.cat, device.subcat,
                      device.description, device.model)
        'New Device: %s %02x %02x %s, %s'.format(
                      device.id, device.cat, device.subcat,
                      device.description, device.model)
        for state in device.states:
            device.states[state].register_updates(
                self.async_state_change_callback)

    def async_state_change_callback(self, id, state, value):
        _LOGGING.info('Device %s state %s value is changed to %02x',
                      id, state, value)
        'Device %s state %s value is changed to %02x'.format(
                      id, state, value)

    def async_aldb_loaded_callback(self):
        print('ALDB Loaded')

    @asyncio.coroutine
    def all_link_console(self,):
        yield from self.do_connect(False)
        self.plm.register_devices_loaded_callback(self.schedule_all_link)

    def schedule_all_link(self):
        asyncio.ensure_future(self.do_all_link())
        yield from asyncio.sleep(.01, loop=self.loop)

    @asyncio.coroutine
    def all_link(self, linkcode, group, address=None):
        _LOGGING.info('Starting the All-Linking process')
        if self.address != '':
            linkdevice = Device.create(self.plm, self.address, None, None)
            retries = 0
            while self.plm.devices[self.address] is None and retries < 3:
                _LOGGING.info('Attempting to link to device %s. '
                              'Waiting %d seconds.',
                              self.address, self.wait_time)
                self.plm.start_all_linking(self.linkcode, self.group)
                linkdevice.enter_linking_mode(group=self.group)
                retries = retries + 1
                yield from asyncio.sleep(self.wait_time, loop=self.loop)
        else:
            _LOGGING.info('Starting All-Linking on PLM. '
                          'Waiting for button press')
            self.plm.start_all_linking(self.linkcode, self.group)
            yield from asyncio.sleep(self.wait_time, loop=self.loop)

        _LOGGING.info('%d devices added to the All-Link Database',
                      len(self.plm.devices))
        yield from asyncio.sleep(.1, loop=self.loop)
        self.loop.stop()

    @asyncio.coroutine
    def list_devices(self):
        """List devices in the ALDB."""
        for addr in self.plm.devices:
            device = self.plm.devices[addr]
            _LOGGING.info('Device: %s %s [%s]',
                          device.address.human,
                          device.description,
                          device.model)

    @asyncio.coroutine
    def on_off_test(self, addr, group):
        """Test the on/off method of a device.

        Usage:
            on_off_test address [group]
        Arguments:
            address: Required - INSTEON address of the device
            group: Optional - All-Link group number. Defaults to 1
        """
        if addr:
            device = self.plm.devices[addr]

        if device:
            state = device.states[group]

        if state:
            if hasattr(state, 'on') and hasattr(state, 'off'):
                _LOGGING.info('Send on request')
                _LOGGING.info('----------------------')
                device.states[group].on()
                yield from asyncio.sleep(2, loop=self.loop)

                _LOGGING.info('Send off request')
                _LOGGING.info('----------------------')
                device.states[group].off()
                yield from asyncio.sleep(2, loop=self.loop)

                _LOGGING.info('Send on request')
                _LOGGING.info('----------------------')
                device.states[group].on()
                yield from asyncio.sleep(2, loop=self.loop)

                _LOGGING.info('Send off request')
                _LOGGING.info('----------------------')
                device.states[group].off()
                yield from asyncio.sleep(2, loop=self.loop)
            else:
                print('Device %s with state %d is not an on/off device.')

        else:
            print('Could not find device %s with state %d',
                  addr, group)

    @asyncio.coroutine
    def do_test4(self):
        for addr in self.plm.devices:
            device = self.plm.devices[addr]
            device.get_engine_version()
            yield from asyncio.sleep(.1, loop=self.loop)
            if device.engine_version is not None:
                _LOGGING.info('Addres: %s  DB Version: %s',
                                device.address, device.engine_version)
            else:
                _LOGGING.info('Addres: %s did not respond to engine '
                                'version request.')

    @asyncio.coroutine
    def get_device_aldb(self, addr):
        """Diplay the All-Link database for a device."""
        device = self.plm.devices[addr]
        if device:
            if not device.aldb:
                device.read_aldb()
            yield from asyncio.sleep(10, loop=self.loop)
            _LOGGING.info('Found %d records', len(device.aldb))
            if (not device.aldb or
                not device.aldb[-1].control_flags.is_high_water_mark):
                _LOGGING.info('Read failed.')
                device.aldb.clear()
            else:
                for record in device.aldb:
                    _LOGGING.info('ALDB record: %s', str(record))
        else:
            _LOGGING.info('Device not found.')

    @asyncio.coroutine
    def load_device_aldb(self, addr):
        """Read the device ALDB."""
        device = self.plm.devices[addr]
        if device:
            device.aldb.clear()
            device.read_aldb()
            yield from asyncio.sleep(10, loop=self.loop)
            _LOGGING.info('Found %d records', len(device.aldb))
            if (not device.aldb or
                not device.aldb[-1].control_flags.is_high_water_mark):
                _LOGGING.info('Read failed.')
                device.aldb.clear()
            else:
                for record in device.aldb:
                    _LOGGING.info('ALDB record: %s', str(record))

    @asyncio.coroutine
    def get_device_callbacks(self, addr):
        """List the callbacks for a device."""
        device_addr = Address(addr)
        for msg in self.plm.message_callbacks:
            if hasattr(msg, 'address'):
                if msg.address == device_addr:
                    _LOGGING.info('-------------- CALLBACK ---------------')
                    _LOGGING.info(msg)
                    _LOGGING.info(self.plm.message_callbacks[msg])


class Commander(Cmd):
    """Command object to manage itneractive sessions."""

    def __init__(self, loop, args):
        self.prompt = "insteonplm: "
        self.intro = ('INSTEON PLM interactive command processor. '
                      'Type `help` for a list of commands.')
        self.loop = loop
        self.tools = Tools(loop, args)

    def start_interactive(self):
        """Start the interactive command loop."""
        super().cmdloop(self.loop)

    def do_connect(self, args):
        """Connect to the PLM device.
        
        Usage:
            connect
        Arguments:
        """
        self.loop.create_task(self.tools.connect(False))

    def do_running_tasks(self, arg):
        """List running tasks.

        Usage:
            running_tasks
        Arguments:
        """
        for task in asyncio.Task.all_tasks(loop=self.loop):
            print(task)

    def do_on_off_test(self, args):
        """Test the on/off method of a device.

        Usage:
            on_off_test address [group]
        Arguments:
            address: Required - INSTEON address of the device
            group: Optional - All-Link group number. Defaults to 1
        """
        params = args.split()
        addr = None
        group = None

        try:
            addr = params[0]
        except IndexError:
            print('Device address required.')
            print('Usage: on_off_test address [group]')
        try:
            group_str = params[2]
            try:
                group = int(group_str)
            except ValueError:
                group = 1
        except IndexError:
            group = 1

        if addr:
            self.loop.create_task(self.tools.on_off_test(addr, group))

    def do_list_devices(self, args):
        """List devices loaded in the PLM.

        Usage:
            list_devices
        Arguments:
        """
        self.loop.create_task(self.tools.list_devices())

    def do_start_all_linking(self, args):
        """Place the PLM in All-Link mode.

        Usage:
            start_all_linking [linkcode [group]]
        Arguments:
            linkcode: 0 - PLM is responder
                      1 - PLM is controller
                      3 - PLM is controller or responder
                      Default 1
            group: All-Link group number (0 - 255). Default 0.
        """
        linkcode = 1
        group = 0
        params = args.split()
        if params:
            try:
                linkcode = params[0]
            except IndexError:
                linkcode = 1
            try:
                group = params[1]
            except IndexError:
                group = 0
        if linkcode in [0, 1, 3] and group >= 0 and group <= 255:
            self.loop.task(self.tools.start_all_linking(linkcode, group))
        else:
            _LOGGING('Could not start')

    def do_get_device_aldb(self, args):
        """Load the All-Link database for a devicedevice.

        Usage:
            get_device_aldb address
        Arguments:
            address: Required - INSTEON address of the device
        """
        params = args.split()
        addr = None
        group = None

        try:
            addr = params[0]
        except IndexError:
            print('Device address required.')
            print('Usage: device_aldb address')

        if addr:
            self.loop.create_task(self.tools.get_device_aldb(addr))

    def do_load_device_aldb(self, args):
        """Load the All-Link database for a devicedevice.

        Usage:
            load_device_aldb address
        Arguments:
            address: Required - INSTEON address of the device
        """
        params = args.split()
        addr = None
        group = None

        try:
            addr = params[0]
        except IndexError:
            print('Device address required.')
            print('Usage: load_device_aldb address')

        if addr:
            self.loop.create_task(self.tools.load_device_aldb(addr))

    def do_set_log_level(self, arg):
        """Set the log level.

        Usage:
            set_log_level i|v
        Parameters:
            log_level: i - info
                       v - verbose
    """
        if arg in ['i', 'v']:
            if arg == 'i':
                _LOGGING.setLevel(logging.INFO)
            else:
                _LOGGING.setLevel(logging.DEBUG)
        else:
            print('Log level incorrect.')
            self.do_help('set_log_level')

    def do_help(self, arg):
        """Help command.

        Usage:
            help [command]
        Parameters:
            command: Optional - command name to display detailed help
        """
        cmds = arg.split()

        if cmds:
            func = getattr(self, 'do_{}'.format(cmds[0]))
            if func:
                print(func.__doc__)
            else:
                print('Command ', cmds[0], ' not found.')
        else:
            print("Available command list: ")
            for curr_cmd in dir(self.__class__):
                if curr_cmd.startswith("do_") and not curr_cmd == 'do_test':
                    print(" - ", curr_cmd[3:])
            print("For help with a command type `help command`")

    def do_get_device_callbacks(self, args):
        """List the callbacks for a device.

        Usage:
            load_device_aldb address
        Arguments:
            address: Required - INSTEON address of the device
        """
        params = args.split()
        addr = None
        group = None

        try:
            addr = params[0]
        except IndexError:
            print('Device address required.')
            print('Usage: load_device_aldb address')

        if addr:
            self.loop.create_task(self.tools.get_device_callbacks(addr))

    def _emptyline(self, line):
        """Handler for empty line if entered.

        Override default behavior. Do nothing instead of repeating
        the last command.
        """
        pass


def monitor():
    """Connect to receiver and show events as they occur.

    Pulls the following arguments from the command line:

    :param device:
        Unix device where the PLM is attached
    :param address:
        Insteon address of the device to link with
    :param group:
        Insteon group for the link
    :param: linkcode
        Link direction: 0 - PLM is responder
                        1 - PLM is controller
                        3 - IM is responder or controller'
    :param verbose:
        Show debug logging.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='/dev/ttyUSB0',
                        help='Path to PLM device')
    parser.add_argument('--verbose', '-v', action='count',
                        help='Set logging level to verbose')
    parser.add_argument('-workdir', default='',
                        help='Working directory for reading and saving '
                        'device information.')

    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    monTool = Tools(loop, args)
    asyncio.ensure_future(monTool.do_connect())
    loop.run_forever()
    loop.close()


def all_linking():
    """Wrapper to call console with a loop."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='/dev/ttyUSB0',
                        help='Path to PLM device')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Set logging level to verbose')
    parser.add_argument('-a', '--address', default='',
                        help='Device to link to in the format of 1a2b3c. '
                        '(only works for i2 devices)')
    parser.add_argument('-g', '--group', default=1,
                        help='All-Link group number to link to')
    parser.add_argument('-l', '--linkcode', default=3,
                        help='Control flags: '
                        '0 - PLM is responder  '
                        '1 - PLM is controller '
                        '3 - IM is responder or controller')
    parser.add_argument('-w', '--wait', default=10,
                        help='Wait time for how long the PLM waits for a '
                        'device to respond to the All-Link request.')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    linkTool = Tools(loop, args)
    asyncio.ensure_future(linkTool.all_link_console(args))
    loop.run_forever()
    loop.close()


def interactive():
    """Wrapper for an interactive session for manual commands to be entered."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='/dev/ttyUSB0',
                        help='Path to PLM device')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Set logging level to verbose')
    parser.add_argument('-workdir', default='',
                        help='Working directory for reading and saving '
                        'device information.')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    cmd = Commander(loop, args)
    cmd.start_interactive()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        pending = asyncio.Task.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
        loop.close()
