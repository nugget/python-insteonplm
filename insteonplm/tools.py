"""Provides a raw console to test module and demonstrate usage."""
# pylint: disable=too-many-lines
import argparse
import asyncio
import binascii
import logging
import string
import sys

import insteonplm
from insteonplm.address import Address
from insteonplm.devices import create, ALDBStatus

__all__ = ('Tools', 'Commander', 'monitor', 'interactive')
_LOGGING = logging.getLogger(__name__)
_INSTEONPLM_LOGGING = logging.getLogger('insteonplm')
PROMPT = 'insteonplm: '
INTRO = ('INSTEON PLM interactive command processor.\n'
         'Type `help` for a list of commands.\n\n'
         'This command line tool is still in development.\n'
         '!!!! Please be VERY careful with the `write_aldb` command !!!!!!!')
ALLOWEDCHARS = string.ascii_letters + string.digits + '_'


# pylint: disable=too-many-instance-attributes
class Tools():
    """Set of tools to support utility programs."""

    def __init__(self, loop, args=None):
        """Create Tools class."""
        # common variables
        self.loop = loop
        self.plm = insteonplm.PLM()
        self.logfile = None
        self.workdir = None
        self.loglevel = logging.INFO

        # connection variables
        self.device = args.device
        self.username = None
        self.password = None
        self.host = None
        self.port = None

        # all-link variables
        self.address = None
        self.linkcode = None
        self.group = None
        self.wait_time = 10

        self.aldb_load_lock = asyncio.Lock(loop=loop)

        if args:
            if args.verbose:
                self.loglevel = logging.DEBUG
            else:
                self.loglevel = logging.INFO

            if hasattr(args, "workdir"):
                self.workdir = args.workdir
            if hasattr(args, "logfile"):
                self.logfile = args.logfile
            if hasattr(args, 'address'):
                self.address = args.address
            if hasattr(args, 'group'):
                self.group = int(args.group)
            if hasattr(args, 'linkcode'):
                self.linkcode = int(args.linkcode)
            if hasattr(args, 'wait'):
                self.wait_time = int(args.wait)

        if self.logfile:
            logging.basicConfig(level=self.loglevel, filename=self.logfile)
        else:
            _LOGGING.info('Settig log level to %s', self.loglevel)
            _LOGGING.setLevel(self.loglevel)
            _INSTEONPLM_LOGGING.setLevel(self.loglevel)

    async def connect(self, poll_devices=False, device=None, workdir=None):
        """Connect to the IM."""
        await self.aldb_load_lock.acquire()
        device = self.host if self.host else self.device
        _LOGGING.info('Connecting to Insteon Modem at %s', device)
        self.device = device if device else self.device
        self.workdir = workdir if workdir else self.workdir
        conn = await insteonplm.Connection.create(
            device=self.device,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            loop=self.loop,
            poll_devices=poll_devices,
            workdir=self.workdir)
        _LOGGING.info('Connecton made to Insteon Modem at %s', device)
        conn.protocol.add_device_callback(self.async_new_device_callback)
        conn.protocol.add_all_link_done_callback(
            self.async_aldb_loaded_callback)
        self.plm = conn.protocol
        await self.aldb_load_lock
        if self.aldb_load_lock.locked():
            self.aldb_load_lock.release()

    async def monitor_mode(self, poll_devices=False, device=None,
                           workdir=None):
        """Place the IM in monitoring mode."""
        print("Running monitor mode")
        await self.connect(poll_devices, device, workdir)
        self.plm.monitor_mode()

    def async_new_device_callback(self, device):
        """Log that our new device callback worked."""
        _LOGGING.info(
            'New Device: %s cat: 0x%02x subcat: 0x%02x desc: %s, model: %s',
            device.id, device.cat, device.subcat,
            device.description, device.model)
        for state in device.states:
            device.states[state].register_updates(
                self.async_state_change_callback)

    # pylint: disable=no-self-use
    def async_state_change_callback(self, addr, state, value):
        """Log the state change."""
        _LOGGING.info('Device %s state %s value is changed to %s',
                      addr, state, value)

    def async_aldb_loaded_callback(self):
        """Unlock the ALDB load lock when loading is complete."""
        if self.aldb_load_lock.locked():
            self.aldb_load_lock.release()
        _LOGGING.info('ALDB Loaded')

    async def start_all_linking(self, linkcode, group, address=None):
        """Start the All-Linking process with the IM and device."""
        _LOGGING.info('Starting the All-Linking process')
        if address:
            linkdevice = self.plm.devices[Address(address).id]
            if not linkdevice:
                linkdevice = create(self.plm, address, None, None)
            _LOGGING.info('Attempting to link the PLM to device %s. ',
                          address)
            self.plm.start_all_linking(linkcode, group)
            asyncio.sleep(.5, loop=self.loop)
            linkdevice.enter_linking_mode(group=group)
        else:
            _LOGGING.info('Starting All-Linking on PLM. '
                          'Waiting for button press')
            self.plm.start_all_linking(linkcode, group)
            await asyncio.sleep(self.wait_time, loop=self.loop)

        _LOGGING.info('%d devices added to the All-Link Database',
                      len(self.plm.devices))
        await asyncio.sleep(.1, loop=self.loop)

    def list_devices(self):
        """List devices in the ALDB."""
        if self.plm.devices:
            for addr in self.plm.devices:
                device = self.plm.devices[addr]
                if device.address.is_x10:
                    _LOGGING.info('Device: %s %s', device.address.human,
                                  device.description)
                else:
                    _LOGGING.info('Device: %s cat: 0x%02x subcat: 0x%02x '
                                  'desc: %s, model: %s',
                                  device.address.human, device.cat,
                                  device.subcat, device.description,
                                  device.model)
        else:
            _LOGGING.info('No devices found')
            if not self.plm.transport:
                _LOGGING.info('IM connection has not been made.')
                _LOGGING.info('Use `connect [device]` to open the connection')

    async def on_off_test(self, addr, group):
        """Test the on/off method of a device.

        Usage:
            on_off_test address [group]
        Arguments:
            address: Required - INSTEON address of the device
            group: Optional - All-Link group number. Defaults to 1
        """
        device = None
        state = None
        if addr:
            dev_addr = Address(addr)
            device = self.plm.devices[dev_addr.id]

        if device:
            state = device.states[group]

        if state:
            if hasattr(state, 'on') and hasattr(state, 'off'):
                _LOGGING.info('Send on request')
                _LOGGING.info('----------------------')
                device.states[group].on()
                await asyncio.sleep(2, loop=self.loop)

                _LOGGING.info('Send off request')
                _LOGGING.info('----------------------')
                device.states[group].off()
                await asyncio.sleep(2, loop=self.loop)

                _LOGGING.info('Send on request')
                _LOGGING.info('----------------------')
                device.states[group].on()
                await asyncio.sleep(2, loop=self.loop)

                _LOGGING.info('Send off request')
                _LOGGING.info('----------------------')
                device.states[group].off()
                await asyncio.sleep(2, loop=self.loop)
            else:
                _LOGGING.warning('Device %s with state %d is not an on/off'
                                 'device.', device.id, state.name)

        else:
            _LOGGING.error('Could not find device %s', addr)

    def print_device_aldb(self, addr):
        """Diplay the All-Link database for a device."""
        if Address(addr).id == self.plm.address.id:
            device = self.plm
        else:
            dev_addr = Address(addr)
            device = self.plm.devices[dev_addr.id]
        if device:
            if device.aldb.status in [ALDBStatus.LOADED, ALDBStatus.PARTIAL]:
                if device.aldb.status == ALDBStatus.PARTIAL:
                    _LOGGING.info('ALDB partially loaded for device %s', addr)
                for mem_addr in device.aldb:
                    record = device.aldb[mem_addr]
                    _LOGGING.debug('mem_addr: %s', mem_addr)
                    _LOGGING.info('ALDB record: %s', record)
            else:
                _LOGGING.info('ALDB not loaded. '
                              'Use `load_aldb %s` first.',
                              device.address.id)
        else:
            _LOGGING.info('Device not found.')

    def print_all_aldb(self):
        """Diplay the All-Link database for all devices."""
        addr = self.plm.address.id
        _LOGGING.info('ALDB for PLM device %s', addr)
        self.print_device_aldb(addr)
        if self.plm.devices:
            for addr in self.plm.devices:
                _LOGGING.info('ALDB for device %s', addr)
                self.print_device_aldb(addr)
        else:
            _LOGGING.info('No devices found')
            if not self.plm.transport:
                _LOGGING.info('IM connection has not been made.')
                _LOGGING.info('Use `connect [device]` to open the connection')

    async def load_device_aldb(self, addr, clear=True):
        """Read the device ALDB."""
        dev_addr = Address(addr)
        device = None
        if dev_addr == self.plm.address:
            device = self.plm
        else:
            device = self.plm.devices[dev_addr.id]
        if device:
            if clear:
                device.aldb.clear()
            device.read_aldb()
            await asyncio.sleep(1, loop=self.loop)
            while device.aldb.status == ALDBStatus.LOADING:
                await asyncio.sleep(1, loop=self.loop)
            if device.aldb.status == ALDBStatus.LOADED:
                _LOGGING.info('ALDB loaded for device %s', addr)
            self.print_device_aldb(addr)
        else:
            _LOGGING.error('Could not find device %s', addr)

    async def load_all_aldb(self, clear=True):
        """Read all devices ALDB."""
        for addr in self.plm.devices:
            await self.load_device_aldb(addr, clear)

    async def write_aldb(self, addr, mem_addr: int, mode: str, group: int,
                         target, data1=0x00, data2=0x00, data3=0x00):
        """Write a device All-Link record."""
        dev_addr = Address(addr)
        target_addr = Address(target)
        device = self.plm.devices[dev_addr.id]
        if device:
            _LOGGING.debug('calling device write_aldb')
            device.write_aldb(mem_addr, mode, group, target_addr,
                              data1, data2, data3)
            await asyncio.sleep(1, loop=self.loop)
            while device.aldb.status == ALDBStatus.LOADING:
                await asyncio.sleep(1, loop=self.loop)
            self.print_device_aldb(addr)

    async def del_aldb(self, addr, mem_addr: int):
        """Write a device All-Link record."""
        dev_addr = Address(addr)
        device = self.plm.devices[dev_addr.id]
        if device:
            _LOGGING.debug('calling device del_aldb')
            device.del_aldb(mem_addr)
            await asyncio.sleep(1, loop=self.loop)
            while device.aldb.status == ALDBStatus.LOADING:
                await asyncio.sleep(1, loop=self.loop)
            self.print_device_aldb(addr)

    def add_device_override(self, addr, cat, subcat, firmware=None):
        """Add a device override to the PLM."""
        self.plm.devices.add_override(addr, 'cat', cat)
        self.plm.devices.add_override(addr, 'subcat', subcat)
        if firmware:
            self.plm.devices.add_override(addr, 'firmware', firmware)

    def add_x10_device(self, housecode, unitcode, dev_type):
        """Add an X10 device to the PLM."""
        device = None
        try:
            device = self.plm.devices.add_x10_device(self.plm, housecode,
                                                     unitcode, dev_type)
        except ValueError:
            pass
        return device

    def kpl_status(self, address, group):
        """Get the status of a KPL button."""
        addr = Address(address)
        device = self.plm.devices[addr.id]
        device.states[group].async_refresh_state()

    def kpl_on(self, address, group):
        """Get the status of a KPL button."""
        addr = Address(address)
        device = self.plm.devices[addr.id]
        device.states[group].on()

    def kpl_off(self, address, group):
        """Get the status of a KPL button."""
        addr = Address(address)
        device = self.plm.devices[addr.id]
        device.states[group].off()

    def kpl_set_on_mask(self, address, group, mask):
        """Get the status of a KPL button."""
        addr = Address(address)
        device = self.plm.devices[addr.id]
        device.states[group].set_on_mask(mask)


# pylint: disable=too-many-public-methods
class Commander():
    """Command object to manage itneractive sessions."""

    def __init__(self, loop, args=None):
        """Init the Commander class."""
        self.loop = loop

        self.tools = Tools(loop, args)
        self.stdout = sys.stdout

    def start(self):
        """Start the command process loop."""
        self.loop.create_task(self._read_line())
        self.loop.create_task(self._greeting())

    async def _read_line(self):
        while True:
            cmd = await self.loop.run_in_executor(None, sys.stdin.readline)
            await self._exec_cmd(cmd)
            self.stdout.write(PROMPT)
            sys.stdout.flush()

    async def _exec_cmd(self, cmd):
        return_val = None
        func = None
        if cmd.strip():
            command, arg = self._parse_cmd(cmd)
            if command is None:
                return self._invalid(cmd)
            if command == '':
                return self._invalid(cmd)

            try:
                func = getattr(self, 'do_' + command)
            except AttributeError:
                func = self._invalid
                arg = str(cmd)
            except KeyboardInterrupt:
                func = None  # func(arg)
            if func:
                if asyncio.iscoroutinefunction(func):
                    return_val = await func(arg)
                else:
                    return_val = func(arg)
        return return_val

    # pylint: disable=no-self-use
    def _parse_cmd(self, cmd):
        cmd = cmd.strip()
        command = None
        arg = None
        if cmd:
            i, n = 0, len(cmd)
            while i < n and cmd[i] in ALLOWEDCHARS:
                i += 1
            command = cmd[:i]
            arg = cmd[i:].strip()
        return command, arg

    @staticmethod
    def _invalid(cmd):
        _LOGGING.error("Invalid command: %s", cmd[:-1])

    async def _greeting(self):
        _LOGGING.info(INTRO)
        self.stdout.write(PROMPT)
        self.stdout.flush()

    async def do_connect(self, args):
        """Connect to the PLM device.

        Usage:
            connect [device [workdir]]
        Arguments:
            device: PLM device (default /dev/ttyUSB0)
            workdir: Working directory to save and load device information
        """
        params = args.split()
        device = '/dev/ttyUSB0'
        workdir = None

        try:
            device = params[0]
        except IndexError:
            if self.tools.device:
                device = self.tools.device
        try:
            workdir = params[1]
        except IndexError:
            if self.tools.workdir:
                workdir = self.tools.workdir

        if device:
            await self.tools.connect(False, device=device, workdir=workdir)
        _LOGGING.info('Connection complete.')

    # pylint: disable=unused-argument
    def do_running_tasks(self, arg):
        """List tasks running in the background.

        Usage:
            running_tasks
        Arguments:
        """
        for task in asyncio.Task.all_tasks(loop=self.loop):
            _LOGGING.info(task)

    async def do_on_off_test(self, args):
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
            addr = None

        try:
            group = int(params[1])
        except ValueError:
            group = None
        except IndexError:
            group = 1

        if addr and group:
            await self.tools.on_off_test(addr, group)
        else:
            _LOGGING.error('Invalid address or group')
            self.do_help('on_off_test')

    # pylint: disable=unused-argument
    def do_list_devices(self, args):
        """List devices loaded in the IM.

        Usage:
            list_devices
        Arguments:
        """
        self.tools.list_devices()

    def do_add_all_link(self, args):
        """Add an All-Link record to the IM and a device.

        Usage:
            add_all_link [linkcode] [group] [address]
        Arguments:
            linkcode: 0 - PLM is responder
                      1 - PLM is controller
                      3 - PLM is controller or responder
                      Default 1
            group: All-Link group number (0 - 255). Default 0.
            address: INSTEON device to link with (not supported by all devices)
        """
        linkcode = 1
        group = 0
        addr = None
        params = args.split()
        if params:
            try:
                linkcode = int(params[0])
            except IndexError:
                linkcode = 1
            except ValueError:
                linkcode = None

            try:
                group = int(params[1])
            except IndexError:
                group = 0
            except ValueError:
                group = None

            try:
                addr = params[2]
            except IndexError:
                addr = None

        if linkcode in [0, 1, 3] and 255 >= group >= 0:
            self.loop.create_task(
                self.tools.start_all_linking(linkcode, group, addr))
        else:
            _LOGGING.error('Link code %d or group number %d not valid',
                           linkcode, group)
            self.do_help('add_all_link')

    def do_del_all_link(self, args):
        """Delete an All-Link record to the IM and a device.

        Usage:
            add_all_link [group] [address]
        Arguments:
            group: All-Link group number (0 - 255). Default 0.
            address: INSTEON device to unlink (not supported by all devices)
        """
        linkcode = 255
        group = 0
        addr = None
        params = args.split()
        if params:
            try:
                group = int(params[0])
            except IndexError:
                group = 0
            except ValueError:
                group = None

            try:
                addr = params[1]
            except IndexError:
                addr = None

        if group and 0 <= group <= 255:
            self.loop.create_task(
                self.tools.start_all_linking(linkcode, group, addr))
        else:
            _LOGGING.error('Group number not valid')
            self.do_help('del_all_link')

    def do_print_aldb(self, args):
        """Print the All-Link database for a device.

        Usage:
            print_aldb address|plm|all
        Arguments:
            address: INSTEON address of the device
            plm: Print the All-Link database for the PLM
            all: Print the All-Link database for all devices

        This method requires that the device ALDB has been loaded.
        To load the device ALDB use the command:
            load_aldb address|plm|all
        """
        params = args.split()
        addr = None

        try:
            addr = params[0]
        except IndexError:
            _LOGGING.error('Device address required.')
            self.do_help('print_aldb')

        if addr:
            if addr.lower() == 'all':
                self.tools.print_all_aldb()
            elif addr.lower() == 'plm':
                addr = self.tools.plm.address.id
                self.tools.print_device_aldb(addr)
            else:
                self.tools.print_device_aldb(addr)

    def do_set_hub_connection(self, args):
        """Set Hub connection parameters.

        Usage:
            set_hub_connection username password host [port]

        Arguments:
            username: Hub username
            password: Hub password
            host: host name or IP address
            port: IP port [default 25105]
        """
        params = args.split()
        username = None
        password = None
        host = None
        port = None

        try:
            username = params[0]
            password = params[1]
            host = params[2]
            port = params[3]
        except IndexError:
            pass

        if username and password and host:
            if not port:
                port = 25105
            self.tools.username = username
            self.tools.password = password
            self.tools.host = host
            self.tools.port = port
        else:
            _LOGGING.error('username password host are required')
            self.do_help('set_hub_connection')

    def do_set_log_file(self, args):
        """Set the log file.

        Usage:
            set_log_file filename
        Parameters:
            filename: log file name to write to

        THIS CAN ONLY BE CALLED ONCE AND MUST BE CALLED
        BEFORE ANY LOGGING STARTS.
        """
        params = args.split()
        try:
            filename = params[0]
            logging.basicConfig(filename=filename)
        except IndexError:
            self.do_help('set_log_file')

    async def do_load_aldb(self, args):
        """Load the All-Link database for a device.

        Usage:
            load_aldb address|all [clear_prior]
        Arguments:
            address: NSTEON address of the device
            all: Load the All-Link database for all devices
            clear_prior: y|n
                         y - Clear the prior data and start fresh.
                         n - Keep the prior data and only apply changes
                         Default is y
        This does NOT write to the database so no changes are made to the
        device with this command.
        """
        params = args.split()
        addr = None
        clear = True

        try:
            addr = params[0]
        except IndexError:
            _LOGGING.error('Device address required.')
            self.do_help('load_aldb')

        try:
            clear_prior = params[1]
            _LOGGING.info('param clear_prior %s', clear_prior)
            if clear_prior.lower() == 'y':
                clear = True
            elif clear_prior.lower() == 'n':
                clear = False
            else:
                _LOGGING.error('Invalid value for parameter `clear_prior`')
                _LOGGING.error('Valid values are `y` or `n`')
        except IndexError:
            pass

        if addr:
            if addr.lower() == 'all':
                await self.tools.load_all_aldb(clear)
            else:
                await self.tools.load_device_aldb(addr, clear)
        else:
            self.do_help('load_aldb')

    async def do_write_aldb(self, args):
        """Write device All-Link record.

        WARNING THIS METHOD CAN DAMAGE YOUR DEVICE IF USED INCORRECTLY.
        Please ensure the memory id is appropriate for the device.
        You must load the ALDB of the device before using this method.
        The memory id must be an existing memory id in the ALDB or this
        method will return an error.

        If you are looking to create a new link between two devices,
        use the `link_devices` command or the `start_all_linking` command.

        Usage:
           write_aldb addr memory mode group target [data1 data2 data3]

        Required Parameters:
            addr: Inseon address of the device to write
            memory: record ID of the record to write (i.e. 0fff)
            mode: r | c
                    r = Device is a responder of target
                    c = Device is a controller of target
            group:  All-Link group integer
            target: Insteon address of the link target device

        Optional Parameters:
            data1: int = Device sepcific
            data2: int = Device specific
            data3: int = Device specific
        """
        params = args.split()
        addr = None
        mem_bytes = None
        memory = None
        mode = None
        group = None
        target = None
        data1 = 0x00
        data2 = 0x00
        data3 = 0x00

        try:
            addr = Address(params[0])
            mem_bytes = binascii.unhexlify(params[1])
            memory = int.from_bytes(mem_bytes, byteorder='big')
            mode = params[2]
            group = int(params[3])
            target = Address(params[4])

            _LOGGING.info('address: %s', addr)
            _LOGGING.info('memory: %04x', memory)
            _LOGGING.info('mode: %s', mode)
            _LOGGING.info('group: %d', group)
            _LOGGING.info('target: %s', target)

        except IndexError:
            _LOGGING.error('Device address memory mode group and target '
                           'are all required.')
            self.do_help('write_aldb')
        except ValueError:
            _LOGGING.error('Value error - Check parameters')
            self.do_help('write_aldb')

        try:
            data1 = int(params[5])
            data2 = int(params[6])
            data3 = int(params[7])
        except IndexError:
            pass
        except ValueError:
            addr = None
            _LOGGING.error('Value error - Check parameters')
            self.do_help('write_aldb')
            return

        if addr and memory and mode and isinstance(group, int) and target:
            await self.tools.write_aldb(addr, memory, mode, group, target,
                                        data1, data2, data3)

    async def do_del_aldb(self, args):
        """Delete device All-Link record.

        WARNING THIS METHOD CAN DAMAGE YOUR DEVICE IF USED INCORRECTLY.
        Please ensure the memory id is appropriate for the device.
        You must load the ALDB of the device before using this method.
        The memory id must be an existing memory id in the ALDB or this
        method will return an error.

        If you are looking to create a new link between two devices,
        use the `link_devices` command or the `start_all_linking` command.

        Usage:
           del_aldb addr memory

        Required Parameters:
            addr: Inseon address of the device to write
            memory: record ID of the record to write (i.e. 0fff)
        """
        params = args.split()
        addr = None
        mem_bytes = None
        memory = None

        try:
            addr = Address(params[0])
            mem_bytes = binascii.unhexlify(params[1])
            memory = int.from_bytes(mem_bytes, byteorder='big')

            _LOGGING.info('address: %s', addr)
            _LOGGING.info('memory: %04x', memory)

        except IndexError:
            _LOGGING.error('Device address and memory are required.')
            self.do_help('del_aldb')
        except ValueError:
            _LOGGING.error('Value error - Check parameters')
            self.do_help('write_aldb')

        if addr and memory:
            await self.tools.del_aldb(addr, memory)

    def do_set_log_level(self, arg):
        """Set the log level.

        Usage:
            set_log_level i|v
        Parameters:
            log_level: i - info | v - verbose

        """
        if arg in ['i', 'v']:
            _LOGGING.info('Setting log level to %s', arg)
            if arg == 'i':
                _LOGGING.setLevel(logging.INFO)
                _INSTEONPLM_LOGGING.setLevel(logging.INFO)
            else:
                _LOGGING.setLevel(logging.DEBUG)
                _INSTEONPLM_LOGGING.setLevel(logging.DEBUG)
        else:
            _LOGGING.error('Log level value error.')
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
            _LOGGING.error('Device name required.')
            self.do_help('set_device')

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
            _LOGGING.error('Device name required.')
            self.do_help('set_workdir')

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
                _LOGGING.info(func.__doc__)
            else:
                _LOGGING.error('Command %s not found', cmds[0])
        else:
            _LOGGING.info("Available command list: ")
            for curr_cmd in dir(self.__class__):
                if curr_cmd.startswith("do_") and not curr_cmd == 'do_test':
                    print(" - ", curr_cmd[3:])
            _LOGGING.info("For help with a command type `help command`")

    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    def do_exit(self, arg):
        """Exit the application."""
        _LOGGING.info("Exiting")
        raise KeyboardInterrupt

    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    def do_test_logger(self, arg):
        """Test the logging function."""
        _LOGGING.error("This is an error")
        _LOGGING.warning("This is a warning")
        _LOGGING.info("This is an info")
        _LOGGING.debug("This is a debug")

    def do_add_device_override(self, args):
        """Add a device override to the IM.

        Usage:
            add_device_override address cat subcat [firmware]

        Arguments:
            address: Insteon address of the device to override
            cat: Device category
            subcat: Device subcategory
            firmware: Optional - Device firmware

        The device address can be written with our without the dots and in
        upper or lower case, for example: 1a2b3c or 1A.2B.3C.

        The category, subcategory and firmware numbers are written in hex
        format, for example: 0x01 0x1b

        Example:
            add_device_override 1a2b3c 0x02 0x1a
        """
        params = args.split()
        addr = None
        cat = None
        subcat = None
        firmware = None
        error = None

        try:
            addr = Address(params[0])
            cat = binascii.unhexlify(params[1][2:])
            subcat = binascii.unhexlify(params[2][2:])
            firmware = binascii.unhexlify(params[3][2:])
        except IndexError:
            error = 'missing'
        except ValueError:
            error = 'value'

        if addr and cat and subcat:
            self.tools.add_device_override(addr, cat, subcat, firmware)
        else:
            if error == 'missing':
                _LOGGING.error('Device address, category and subcategory are '
                               'required.')
            else:
                _LOGGING.error('Check the vales for address, category and '
                               'subcategory.')
            self.do_help('add_device_override')

    def do_add_x10_device(self, args):
        """Add an X10 device to the IM.

        Usage:
            add_x10_device housecode unitcode type

        Arguments:
            housecode: Device housecode (A - P)
            unitcode: Device unitcode  (1 - 16)
            type: Device type

        Current device types are:
            - OnOff
            - Dimmable
            - Sensor

        Example:
            add_x10_device M 12 OnOff
        """
        params = args.split()
        housecode = None
        unitcode = None
        dev_type = None

        try:
            housecode = params[0]
            unitcode = int(params[1])
            if unitcode not in range(1, 17):
                raise ValueError
            dev_type = params[2]
        except IndexError:
            pass
        except ValueError:
            _LOGGING.error('X10 unit code must be an integer 1 - 16')
            unitcode = None

        if housecode and unitcode and dev_type:
            device = self.tools.add_x10_device(housecode, unitcode, dev_type)
            if not device:
                _LOGGING.error('Device not added. Please check the '
                               'information you provided.')
                self.do_help('add_x10_device')
        else:
            _LOGGING.error('Device housecode, unitcode and type are '
                           'required.')
            self.do_help('add_x10_device')

    def do_kpl_status(self, args):
        """Get the status of a KeypadLinc button.

        Usage:
            kpl_status address group
        """
        params = args.split()
        address = None
        group = None

        try:
            address = params[0]
            group = int(params[1])
        except IndexError:
            _LOGGING.error("Address and group are regquired")
            self.do_help('kpl_status')
        except TypeError:
            _LOGGING.error("Group must be an integer")
            self.do_help('kpl_status')

        if address and group:
            self.tools.kpl_status(address, group)

    def do_kpl_on(self, args):
        """Turn on a KeypadLinc button.

        Usage:
            kpl_on address group
        """
        params = args.split()
        address = None
        group = None

        try:
            address = params[0]
            group = int(params[1])
        except IndexError:
            _LOGGING.error("Address and group are regquired")
            self.do_help('kpl_status')
        except TypeError:
            _LOGGING.error("Group must be an integer")
            self.do_help('kpl_status')

        if address and group:
            self.tools.kpl_on(address, group)

    def do_kpl_off(self, args):
        """Turn off a KeypadLinc button.

        Usage:
            kpl_on address group
        """
        params = args.split()
        address = None
        group = None

        try:
            address = params[0]
            group = int(params[1])
        except IndexError:
            _LOGGING.error("Address and group are regquired")
            self.do_help('kpl_status')
        except TypeError:
            _LOGGING.error("Group must be an integer")
            self.do_help('kpl_status')

        if address and group:
            self.tools.kpl_off(address, group)

    def do_kpl_set_on_mask(self, args):
        """Set the on mask for a KeypadLinc button.

        Usage:
            kpl_set_on_mask address group mask
        """
        params = args.split()
        address = None
        group = None
        mask_string = None
        mask = None

        try:
            address = params[0]
            group = int(params[1])
            mask_string = params[2]
            if mask_string[0:2].lower() == '0x':
                mask = binascii.unhexlify(mask_string[2:])
            else:
                mask = int(mask_string)
        except IndexError:
            _LOGGING.error("Address, group and mask are regquired")
            self.do_help('kpl_status')
        except TypeError:
            _LOGGING.error("Group must be an integer")
            self.do_help('kpl_status')

        if address and group and mask:
            self.tools.kpl_set_on_mask(address, group, mask)

    # pylint: disable=unused-argument
    def do_poll_devices(self, args):
        """Poll all devices for current status.

        Usage:
            poll_devices
        """
        self.tools.plm.poll_devices()


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
    parser.add_argument('-l', '--logfile', default='',
                        help='Log file name')
    parser.add_argument('--workdir', default='',
                        help='Working directory for reading and saving '
                        'device information.')

    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    monTool = Tools(loop, args)
    asyncio.ensure_future(monTool.monitor_mode())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        if monTool.plm:
            if monTool.plm.transport:
                _LOGGING.info('Closing the session')
                asyncio.ensure_future(monTool.plm.transport.close(), loop=loop)
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


def interactive():
    """Create an interactive command line tool.

    Wrapper for an interactive session for manual commands to be entered.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='/dev/ttyUSB0',
                        help='Path to PLM device')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Set logging level to verbose')
    parser.add_argument('-l', '--logfile', default='',
                        help='Log file name')
    parser.add_argument('--workdir', default='',
                        help='Working directory for reading and saving '
                        'device information.')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    cmd = Commander(loop, args)
    cmd.start()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        if cmd.tools.plm:
            if cmd.tools.plm.transport:
                # _LOGGING.info('Closing the session')
                cmd.tools.plm.transport.close()
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
