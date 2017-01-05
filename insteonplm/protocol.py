"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import time
import binascii

# 40.95.e6 is my computer room wall switch

__all__ = ('PLM', 'PLMCode', 'PLMProtocol')

class PLMCode(object):
    def __init__(self, code, name = None, size = None, rsize = None):
        self.code = code
        self.size = size
        self.rsize = rsize
        self.name = name

class PLMProtocol(object):
    def __init__(self, version = 1):
        self._codelist = []

    def add(self, code, name = None, size = None, rsize = None):
        self._codelist.append(PLMCode(code,name = name, size = size, rsize = rsize))

    @property
    def len(self):
        return len(self._codelist)

    @property
    def codelist(self):
        clist = []
        for x in self._codelist:
            clist.append(x.code)
        return clist

    def lookup(self, code):
        for x in self._codelist:
            if x.code == code:
                return x

    def response_bytes(self, code):
        rsize = 0
        for x in self._codelist:
            if x.code == code:
                if isinstance(x.rsize, int):
                    rsize = x.rsize
        return rsize

PP = PLMProtocol()

PP.add(b'\x50', name = 'INSTEON Standard Message Received', size = 11)
PP.add(b'\x51', name = 'INSTEON Extended Message Received', size = 25)
PP.add(b'\x52', name = 'X10 Message Received', size = 4)
PP.add(b'\x53', name = 'ALL-Linking Completed', size = 10)
PP.add(b'\x54', name = 'Button Event Report', size = 3)
PP.add(b'\x55', name = 'User Reset Detected', size = 2)
PP.add(b'\x56', name = 'ALL-Link CLeanup Failure Report', size = 2)
PP.add(b'\x57', name = 'ALL-Link Record Response', size = 10)
PP.add(b'\x58', name = 'ALL-Link Cleanup Status Report', size = 3)

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
        self.log = logging.getLogger(__name__)
        self._connection_lost_callback = connection_lost_callback
        self._update_callback = update_callback
        self._input_names = {}
        self._input_numbers = {}
        self.transport = None
        self._buffer = bytearray()
        self._sent_messages = []


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

    def data_received(self, data):
        """Called when asyncio.Protocol detects received data from network."""
        self.log.debug('Received %d bytes from PLM: %s',len(data), binascii.hexlify(data))

        self._buffer.extend(data)

        message_list, self._buffer = self._strip_messages_off_front_of_buffer(self._buffer)

        for message in message_list:
            self._process_message(message)

    def connection_lost(self, exc):
        """Called when asyncio.Protocol loses the network connection."""
        if exc is None:
            self.log.warning('eof from modem?')
        else:
            self.log.warning('Lost connection to modem: %s', exc)

        self.transport = None

        if self._connection_lost_callback:
            self._connection_lost_callback()

    def _strip_messages_off_front_of_buffer(self,buffer):
        message_list = []

        if len(buffer) < 2:
            return(message_list,buffer)

        lastlooplen = 0
        worktodo = True

        while worktodo:
            if len(buffer) == 0:
                self.log.debug('Clean break!  There is no buffer left')
                worktodo = False
                break

            first = bytes([buffer[0]])
            self.log.debug('-- ')
            self.log.debug('First byte is %s', binascii.hexlify(first))
            self.log.debug('Buffer is %d bytes: %s',len(buffer), binascii.hexlify(buffer))

            if len(buffer) == lastlooplen:
                self.log.warn('Buffer size unchanged after loop, That means that something went wrong')
                worktodo = False
                break

            lastlooplen = len(buffer)

            if buffer.find(2) < 0:
                self.log.debug('Buffer does not contain a 2, we should bail')
                break

            if buffer[0] != 2:
                buffer = buffer[1:]
                self.log.debug('Buffer does not start at a command, trimming leading garbage')
            else:
                code = bytes([buffer[1]])
                self.log.debug('Code is %s', binascii.hexlify(code))

                for c in PP.codelist:
                    if code == c:
                        ppc = PP.lookup(code)

                        self.log.debug('Found a code %s message which is %d bytes', binascii.hexlify(code), ppc.size)

                        if len(buffer) == ppc.size:
                            new_message = buffer[0:ppc.size]
                            self.log.debug('new message is: %s', binascii.hexlify(new_message))
                            message_list.append(new_message)
                            buffer = buffer[ppc.size:]
                        else:
                            self.log.debug('I have not received enough data to process this message')
                            worktodo = False
                            break

            for sm in self._sent_messages:
                self.log.debug('Looking for ACK/NAK on sent message: %s', binascii.hexlify(sm))
                if buffer.find(sm) == 0 and len(buffer) > len(sm):
                    message_length = len(sm)
                    buffer = buffer[message_length:]

                    if buffer[0] == 6:
                        self.log.info('Sent command %s was successful!', binascii.hexlify(sm))
                    else:
                        self.log.warn('Sent command %s was NOT successful!', binascii.hexlify(sm))

                    buffer = buffer[1:]
                    self._sent_messages.remove(sm)

        return (message_list,buffer)

    def _process_message(self,message):
        self.log.debug('Processing message: %s', binascii.hexlify(message))
        if message[0] != 2 or len(message) < 2:
            self.log.warn('process_message called with a malformed message')
            return

        code = bytes([message[1]])
        self.log.debug('Code is %s', binascii.hexlify(code))
        ppc = PP.lookup(code)
        self.log.info(ppc.name)
        if code == b'\x50':
            self._parse_insteon_standard(message)

    def _insteon_addr(self, addr):
        hexaddr = str(binascii.hexlify(addr))[2:]
        addrstr = hexaddr[0:2]+'.'+hexaddr[2:4]+'.'+hexaddr[4:6]
        return addrstr.upper()

    def _parse_insteon_standard(self,message):
        code = bytes([message[1]])
        imessage = message[2:11]
        from_addr = imessage[0:3]
        to_addr = imessage[3:6]
        flags = imessage[6]
        cmd1 = imessage[7]
        cmd2 = imessage[8]

        self.log.info('INSTEON message from %s to %s: cmd1:%s cmd2:%s flags:%s',
                      self._insteon_addr(from_addr), self._insteon_addr(to_addr),
                      hex(cmd1), hex(cmd2), hex(flags))


    def _send_raw(self,message):
        self.log.info('Sending %d byte message: %s', len(message), binascii.hexlify(message))
        self.transport.write(message)
        self._sent_messages.append(message)

    @property
    def dump_rawdata(self):
        """Return contents of transport object for debugging forensics."""
        if hasattr(self, 'transport'):
            attrs = vars(self.transport)
            return ', '.join("%s: %s" % item for item in attrs.items())

    @property
    def test_string(self):
        """I really do."""
        return 'I like cows'
