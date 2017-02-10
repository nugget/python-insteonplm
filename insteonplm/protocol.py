"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import binascii
import collections

# 40.95.e6 is my computer room wall switch

__all__ = ('PLM', 'PLMCode', 'PLMProtocol', 'Address')


class Address(bytearray):
    """Datatype definition for INSTEON device address handling."""

    def __init__(self, addr):
        """Create an Address object."""
        self.log = logging.getLogger(__name__)
        self.addr = self.normalize(addr)

    def normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        if isinstance(addr, Address):
            return addr.hex
        if isinstance(addr, bytearray):
            addr = bytes(addr)
        if isinstance(addr, bytes):
            return binascii.hexlify(addr).decode()
        if isinstance(addr, str):
            addr.replace('.', '')
            addr = addr[0:6]
            return addr.lower()
        else:
            self.log.warn('Address class initialized with unknown type %s', type(addr))
            return 'aabbcc'

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        addrstr = self.addr[0:2]+'.'+self.addr[2:4]+'.'+self.addr[4:6]
        return addrstr.upper()

    @property
    def hex(self):
        """Emit the address in bare hex format (aabbcc)."""
        return self.addr

    @property
    def bytes(self):
        r"""Emit the address in bytes format (b'\xaabbcc')."""
        return binascii.hexlify(self.addr)


class PLMCode(object):
    """Class to store PLM code definitions and attributes."""

    def __init__(self, code, name=None, size=None, rsize=None):
        """Create a new PLM code object."""
        self.code = code
        self.size = size
        self.rsize = rsize
        self.name = name


class PLMProtocol(object):
    """Class container to store PLMCode objects as a Protocol."""

    def __init__(self, version=1):
        """Create the Protocol object."""
        self._codelist = []

    def __len__(self):
        """Return the number of PLMCodes in the Protocol."""
        return len(self._codelist)

    def __dir__(self):
        """Return the full list of PLMCodes."""
        clist = []
        for x in self._codelist:
            clist.append(x.code)
        return clist

    def add(self, code, name=None, size=None, rsize=None):
        """Add a new PLMCode to the Protocol."""
        self._codelist.append(PLMCode(code, name=name, size=size, rsize=rsize))

    def lookup(self, code, fullmessage=None):
        """Return the PLMCode from a byte and optional stream buffer."""
        for x in self._codelist:
            if x.code == code:
                if code == b'\x62' and fullmessage:
                    x.name = 'INSTEON Fragmented Message'
                    x.size = 8
                    x.rsize = 9
                    if len(fullmessage) >= 6:
                        flags = bytes([fullmessage[5]])
                        if flags == b'\x00':
                            x.name = 'INSTEON Standard Message'
                        else:
                            x.name = 'INSTEON Extended Message'
                            x.size = 22
                            x.rsize = 23

                return x

PP = PLMProtocol()

PP.add(b'\x50', name='INSTEON Standard Message Received', size=11)
PP.add(b'\x51', name='INSTEON Extended Message Received', size=25)
PP.add(b'\x52', name='X10 Message Received', size=4)
PP.add(b'\x53', name='ALL-Linking Completed', size=10)
PP.add(b'\x54', name='Button Event Report', size=3)
PP.add(b'\x55', name='User Reset Detected', size=2)
PP.add(b'\x56', name='ALL-Link CLeanup Failure Report', size=2)
PP.add(b'\x57', name='ALL-Link Record Response', size=10)
PP.add(b'\x58', name='ALL-Link Cleanup Status Report', size=3)

PP.add(b'\x60', name='Get IM Info', size=2, rsize=9)
PP.add(b'\x61', name='Send ALL-Link Command', size=5, rsize=6)
PP.add(b'\x62', name='INSTEON Fragmented Message', size=8, rsize=9)
PP.add(b'\x69', name='Get First ALL-Link Record', size=2)
PP.add(b'\x6a', name='Get Next ALL-Link Record', size=2)
PP.add(b'\x73', name='Get IM Configuration', size=2, rsize=6)

Device = collections.namedtuple('Device', ['cat', 'subcat', 'firmware', 'onlevel'])


class ALDB:
    def __init__(self):
        self._devices = {}
        self._cb_new_device = []
        self._cb_status = []
        self.state = 'empty'
        self.log = logging.getLogger(__name__)

    def __len__(self):
        return len(self._devices)

    def __dir__(self):
        return self._devices.keys()

    def __getitem__(self, address):
        if address in self._devices:
            return self._devices[address]
        raise KeyError

    def __setitem__(self, key, value):
        if key in self._devices:
            if 'firmware' in value and value['firmware'] < 255:
                self._devices[key] = value

        else:
            self._devices[key] = value
            for cb, criteria in self._cb_new_device:
                self.log.warning('I should callback to %s if %s', cb, criteria)
                cb(address=key, name=key)

    def new_device_callback(self, callback, criteria):
        self.log.warn('New callback %s with %s', callback, criteria)
        self._cb_new_device.append([callback, criteria])

    def status_update_callback(self, callback, criteria):
        self.log.warn('Status callback %s', callback, criteria)
        self._cb_status.append([callback, criteria])

    def setattr(self, key, attr, value):
        if key in self._devices:
            oldvalue = None
            if attr in self._devices[key]:
                oldvalue = self._devices[key][attr]
            self._devices[key][attr] = value
            if value != oldvalue:
                self.log.info('Device %s.%s changed: %s->%s"',
                              key, attr, oldvalue, value)
                return True
            else:
                return False
        else:
            raise KeyError


# In Python 3.4.4, `async` was renamed to `ensure_future`.
try:
    ensure_future = asyncio.ensure_future
except AttributeError:
    ensure_future = asyncio.async


# pylint: disable=too-many-instance-attributes, too-many-public-methods
class PLM(asyncio.Protocol):
    """The Insteon PLM IP control protocol handler."""

    def __init__(self, update_callback=None, loop=None, connection_lost_callback=None):
        """Protocol handler that handles all status and changes on PLM.

        This class is expected to be wrapped inside a Connection class object
        which will maintain the socket and handle auto-reconnects.

            :param update_callback:
                called if any state information changes in device (optional)
            :param connection_lost_callback:
                called when connection is lost to device (optional)
            :param loop:
                asyncio event loop (optional)

            :type update_callback:
                callable
            :type: connection_lost_callback:
                callable
            :type loop:
                asyncio.loop
        """
        self._loop = loop

        self._connection_lost_callback = connection_lost_callback
        self._update_callback = [[update_callback,{}]]

        self._buffer = bytearray()
        self._last_command = None
        self._wait_for = {}
        self._recv_queue = []
        self._send_queue = []

        self.devices = ALDB()

        self.log = logging.getLogger(__name__)
        self.transport = None

    #
    # asyncio network functions
    #

    def connection_made(self, transport):
        """Called when asyncio.Protocol establishes the network connection."""
        self.log.info('Connection established to PLM')
        self.transport = transport

        self.transport.set_write_buffer_limits(128)
        limit = self.transport.get_write_buffer_size()
        self.log.debug('Write buffer size is %d', limit)
        self.load_all_link_database()

    def data_received(self, data):
        """Called when asyncio.Protocol detects received data from network."""
        self.log.debug('Received %d bytes from PLM: %s',
                       len(data), binascii.hexlify(data))

        self._buffer.extend(data)
        self._strip_messages_off_front_of_buffer()

        for message in self._recv_queue:
            self._process_message(message)
            self._recv_queue.remove(message)

    def connection_lost(self, exc):
        """Called when asyncio.Protocol loses the network connection."""
        if exc is None:
            self.log.warning('eof from modem?')
        else:
            self.log.warning('Lost connection to modem: %s', exc)

        self.transport = None

        if self._connection_lost_callback:
            self._connection_lost_callback()

    def _rsize(self, message):
        code = bytes([message[1]])
        ppc = PP.lookup(code, fullmessage=message)

        if hasattr(ppc, 'rsize') and ppc.rsize:
            self.log.debug('Found a code %s message which returns %d bytes',
                           binascii.hexlify(code), ppc.rsize)
            return ppc.rsize
        else:
            self.log.debug('Unable to find an rsize for code %s',
                           binascii.hexlify(code))
            return len(message) + 1

    def _timeout_reached(self):
        self.log.debug('timeout_reached invoked')
        self._clear_wait()
        self._process_queue()

    def _clear_wait(self):
        self.log.debug('clear_wait invoked')
        if 'thandle' in self._wait_for:
            self.log.debug('Cancelling wait_for timeout callback')
            self._wait_for['thandle'].cancel()
        self._wait_for = {}

    def _schedule_wait(self, keys, timeout=2):
        self.log.debug('setting wait_for to %s timeout %d', keys, timeout)
        if self._wait_for != {}:
            self.log.warn('Overwriting stale wait_for: %s', self._wait_for)
            self._clear_wait()

        if timeout > 0:
            self.log.debug('Set timeout on wait_for at %d seconds', timeout)
            keys['thandle'] = self._loop.call_later(timeout,
                                                    self._timeout_reached)

        self._wait_for = keys

    def _wait_for_last_command(self):
        sm = self._last_command
        rsize = self._rsize(sm)
        self.log.debug('Wait for ACK/NAK on sent: %s expecting rsize of %d',
                       binascii.hexlify(sm), rsize)
        if self._buffer.find(sm) == 0:
            if len(self._buffer) < rsize:
                self.log.debug('Waiting for all of message to arrive, %d/%d',
                               len(self._buffer), rsize)
                return

            code = bytes([self._buffer[1]])
            message_length = len(sm)
            response_length = rsize - message_length
            response = self._buffer[message_length:response_length]
            acknak = self._buffer[rsize-1]

            mla = self._buffer[:rsize]
            buffer = self._buffer[rsize:]

            if acknak == 6:
                if len(response) > 0:
                    self.log.debug('Sent command %s OK with response %s',
                                   binascii.hexlify(sm), response)
                    self._recv_queue.append(mla)
                else:
                    self.log.debug('Sent command %s OK', binascii.hexlify(sm))
            else:
                if code == b'\x6a':
                    self.log.info('ALL-Link database dump is complete')
                    self.devices.state = 'loaded'
                    for da in dir(self.devices):
                        d = self.devices[da]
                        if 'cat' in d and d['cat'] > 0:
                            self.log.debug('I know the category for %s (%s)',
                                           da, hex(d['cat']))
                        else:
                            self.product_data_request(da)
                    self.poll_devices()
                else:
                    self.log.warn('Sent command %s UNsuccessful! (acknak %d)',
                                  binascii.hexlify(sm), acknak)
            self._last_command = None
            self._buffer = buffer

    def _wait_for_recognized_message(self):
        code = bytes([self._buffer[1]])
        self.log.debug('Code is %s', binascii.hexlify(code))

        for c in dir(PP):
            if code == c:
                ppc = PP.lookup(code, fullmessage=self._buffer)

                self.log.debug('Found a code %s message which is %d bytes',
                               binascii.hexlify(code), ppc.size)

                if len(self._buffer) == ppc.size:
                    new_message = self._buffer[0:ppc.size]
                    self.log.debug('new message is: %s',
                                   binascii.hexlify(new_message))
                    self._recv_queue.append(new_message)
                    self._buffer = self._buffer[ppc.size:]
                else:
                    self.log.debug('Need more bytes to process message.')

    def _strip_messages_off_front_of_buffer(self):
        lastlooplen = 0
        worktodo = True

        while worktodo:
            if len(self._buffer) == 0:
                self.log.debug('Clean break!  There is no buffer left')
                worktodo = False
                break

            if len(self._buffer) < 2:
                worktodo = False
                break

            if self._buffer[0] != 2:
                self._buffer = self._buffer[1:]
                self.log.debug('Trimming leading buffer garbage')

            if len(self._buffer) == lastlooplen:
                # Buffer size did not change so we should wait for more data
                worktodo = False
                break

            lastlooplen = len(self._buffer)

            if self._buffer.find(2) < 0:
                self.log.debug('Buffer does not contain a 2, we should bail')
                worktodo = False
                break

            if self._last_command:
                self._wait_for_last_command()
            else:
                self._wait_for_recognized_message()

        self._process_queue()

    def _process_queue(self):
        self.log.debug('processing queue with %d items', len(self._send_queue))
        if self._clear_to_send() is True:
            self.log.debug('Clear to send next command in send_queue')
            command, wait_for = self._send_queue[0]
            self._send_hex(command, wait_for=wait_for)
            self._send_queue.remove([command, wait_for])

    def _clear_to_send(self):
        if len(self._buffer) == 0:
            if len(self._send_queue) > 0:
                if self._last_command is None:
                    if self._wait_for == {}:
                        return True

    def _process_message(self, message):
        self.log.debug('Processing message: %s', binascii.hexlify(message))
        if message[0] != 2 or len(message) < 2:
            self.log.warn('process_message called with a malformed message')
            return

        code = bytes([message[1]])
        self.log.debug('Code is %s', binascii.hexlify(code))
        ppc = PP.lookup(code, fullmessage=message)

        if code == b'\x50':
            self._parse_insteon_standard(message)
        elif code == b'\x51':
            self._parse_insteon_extended(message)
        elif code == b'\x53':
            self._parse_all_link_completed(message)
        elif code == b'\x54':
            self._parse_button_event(message)
        elif code == b'\x57':
            self._parse_all_link_record(message)
        elif code == b'\x60':
            self._parse_get_plm_info(message)
        elif code == b'\x73':
            self._parse_get_plm_config(message)
        else:
            if hasattr(ppc, 'name') and ppc.name:
                self.log.info('Unhandled event: %s (%s)', ppc.name,
                              binascii.hexlify(message))
            else:
                self.log.info('Unrecognized event: UNKNOWN (%s)',
                              binascii.hexlify(message))

        self._eval_wait_for(message)
        self._process_queue()

    def _eval_wait_for(self, message):
        match = True

        code = bytes([message[1]])
        if 'code' in self._wait_for:
            if self._wait_for['code'] != code:
                self.log.debug('code is not a match')
                match = False
        else:
            self.log.debug('there is no code to find')

        if code == b'\x50' or code == b'\x51':
            cmd1 = bytes([message[9]])
            cmd2 = bytes([message[10]])
        else:
            cmd1 = None
            cmd2 = None

        if 'cmd1' in self._wait_for:
            if self._wait_for['cmd1'] != cmd1:
                self.log.debug('cmd1 is not a match')
                match = False

        if 'cmd2' in self._wait_for:
            if self._wait_for['cmd2'] != cmd2:
                self.log.debug('cmd2 is not a match')
                match = False

        if match is True:
            self.log.debug('I found what I was waiting for')
            if 'callback' in self._wait_for:
                self._wait_for['callback'](message)
            self._clear_wait()

    def _parse_insteon_standard(self, message):
        imessage = message[2:11]
        from_addr = Address(imessage[0:3])
        to_addr = Address(imessage[3:6])
        flags = imessage[6]
        cmd1 = imessage[7]
        cmd2 = imessage[8]

        self.log.info('INSTEON standard message from %s to %s: cmd1:%s cmd2:%s flags:%s',
                      from_addr.human, to_addr.human,
                      hex(cmd1), hex(cmd2), hex(flags))

        if cmd1 == 0x13:
            if self.devices.setattr(from_addr.hex, 'onlevel', 0):
                self._do_update_callback(message)
        elif cmd1 == 0x11:
            if self.devices.setattr(from_addr.hex, 'onlevel', 255):
                self._do_update_callback(message)

    def _parse_insteon_extended(self, message):
        imessage = message[2:]
        from_addr = Address(imessage[0:3])
        to_addr = Address(imessage[3:6])
        flags = imessage[6]
        cmd1 = imessage[7]
        cmd2 = imessage[8]
        userdata = imessage[9:]

        self.log.info('INSTEON extended %s->%s: cmd1:%s cmd2:%s flags:%s data:%s',
                      from_addr.human, to_addr.human,
                      hex(cmd1), hex(cmd2), hex(flags),
                      binascii.hexlify(userdata))

        if cmd1 == 3 and cmd2 == 0:
            self._parse_product_data_response(from_addr, userdata)

    def _parse_status_response(self, message):
        imessage = message[2:]
        from_addr = Address(imessage[0:3])
        onlevel = imessage[8]
        self.log.info('INSTEON Dimmer %s is at level %s',
                      from_addr.human, hex(onlevel))
        self.devices.setattr(from_addr.hex, 'onlevel', onlevel)
        self._do_update_callback(message)

    def _do_update_callback(self, message):
        for cb, criteria in self._update_callback:
            self.log.info('update callback %s with criteria %s', cb, criteria)
            self._loop.call_soon(cb, message)

    def _parse_product_data_response(self, from_addr, message):
        from_addr = Address(from_addr)
        category = message[4]
        subcategory = message[5]
        firmware = message[6]
        self.log.info('INSTEON Product Data Response from %s: cat:%s, subcat:%s',
                      from_addr.human, hex(category), hex(subcategory))

        self.devices[from_addr.hex] = dict(cat=category, subcat=subcategory, firmware=firmware)

    def _parse_button_event(self, message):
        event = message[2]
        self.log.info('Button event: %s', hex(event))

    def _parse_get_plm_info(self, message):
        plm_addr = Address(message[2:5])
        category = message[5]
        subcategory = message[6]
        firmware = message[7]
        self.log.info('PLM Info from %s: category:%s subcat:%s firmware:%s',
                      plm_addr.human,
                      hex(category), hex(subcategory), hex(firmware))

    def _parse_get_plm_config(self, message):
        flags = message[2]
        spare1 = message[3]
        spare2 = message[4]
        self.log.info('PLM Config: flags:%s spare:%s spare:%s',
                      hex(flags), hex(spare1), hex(spare2))

    def _parse_all_link_record(self, message):
        flags = message[2]
        group = message[3]
        device_addr = Address(message[4:7])
        linkdata1 = message[7]
        linkdata2 = message[8]
        linkdata3 = message[9]
        self.log.info('ALL-Link Record for %s: flags:%s group:%s data:%s/%s/%s',
                      device_addr.human,
                      hex(flags), hex(group),
                      hex(linkdata1), hex(linkdata2), hex(linkdata3))

        self.devices[device_addr.hex] = dict(cat=linkdata1, subcat=linkdata2, firmware=linkdata3)

        if self.devices.state == 'loading':
            self.get_next_all_link_record()

    def _parse_all_link_completed(self, message):
        linkcode = message[2]
        group = message[3]
        device_addr = Address(message[4:7])
        category = message[7]
        subcategory = message[8]
        firmware = message[9]
        self.log.info('ALL-Link Completed for %s: group:%s cat:%s subcat:%s firmware:%s linkcode:%s',
                      device_addr.human, hex(group),
                      hex(category), hex(subcategory), hex(firmware),
                      hex(linkcode))

    def _queue_hex(self, message, wait_for={}):
        self.log.debug('Adding command to queue: %s', message)
        self._send_queue.append([message, wait_for])

    def _send_hex(self, message, wait_for={}):
        if self._last_command:
            self.log.debug('Still waiting on last_command.')
            self._queue_hex(message, wait_for)
        else:
            self._send_raw(binascii.unhexlify(message))
            self._schedule_wait(wait_for)

    def _send_raw(self, message):
        self.log.debug('Sending %d byte message: %s', len(message), binascii.hexlify(message))
        self.transport.write(message)
        self._last_command = message

    def send_insteon_standard(self, device, cmd1, cmd2, wait_for={}):
        """Send an INSTEON Standard message to the PLM."""
        device = Address(device)
        rawstr = '0262'+device.hex+'00'+cmd1+cmd2
        self._send_hex(rawstr, wait_for)

    def send_insteon_extended(self, device, cmd1, cmd2, wait_for={}):
        """Send an INSTEON Extended message to the PLM."""
        device = Address(device)
        rawstr = '0262'+device.hex+'00'+cmd1+cmd2
        self._send_hex(rawstr, wait_for)

    def get_plm_info(self):
        """Request PLM Info."""
        self.log.info('Requesting PLM Info')
        self._send_hex('0260')

    def get_plm_config(self):
        """Request PLM Config."""
        self.log.info('Requesting PLM Config')
        self._send_hex('0273')

    def get_first_all_link_record(self):
        """Request first ALL-Link record."""
        self.log.info('Requesting First ALL-Link Record')
        self._send_hex('0269', wait_for={'code': b'\x57'})

    def get_next_all_link_record(self):
        """Request next ALL-Link record."""
        self.log.info('Requesting Next ALL-Link Record')
        self._send_hex('026a', wait_for={'code': b'\x57'})

    def load_all_link_database(self):
        """Load the ALL-Link Database into object."""
        self.devices.state = 'loading'
        self.get_first_all_link_record()

    def product_data_request(self, addr):
        """Request Product Data Record for device."""
        device = Address(addr)
        self.log.info('Requesting product data for %s', device.human)
        self.send_insteon_standard(
            device, '03', '00',
            wait_for={'code': b'\x51', 'cmd1': b'\x03', 'cmd2': b'\x00'})

    def text_string_request(self, addr):
        """Request Device Text String."""
        device = Address(addr)
        self.log.info('Requesting text string for %s', device.human)
        self.send_insteon_standard(
            device, '03', '02',
            wait_for={'code': b'\x51', 'cmd1': b'\x03', 'cmd2': b'\x02'})

    def status_request(self, addr):
        """Request Device Status."""
        device = Address(addr)
        self.log.info('Requesting status for %s', device.human)
        self.send_insteon_standard(
            device, '19', '00',
            wait_for={'code': b'\x50', 'callback': self._parse_status_response})

    def new_device_callback(self, callback, criteria):
        self.devices.new_device_callback(callback, criteria)

    def update_callback(self, callback, criteria):
        self._update_callback.append([callback, criteria])

    def get_device_attr(self, addr, attr):
        address = Address(addr)
        device = self.devices[address.hex]
        if attr in device:
            return device[attr]

    def turn_off(self, addr):
        device = Address(addr)
        self.send_insteon_standard(device,'13','00')

    def turn_on(self, addr, brightness=255):
        device = Address(addr)
        self.send_insteon_standard(device,'11','ff')

    def poll_devices(self):
        for d in dir(self.devices):
            self.status_request(d)

    def list_devices(self):
        for d in dir(self.devices):
            dev = self.devices[d]
            print(d,':',dev)
