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

    def lookup(self, code, fullmessage = None):
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

PP.add(b'\x50', name = 'INSTEON Standard Message Received', size = 11)
PP.add(b'\x51', name = 'INSTEON Extended Message Received', size = 25)
PP.add(b'\x52', name = 'X10 Message Received', size = 4)
PP.add(b'\x53', name = 'ALL-Linking Completed', size = 10)
PP.add(b'\x54', name = 'Button Event Report', size = 3)
PP.add(b'\x55', name = 'User Reset Detected', size = 2)
PP.add(b'\x56', name = 'ALL-Link CLeanup Failure Report', size = 2)
PP.add(b'\x57', name = 'ALL-Link Record Response', size = 10)
PP.add(b'\x58', name = 'ALL-Link Cleanup Status Report', size = 3)

PP.add(b'\x60', name = 'Get IM Info', size = 2, rsize = 9)
PP.add(b'\x61', name = 'Send ALL-Link Command', size = 5, rsize = 6)
PP.add(b'\x62', name = 'INSTEON Fragmented Message', size = 8, rsize = 9)
PP.add(b'\x69', name = 'Get First ALL-Link Record', size = 2)
PP.add(b'\x6a', name = 'Get Next ALL-Link Record', size = 2)
PP.add(b'\x73', name = 'Get IM Configuration', size = 2, rsize = 6)

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
        self._dump_in_progress = False


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

    def _rsize(self,message):
        code = bytes([message[1]])
        ppc = PP.lookup(code, fullmessage = message)

        if hasattr(ppc, 'rsize') and ppc.rsize:
            self.log.debug('Found a code %s message which returns %d bytes', binascii.hexlify(code), ppc.rsize)
            return ppc.rsize
        else:
            self.log.debug('Unable to find an rsize for code %s', binascii.hexlify(code))
            return len(message) + 1

        return retval


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

            if buffer[0] != 2:
                buffer = buffer[1:]
                self.log.debug('Buffer does not start at a command, trimming leading garbage')

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

            for sm in self._sent_messages:
                rsize = self._rsize(sm)
                self.log.debug('Looking for ACK/NAK on sent message: %s expecting rsize of %d', binascii.hexlify(sm), rsize)
                if buffer.find(sm) == 0:
                    if len(buffer) < rsize:
                        self.log.debug('Still waiting for all of message to arrive, %d/%d', len(buffer), rsize)
                        return ([], buffer)

                    code = bytes([buffer[1]])
                    message_length = len(sm)
                    response_length = rsize - message_length
                    response = buffer[message_length:response_length]
                    acknak = buffer[-1]

                    mla = buffer[:rsize]
                    buffer = buffer[rsize:]

                    self.log.debug('sm found response: %s', binascii.hexlify(response))
                    self.log.debug('ackbak is %d', acknak)

                    if acknak == 6:
                        self.log.debug('Sent command %s was successful!', binascii.hexlify(sm))
                        self.log.debug('Appending receipt %s', binascii.hexlify(mla))
                        message_list.append(mla)
                    else:
                        if code == b'\x6a':
                            self.log.info('ALL-Link database dump is complete')
                            self._dump_in_progress = False
                        else:
                            self.log.warn('Sent command %s was NOT successful!', binascii.hexlify(sm))

                    self._sent_messages.remove(sm)

            if len(buffer) == 0:
                self.log.debug('Clean break!  There is no buffer left')
                worktodo = False
                break

            code = bytes([buffer[1]])
            self.log.debug('Code is %s', binascii.hexlify(code))

            for c in PP.codelist:
                if code == c:
                    ppc = PP.lookup(code, fullmessage = buffer)

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


        return (message_list,buffer)

    def _process_message(self,message):
        self.log.debug('Processing message: %s', binascii.hexlify(message))
        if message[0] != 2 or len(message) < 2:
            self.log.warn('process_message called with a malformed message')
            return

        code = bytes([message[1]])
        self.log.debug('Code is %s', binascii.hexlify(code))
        ppc = PP.lookup(code, fullmessage = message)

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
                self.log.info('Unhandled event: %s (%s)', ppc.name, binascii.hexlify(message))
            else:
                self.log.info('Unrecognized event: UNKNOWN (%s)', binascii.hexlify(message))

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

        self.log.info('INSTEON standard message from %s to %s: cmd1:%s cmd2:%s flags:%s',
                      self._insteon_addr(from_addr), self._insteon_addr(to_addr),
                      hex(cmd1), hex(cmd2), hex(flags))

    def _parse_insteon_extended(self,message):
        code = bytes([message[1]])
        imessage = message[2:]
        from_addr = imessage[0:3]
        to_addr = imessage[3:6]
        flags = imessage[6]
        cmd1 = imessage[7]
        cmd2 = imessage[8]
        userdata = imessage[9:]

        self.log.info('INSTEON extended message from %s to %s: cmd1:%s cmd2:%s flags:%s userdata:%s',
                      self._insteon_addr(from_addr), self._insteon_addr(to_addr),
                      hex(cmd1), hex(cmd2), hex(flags),
                      binascii.hexlify(userdata))


    def _parse_button_event(self, message):
        event = message[2]
        self.log.info('Button event: %s', hex(event))

    def _parse_get_plm_info(self, message):
        plm_addr = message[2:5]
        category = message[5]
        subcategory = message[6]
        firmware = message[7]
        self.log.info('PLM Info from %s: category:%s subcategory:%s firmware:%s',
                      self._insteon_addr(plm_addr),
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
        device_addr = message[4:7]
        linkdata1 = message[7]
        linkdata2 = message[8]
        linkdata3 = message[9]
        self.log.info('ALL-Link Record for %s: flags:%s group:%s data:%s/%s/%s',
                      self._insteon_addr(device_addr),
                      hex(flags), hex(group),
                      hex(linkdata1), hex(linkdata2), hex(linkdata3))

        if self._dump_in_progress is True:
            self.get_next_all_link_record()

    def _parse_all_link_completed(self, message):
        linkcode = message[2]
        group = message[3]
        device_addr = message[4:7]
        category = message[7]
        subcategory = message[8]
        firmware = message[9]
        self.log.info('ALL-Link Completed for %s: group:%s category:%s sub:%s firmware:%s',
                      self._insteon_addr(device_addr), hex(group),
                      hex(category), hex(subcategory), hex(firmware))


    def _send_raw(self, message):
        self.log.info('Sending %d byte message: %s', len(message), binascii.hexlify(message))
        self.transport.write(message)
        self._sent_messages.append(message)

    def get_plm_info(self):
        self.log.info('Requesting PLM Info')
        self._send_raw(binascii.unhexlify('0260'))

    def get_plm_config(self):
        self.log.info('Requesting PLM Config')
        self._send_raw(binascii.unhexlify('0273'))

    def get_first_all_link_record(self):
        self.log.info('Requesting First ALL-Link Record')
        self._send_raw(binascii.unhexlify('0269'))

    def get_next_all_link_record(self):
        self.log.info('Requesting Next ALL-Link Record')
        self._send_raw(binascii.unhexlify('026a'))

    def dump_all_link_database(self):
        self._dump_in_progress = True
        self.get_first_all_link_record()

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
