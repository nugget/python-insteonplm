"""Provides a raw console to test module and demonstrate usage."""
import argparse
import asyncio
import logging
import string
import sys

import insteonplm
from insteonplm.address import Address
from insteonplm.devices import Device, ALDBStatus

__all__ = ('Tools', 'monitor', 'interactive')

_LOGGING = logging.getLogger()
PROMPT = 'insteonplm: '
INTRO = ('INSTEON PLM interactive command processor. '
         'Type `help` for a list of commands.')
ALLOWEDCHARS = string.ascii_letters + string.digits + '_'


class Tools():
    """Set of tools to support utility programs."""
    def __init__(self, loop, args=None):
        """Create Tools class."""
        # common variables
        self.loop = loop
        self.plm = insteonplm.PLM()
        self.device = args.device
        self.workdir = args.workdir

        # all-link variables
        self.address = None
        self.linkcode = None
        self.group = None
        self.wait_time = 10

        self.aldb_load_lock = asyncio.Lock(loop=loop)

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
    def connect(self, poll_devices=False, device=None):
        yield from self.aldb_load_lock.acquire()
        _LOGGING.info('Connecting to Insteon PLM at %s', self.device)
        conn_device = device if device else self.device
        workdir = None if self.workdir == '' else self.workdir
        conn = yield from insteonplm.Connection.create(
            device=conn_device, loop=self.loop,
            poll_devices=poll_devices,
            workdir=workdir)
        conn.protocol.add_device_callback(self.async_new_device_callback)
        conn.protocol.add_all_link_done_callback(
            self.async_aldb_loaded_callback)
        self.plm = conn.protocol
        yield from self.aldb_load_lock
        if self.aldb_load_lock.locked():
            self.aldb_load_lock.release()

    def async_new_device_callback(self, device):
        """Log that our new device callback worked."""
        _LOGGING.info(
            'New Device: %s cat: 0x%02x subcat: 0x%02x desc: %s, model: %s',
            device.id, device.cat, device.subcat,
            device.description, device.model)
        for state in device.states:
            device.states[state].register_updates(
                self.async_state_change_callback)

    def async_state_change_callback(self, id, state, value):
        _LOGGING.info('Device %s state %s value is changed to %02x',
                      id, state, value)

    def async_aldb_loaded_callback(self):
        if self.aldb_load_lock.locked():
            self.aldb_load_lock.release()
        _LOGGING.info('ALDB Loaded')

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

    def list_devices(self):
        """List devices in the ALDB."""
        for addr in self.plm.devices:
            device = self.plm.devices[addr]
            _LOGGING.info(
                'Device: %s cat: 0x%02x subcat: 0x%02x desc: %s, model: %s',
                device.address.human, device.cat, device.subcat,
                device.description, device.model

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

    def print_device_aldb(self, addr):
        """Diplay the All-Link database for a device."""
        device = self.plm.devices[addr]
        if device:
            if (device.aldb.status == ALDBStatus.LOADED or
                device.aldb.status == ALDBStatus.PARTIAL):
                if device.aldb.status == ALDBStatus.PARTIAL:
                    _LOGGING.info('ALDB partially loaded for device %s', addr)
                    _LOGGING.info('Some records missing.')
                for record in device.aldb:
                    _LOGGING.info('ALDB record: %s', record)
            else:
                _LOGGING.info('ALDB not loaded. '
                              'Use `load_device_aldb %s` first.',
                              device.address.hex)
        else:
            _LOGGING.info('Device not found.')

    def print_all_aldb(self):
        """Diplay the All-Link database for all devices."""
        for addr in self.plm.devices:
            _LOGGING.info('Printing ALDB for device %s', addr)
            self.print_device_aldb(addr)

    @asyncio.coroutine
    def load_device_aldb(self, addr):
        """Read the device ALDB."""
        device = self.plm.devices[addr]
        if device:
            device.aldb.clear()
            device.read_aldb()
            yield from asyncio.sleep(1, loop=self.loop)
            _LOGGING.info('ALDB status %s', device.aldb.status)
            while device.aldb.status == ALDBStatus.LOADING:
                yield from asyncio.sleep(1, loop=self.loop)
            if device.aldb.status == ALDBStatus.LOADED:
                _LOGGING.info('ALDB loaded for device %s', addr)
            self.print_device_aldb(addr)

    @asyncio.coroutine
    def load_all_aldb(self):
        """Read all devices ALDB."""
        for addr in self.plm.devices:
            yield from self.load_device_aldb(addr)


class Commander(object):
    """Command object to manage itneractive sessions."""

    def __init__(self, loop, args=None):
        self.loop = loop

        self.tools = Tools(loop, args)
        self.stdout = sys.stdout

    def start(self):
        self.loop.create_task(self._read_line())
        self.loop.create_task(self._greeting())

    @asyncio.coroutine
    def _read_line(self):
        while True:
            input = yield from self.loop.run_in_executor(None,
                                                         sys.stdin.readline)
            yield from self._exec_cmd(input)
            self.stdout.write(PROMPT)
            sys.stdout.flush()

    @asyncio.coroutine
    def _exec_cmd(self, input):
        return_val = None
        func = None
        if input.strip():
            command, arg = self._parse_cmd(input)
            if command is None:
                return self._invalid(input)
            if command == '':
                return self._invalid(input)
            else:
                try:
                    func = getattr(self, 'do_' + command)
                except AttributeError:
                    func = self._invalid
                except KeyboardInterrupt:
                    func = None  # func(arg)
            if func:
                if asyncio.iscoroutinefunction(func):
                    return_val = yield from func(arg)
                else:
                    return_val = func(arg)
        return return_val

    def _parse_cmd(self, input):
        input = input.strip()
        command = None
        arg = None
        if input:
            i, n = 0, len(input)
            while i < n and input[i] in ALLOWEDCHARS:
                i += 1
            command = input[:i]
            arg = input[i:].strip()
        return command, arg

    @staticmethod
    def _invalid(input):
        print("Invalid command: ", input)

    async def _greeting(self):
        print(INTRO)
        self.stdout.write(PROMPT)
        self.stdout.flush()

    @asyncio.coroutine
    def do_connect(self, args):
        """Connect to the PLM device.

        Usage:
            connect [device]
        Arguments:
            device: PLM device (default /dev/ttyUSB0)
        """
        params = args.split()
        device = '/dev/ttyUSB0'

        try:
            device = params[0]
        except IndexError:
            if self.tools.device:
                device = self.tools.device

        if device:
            yield from self.tools.connect(False, device)
        print('Connection complete.')

    def do_running_tasks(self, arg):
        """List tasks running in the background.

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
        """List devices loaded in the IM.

        Usage:
            list_devices
        Arguments:
        """
        self.tools.list_devices()

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
            self.loop.create_task(
                self.tools.start_all_linking(linkcode, group))
        else:
            _LOGGING('Could not start')

    def do_print_aldb(self, args):
        """Print the All-Link database for a device.

        Usage:
            print_aldb address|all
        Arguments:
            address: INSTEON address of the device
            all: Print the All-Link database for all devices

        This method requires that the device ALDB has been loaded.
        To load the device ALDB use the command:
            load_aldb address|all
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
            if addr.lower() == 'all':
                self.tools.print_all_aldb()
            else:
                self.tools.print_device_aldb(addr)

    @asyncio.coroutine
    def do_load_aldb(self, args):
        """Load the All-Link database for a device.

        Usage:
            load_aldb address|all
        Arguments:
            address: NSTEON address of the device
            all: Load the All-Link database for all devices
        """
        params = args.split()
        addr = None
        group = None

        try:
            addr = params[0]
        except IndexError:
            print('Device address required.')
            print('Usage: load_device_aldb address|all')

        if addr:
            if addr.lower() == 'all':
                yield from self.tools.load_all_aldb()
            else:
                yield from self.tools.load_device_aldb(addr)

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

    def do_set_device(self, args):
        """Set the PLM OS device.

        Device defaults to /dev/ttyUSB0

        Usage:
            set_device device
        Arguments:
            device: Required - INSTEON PLM device
        """
        params = args.split()
        device = None

        try:
            device = params[0]
        except IndexError:
            print('Device name required.')
            print('Usage: set_device device')

        if device:
            self.tools.device = device

    def do_set_workdir(self, args):
        """Set the working directory.

        The working directory is used to load and save known devices
        to improve startup times. During startup the application
        loads and saves a file `insteon_plm_device_info.dat`. This file
        is saved in the working directory. 

        The working directory has no default value. If the working directory is
        not set, the `insteon_plm_device_info.dat` file is not loaded or saved.

        Usage:
            set_workdir workdir
        Arguments:
            workdir: Required - Working directory to load and save devie list
        """
        params = args.split()
        workdir = None

        try:
            workdir = params[0]
        except IndexError:
            print('Device name required.')
            print('Usage: set_workdir workdir')

        if workdir:
            self.tools.workdir = workdir

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

    def do_exit(self, arg):
        """Exit the application."""
        print("Exiting")
        raise KeyboardInterrupt


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
    parser.add_argument('--workdir', default='',
                        help='Working directory for reading and saving '
                        'device information.')

    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    monTool = Tools(loop, args)
    asyncio.ensure_future(monTool.connect())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pending = asyncio.Task.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                pass
    loop.stop()
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
    cmd.start()
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
            except KeyboardInterrupt:
                pass
        loop.close()
