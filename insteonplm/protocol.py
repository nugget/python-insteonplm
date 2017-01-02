"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import time
import binascii

# 40.95.e6 is my computer room wall switch

__all__ = ('PLM')

# 62 needs definition

STATIC_COMMAND_LENGTHS = {
    b'\x50': 11,
    b'\x51': 25,
    b'\x52': 4,
    b'\x53': 10,
    b'\x54': 3,
    b'\x55': 2,
    b'\x56': 7,
    b'\x57': 10,
    b'\x58': 3
    }

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
        self.buffer = bytearray()

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

        self.buffer.extend(data)

        message_list, self.buffer = self._strip_messages_off_front_of_buffer(self.buffer)

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

                for c in STATIC_COMMAND_LENGTHS:
                    if code == c:
                        message_length = STATIC_COMMAND_LENGTHS[code]
                        self.log.debug('Found a code %s message which is %d bytes', binascii.hexlify(code), message_length)

                        if len(buffer) < message_length:
                            self.log.debug('I have not received the full message yet')
                            worktodo = False
                            break
                        else:
                            new_message = buffer[0:message_length]
                            self.log.debug('new message is: %s', binascii.hexlify(new_message))
                            message_list.append(new_message)
                            buffer = buffer[message_length:]


        return (message_list,buffer)

    def _process_message(self,message):
        self.log.info('Processing message: %s', binascii.hexlify(message))


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
