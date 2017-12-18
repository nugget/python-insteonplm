"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import binascii
import time
from collections import deque

from .constants import *
from .aldb import ALDB
from .address import Address
from .messagecallback import MessageCallback 
from .messages.message import Message
from .messages.getIMInfo import GetImInfo
from .messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from .messages.getNextAllLinkRecord import GetNextAllLinkRecord 
from .messages.standardSend import StandardSend
from .messages.extendedSend import ExtendedSend 

__all__ = ('PLM')

#PP = PLMProtocol()

class PLM(asyncio.Protocol):
    """The Insteon PLM IP control protocol handler."""

    def __init__(self, loop=None, connection_lost_callback=None, userdefineddevices=()):
        """Protocol handler that handles all status and changes on PLM.

        This class is expected to be wrapped inside a Connection class object
        which will maintain the socket and handle auto-reconnects.

            :param connection_lost_callback:
                called when connection is lost to device (optional)
            :param loop:
                asyncio event loop (optional)

            :type: connection_lost_callback:
                callable
            :type loop:
                asyncio.loop
        """
        self._loop = loop

        self._connection_lost_callback = connection_lost_callback
        self._message_callbacks = MessageCallback()

        self._buffer = bytearray()
        self._recv_queue = deque([])
        self._send_queue = []
        self._wait_acknack_queue = []
        self._aldb_response_queue = {}
        self.devices = ALDB()

        self.address = None
        self.category = None
        self.subcategory = None
        self.firmware = None

        self.log = logging.getLogger(__name__)
        self.transport = None

        # TODO: Define a method for handling Insteon commands received via StandardMessageRecieved
        #       or ExtendedMessageReceived
        #       This will also define the device class' capabilities (i.e. device class can handle a
        #       COMMAND_LIGHT_ON request)
        #       It feels like a good idea to build this into the PLMProtocol class so that every 
        #       device (including the PLM) handle command registration the same way.

        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, 
                                                     None, self._handle_standard_or_extended_message_received)

        self._message_callbacks.add_message_callback(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, 
                                                     None, self._handle_standard_or_extended_message_received)

        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, 
                                                     COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE, self._handle_assign_to_all_link_group)

        self._message_callbacks.add_message_callback(MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57, 
                                                     None, self._handle_all_link_record_response)

        self._message_callbacks.add_message_callback(MESSAGE_GET_IM_INFO_0X60, 
                                                     None, self._handle_get_plm_info)

        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, 
                                                     None, self._handle_send_standard_or_extended_message_nak, MESSAGE_NAK)

        self._message_callbacks.add_message_callback(MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A, 
                                                     None, self._handle_get_next_all_link_record_nak, MESSAGE_NAK)

    def connection_made(self, transport):
        """Called when asyncio.Protocol establishes the network connection."""
        self.log.info('Connection established to PLM')
        self.transport = transport

        # self.transport.set_write_buffer_limits(128)
        # limit = self.transport.get_write_buffer_size()
        # self.log.debug('Write buffer size is %d', limit)
        self._get_plm_info()
        self._load_all_link_database()

    def data_received(self, data):
        self.log.debug("Starting: data_received")
        """Called when asyncio.Protocol detects received data from network."""
        self.log.debug('Received %d bytes from PLM: %s',
                       len(data), binascii.hexlify(data))

        self._buffer.extend(data)
        self._peel_messages_from_buffer()

        self.log.debug('Messages in queue: %d', len(self._recv_queue))
        worktodo = True
        while worktodo:
            try:
                msg = self._recv_queue.pop()
                callback = self._message_callbacks.get_callback_from_message(msg)
                if callback is not None:
                    self._loop.call_soon(callback, msg)
                else: 
                    self.log.debug("Did not find a message callback for code %x", msg.code)
            except:
                worktodo = False

        self.log.debug("Finishing: data_received")

    def connection_lost(self, exc):
        """Called when asyncio.Protocol loses the network connection."""
        if exc is None:
            self.log.warning('eof from modem?')
        else:
            self.log.warning('Lost connection to modem: %s', exc)

        self.transport = None

        if self._connection_lost_callback:
            self._connection_lost_callback()

    def add_device_callback(self, callback, criteria):
        """Register a callback for when a matching new device is seen."""
        self.log.debug("Starting: add_device_callback")
        self.devices.add_device_callback(callback, criteria)
        self.log.debug("Ending: add_device_callback")

    def send_msg(self, msg):
        # TODO: implement an ACK/NAK review of sent commands
        # Purpose of the function is to capture sent commands and compare them to ACK/NAK messages
        # A callback can then be defined in the event of a NAK (i.e. retry or do something else)
        # self._sent_queue.append(msg)
        self.log.debug("Starting: send_msg")
        self.log.debug('Sending %d byte message: %s',
                len(msg.bytes), msg.hex)
        time.sleep(.5)
        self.transport.write(msg.bytes)

        self.log.debug("Ending: send_msg")

    def send_standard(self, target, commandtuple, cmd2=None, flags=0x00, acknak=None):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError
        if cmd2out is None:
           if cmd2 is not None:
               cmd2out = cmd2
           else:
                raise ValueError

        msg = StandardSend(target, flags, cmd1, cmd2out, acknak)
        self.send_msg(msg)

    def send_extended(self, target, commandtuple, cmd2=None, flags=0x00, acknak=None, **userdata):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError
        if cmd2out is None:
           if cmd2 is not None:
               cmd2out = cmd2
           else:
                raise ValueError

        msg = ExtendedSend(target, cmd1, cmd2out,flags,  acknak, **userdata)
        self.send_msg(msg)

    def _get_plm_info(self):
        """Request PLM Info."""
        self.log.debug("Starting: _get_plm_info")
        self.log.info('Requesting PLM Info')
        msg = GetImInfo()
        self.send_msg(msg)
        self.log.debug("Ending: _get_plm_info")

    def _handle_assign_to_all_link_group(self, msg):
        self.log.debug("Starting _handle_assign_to_all_link_group")

        if msg.isbroadcastflag:
            cat = msg.target.bytes[0:1]
            subcat = msg.target.bytes[1:2]
            product_key = msg.target.bytes[2:3]
            self.log.info('Received Device ID with address: %s  cat: 0x%s  subcat: 0x%s  firmware: 0x%s', 
                            msg.address.hex, binascii.hexlify(cat), binascii.hexlify(subcat), binascii.hexlify(product_key))
            device = self.devices.create_device_from_category(self, msg.address.hex, cat, subcat)
            if device is not None:
                if isinstance(device, list):
                    for dev in device:
                        self.devices[device.id] = device
                        self.log.info('Device with id %s added to device list.', device.id)
                else:
                    self.devices[device.id] = device
                    self.log.info('Device with id %s added to device list.', device.id)
            else:
                self.log.error('Did not add device to list because the device came back None')
            self.log.info('Total Devices Found: %d', len(self.devices))
        self.log.debug("Ending _handle_assign_to_all_link_group")

    def _handle_send_standard_or_extended_message_nak(self, msg):
        self.log.debug("Starting _handle_send_standard_or_exteded_message_nak")
        if msg.cmd1 == COMMAND_ID_REQUEST_0X10_0X00['cmd1']:
            retries = self._aldb_response_queue[msg.target.hex]['retries']
            if retries < 5:
                self.log.info('Device %s did not respond to %d tries for a device ID. Retrying.', msg.target, retries)
                self._aldb_response_queue[msg.target.hex]['retries'] = retries + 1
                self._loop.call_later(2, self._device_id_request, msg.target.hex)
            else:
                # If we have tried 5 times and did not get a device ID and
                # the ALDB record did not return a device type either
                # we remove the device from the list of devices assuming it is offline
                # If it is online it can be added manually via the device overrides
                self.log.info("Device with address %s did not respond to a request for a device ID.", msg.target.hex)
                self.log.debug("Device with address %s is being removed from the list.", msg.target.hex)
                self._aldb_response_queue.pop(msg.target.hex)
        
        self.log.debug("Ending _handle_send_standard_or_exteded_message_nak")

    def _handle_standard_or_extended_message_received(self, msg):
        self.log.debug("Starting: _handle_standard_message_received")
        # If it is not a broadcast message then it is device specific and we call the device's receive_message method
        # TODO: Is there a situation where the PLM is the device? If this is the case the PLM device will not be in the ALDB
        device = self.devices[msg.address.hex]
        if device is not None:
            device.receive_message(msg)

        self.log.debug("Ending: _handle_standard_message_received")

    def _handle_all_link_record_response(self, msg):
        self.log.debug('Starting _handle_all_link_record_response')

        self._aldb_response_queue[msg.address.hex] = {'msg':msg, 'retries':0}
        self._get_next_all_link_record()
        
        self.log.debug('Ending _handle_all_link_record_response')

    def _handle_get_next_all_link_record_nak(self, msg):
        self.log.debug('Starting _handle_get_next_all_link_record_acknak')

        # When the last All-Link record is reached the PLM sends a NAK
        self.log.debug('Devices found: %d', len(self._aldb_response_queue))
        for addr in self._aldb_response_queue:
            aldbRecordMessage = self._aldb_response_queue[addr]['msg']
            cat = aldbRecordMessage.linkdata1
            subcat = aldbRecordMessage.linkdata2
            product_key = aldbRecordMessage.linkdata3

            # Get a device from the ALDB based on cat, subcat and product_key
            device = self.devices.create_device_from_category(self, aldbRecordMessage.address, cat, subcat, product_key)

            # If a device is returned and that device is of a type tha stores the product data in the ALDB record
            # we can use that as the device type for this record
            # Otherwise we need to request the device ID.
            if device is not None:
                if device.prod_data_in_aldb:
                    if device is not None:
                        if isinstance(device, list):
                            for dev in device:
                                self.devices[device.id] = device
                                self.log.info('--------------------------------------------------------')
                                self.log.info('Device with id %s added to device list from ALDB Data.', device.id)
                                self.log.info('--------------------------------------------------------')
                        else:
                            self.devices[device.id] = device
                            self.log.info('--------------------------------------------------------')
                            self.log.info('Device with id %s added to device list from ALDB data.', device.id)
                            self.log.info('--------------------------------------------------------')

        for addr in self.devices:
            try:
                self._aldb_response_queue.pop(addr)
            except:
                pass
        delay = 2
        for addr in self._aldb_response_queue:
            self._loop.call_later(delay, self._device_id_request, addr)
            delay += 2

        self.log.debug('Ending _handle_get_next_all_link_record_acknak')

    def _handle_get_plm_info(self, msg):
        self.log.debug('Starting _handle_get_plm_info')
        self.address = msg.address
        self.category = msg.category
        self.subcategory = msg.subcategory
        self.firmware = msg.firmware
        self.log.debug('Ending _handle_get_plm_info')

    def _load_all_link_database(self):
        """Load the ALL-Link Database into object."""
        self.log.debug("Starting: _load_all_link_database")
        self.devices.state = 'loading'
        self._get_first_all_link_record()
        self.log.debug("Ending: _load_all_link_database")

    def _get_first_all_link_record(self):
        """Request first ALL-Link record."""
        self.log.debug("Starting: _get_first_all_link_record")
        self.log.info('Requesting First ALL-Link Record')
        msg = GetFirstAllLinkRecord()
        self.send_msg(msg)
        self.log.debug("Ending: _get_first_all_link_record")

    def _get_next_all_link_record(self):
        """Request next ALL-Link record."""
        self.log.debug("Starting: _get_next_all_link_recor")
        self.log.info('Requesting Next ALL-Link Record')
        msg = GetNextAllLinkRecord()
        self.send_msg(msg)
        self.log.debug("Ending: _get_next_all_link_recor")

    def _device_id_request(self, addr):
        """Request a device ID from a device"""
        self.log.debug("Starting: _device_id_request")
        if isinstance(addr, Address):
            device = addr
        else:
            device = Address(addr)
        self.log.info('Requesting device ID for %s', device.human)
        msg = StandardSend(device, 0x00, COMMAND_ID_REQUEST_0X10_0X00['cmd1'], COMMAND_ID_REQUEST_0X10_0X00['cmd1'])
        self.send_msg(msg)
        self.log.debug("Ending: _device_id_request")

    def _product_data_request(self, addr):
        """Request Product Data Record for device."""
        self.log.debug("Starting: _product_data_request")
        device = Address(addr)
        self.log.info('Requesting product data for %s', device.human)
        msg = StandardSend(device, 0x00, COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00['cmd1'], COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00['cmd2'])    
        self.send_msg(msg)
        self.log.debug("Starting: _product_data_request")
    
    def _peel_messages_from_buffer(self):
        self.log.debug("Starting: _peel_messages_from_buffer")
        lastlooplen = 0
        worktodo = True

        while worktodo:
            if len(self._buffer) == 0:
                self.log.debug('Clean break!  There is no buffer left')
                worktodo = False
                break
            msg = Message.create(self._buffer)

            if msg is not None:
                self._recv_queue.appendleft(msg)
                self._buffer = self._buffer[len(msg.bytes):]

            if len(self._buffer) < 2:
                worktodo = False
                break

            if len(self._buffer) == lastlooplen:
                # Buffer size did not change so we should wait for more data
                worktodo = False
                break

            lastlooplen = len(self._buffer)

        self.log.debug("Finishing: _peel_messages_from_buffer")


# pylint: disable=too-many-instance-attributes, too-many-public-methods
#class PLMOld(asyncio.Protocol):
#    """The Insteon PLM IP control protocol handler."""

#    def __init__(self, loop=None, connection_lost_callback=None, userdefineddevices=()):
#        """Protocol handler that handles all status and changes on PLM.

#        This class is expected to be wrapped inside a Connection class object
#        which will maintain the socket and handle auto-reconnects.

#            :param connection_lost_callback:
#                called when connection is lost to device (optional)
#            :param loop:
#                asyncio event loop (optional)

#            :type: connection_lost_callback:
#                callable
#            :type loop:
#                asyncio.loop
#        """
#        self._loop = loop

#        self._connection_lost_callback = connection_lost_callback
#        self._update_callbacks = []
#        self._message_callbacks = []
#        self._insteon_callbacks = []

#        self._buffer = bytearray()
#        self._last_message = None
#        self._last_command = None
#        self._wait_for = {}
#        self._recv_queue = []
#        self._send_queue = []

#        self._device_queue = []

#        self.devices = ALDB()

#        self.log = logging.getLogger(__name__)
#        self.transport = None

#        self._me = {}

#        self._userdefineddevices = {}

#        for userdevice in userdefineddevices:
#            if 'cat' in userdevice and 'subcat' in userdevice and 'firmware' in userdevice:
#                self._userdefineddevices[userdevice["address"]] = {
#                    "cat": userdevice["cat"],
#                    "subcat": userdevice["subcat"],
#                    "firmware": userdevice["firmware"],
#                    "status": "notfound"
#                }
#                self.devices[userdevice["address"]] = {'cat': userdevice["cat"],
#                                            'subcat': userdevice["subcat"],
#                                            'firmware': userdevice["firmware"]}

#        self.add_message_callback(self._parse_insteon_standard, {'code': 0x50})
#        self.add_message_callback(self._parse_insteon_extended, {'code': 0x51})
#        self.add_message_callback(self._parse_all_link_completed, {'code': 0x53})
#        self.add_message_callback(self._parse_button_event, {'code': 0x54})
#        self.add_message_callback(self._parse_all_link_record, {'code': 0x57})
#        self.add_message_callback(self._parse_get_plm_info, {'code': 0x60})
#        self.add_message_callback(self._parse_get_plm_config, {'code': 0x73})

#        self.add_insteon_callback(self._parse_device_info_response, {'cmd1': 0x01})
#        self.add_insteon_callback(self._parse_product_data_response, {'cmd1': 0x03, 'cmd2': 0x00})
#        self.add_insteon_callback(self._insteon_on, {'cmd1': 0x11})
#        self.add_insteon_callback(self._insteon_on, {'cmd1': 0x12})
#        self.add_insteon_callback(self._insteon_off, {'cmd1': 0x13})
#        self.add_insteon_callback(self._insteon_off, {'cmd1': 0x14})
#        self.add_insteon_callback(self._insteon_manual_change_stop, {'cmd1': 0x18})

#    #
#    # asyncio network functions
#    #

#    def connection_made(self, transport):
#        """Called when asyncio.Protocol establishes the network connection."""
#        self.log.info('Connection established to PLM')
#        self.transport = transport

#        # self.transport.set_write_buffer_limits(128)
#        # limit = self.transport.get_write_buffer_size()
#        # self.log.debug('Write buffer size is %d', limit)
#        self.get_plm_info()
#        self.load_all_link_database()

#    def data_received(self, data):
#        self.log.debug("Starting: data_received")
#        """Called when asyncio.Protocol detects received data from network."""
#        self.log.debug('Received %d bytes from PLM: %s',
#                       len(data), binascii.hexlify(data))

#        self._buffer.extend(data)
#        self._peel_messages_from_buffer()

#        for message in self._recv_queue:
#            self._process_message(message)
#            self._recv_queue.remove(message)
#        self.log.debug("Finishing: data_received")

#    def connection_lost(self, exc):
#        """Called when asyncio.Protocol loses the network connection."""
#        if exc is None:
#            self.log.warning('eof from modem?')
#        else:
#            self.log.warning('Lost connection to modem: %s', exc)

#        self.transport = None

#        if self._connection_lost_callback:
#            self._connection_lost_callback()

#    def _returnsize(self, message):
#        code = message[1]
#        ppc = PP.lookup(code, fullmessage=message)

#        if hasattr(ppc, 'returnsize') and ppc.returnsize:
#            self.log.debug('Found a code 0x%x message which returns %d bytes',
#                           code, ppc.returnsize)
#            return ppc.returnsize
#        else:
#            self.log.debug('Unable to find an returnsize for code 0x%x', code)
#            return len(message) + 1

#    def _timeout_reached(self):
#        self.log.debug('_timeout_reached invoked')
#        self._clear_wait()
#        self._process_queue()

#    def _clear_wait(self):
#        self.log.debug('Starting: _clear_wait')
#        if '_thandle' in self._wait_for:
#            self._wait_for['_thandle'].cancel()
#        self._wait_for = {}
#        self.log.debug("Finishing: _clear_wait")
        
#    def _schedule_wait(self, keys, timeout=1):
#        self.log.debug("Starting: _schedule_wait")
#        if self._wait_for != {}:
#            self.log.warning('Overwriting stale wait_for: %s', self._wait_for)
#            self._clear_wait()

#        self.log.debug('Waiting for %s timeout in %d seconds', keys, timeout)
#        if timeout > 0:
#            keys['_thandle'] = self._loop.call_later(timeout,
#                                                     self._timeout_reached)

#        self._wait_for = keys
#        self.log.debug("Finishing: _schedule_wait")

#    def _wait_for_last_command(self):
#        self.log.debug("Starting: _wait_for_last_command")
#        sentmessage = self._last_command
#        returnsize = self._returnsize(sentmessage)
#        self.log.debug('Wait for ACK/NAK on sent: %s expecting return size of %d',
#                       binascii.hexlify(sentmessage), returnsize)
#        self.log.debug('Find result: %d', binascii.hexlify(self._buffer).find(binascii.hexlify(sentmessage)) )
#        if binascii.hexlify(self._buffer).find(binascii.hexlify(sentmessage)) == 0: 
#            if len(self._buffer) < returnsize:
#                self.log.debug('Waiting for all of message to arrive, %d/%d',
#                               len(self._buffer), returnsize)
#                return

#            code = self._buffer[1]
#            message_length = len(sentmessage)
#            response_length = returnsize - message_length
#            response = self._buffer[message_length:response_length]
#            acknak = self._buffer[returnsize-1]

#            mla = self._buffer[:returnsize-1]
#            buffer = self._buffer[returnsize:]

#            data_in_ack = [0x19, 0x2e]
#            msg = Message(mla)

#            queue_ack = False

#            if sentmessage != mla:
#                self.log.debug('sent command and ACK response differ')
#                queue_ack = True

#            if hasattr(msg, 'cmd1') and msg.cmd1 in data_in_ack:
#                self.log.debug('sent cmd1 is on queue_ack list')
#                queue_ack = True

#            if acknak == 0x06:
#                if len(response) > 0 or queue_ack is True:
#                    self.log.debug('Sent command %s OK with response %s',
#                                  binascii.hexlify(sentmessage), response)
#                    self._recv_queue.append(mla)
#                else:
#                    self.log.debug('Sent command %s OK',
#                                   binascii.hexlify(sentmessage))

#            else:
#                if code == 0x6a:
#                    self.log.info('ALL-Link database dump is complete')
#                    self.devices.state = 'loaded'
#                    for address in self._device_queue:
#                        #self.get_device_info(address)
#                        self.product_data_request(address)

#                    for userdevice in self._userdefineddevices:
#                        if self._userdefineddevices[userdevice]["status"] == "notfound":
#                            self.log.info("Failed to discover device %r.", userdevice)
#                    self.poll_devices()
#                else:
#                    self.log.warning('Sent command %s UNsuccessful! (%02x)',
#                                     binascii.hexlify(sentmessage), acknak)
#            self._last_command = None
#            self._buffer = buffer
##        else:
##            self.log.debug('Could not find last message %s in buffer %s.', binascii.hexlify(sentmessage), binascii.hexlify(self._buffer))
##            self._wait_for_recognized_message()
#        self.log.debug("Finishing: _wait_for_last_command")

#    def _wait_for_recognized_message(self):
#        self.log.debug("Starting: _wait_for_recognized_message")
#        code = self._buffer[1]

#        for ppcode in PP:
#            if ppcode == code or ppcode == bytes([code]):
#                ppc = PP.lookup(code, fullmessage=self._buffer)

#                self.log.debug('Found a code %02x message which is %d bytes',
#                               code, ppc.size)
#                self.log.debug(binascii.hexlify(self._buffer))
#                if len(self._buffer) >= ppc.size:
#                    new_message = self._buffer[0:ppc.size]
#                    self.log.debug('new message is: %s',
#                                   binascii.hexlify(new_message))
#                    self._recv_queue.append(new_message)
#                    self._buffer = self._buffer[ppc.size:]
#                else:
#                    self.log.debug('Expected %r bytes but received %r bytes. Need more bytes to process message.', ppc.size, len(self._buffer))
#        self.log.debug("Finishing: _wait_for_recognized_message")

#    def _peel_messages_from_buffer(self):
#        self.log.debug("Starting: _peel_messages_from_buffer")
#        lastlooplen = 0
#        worktodo = True

#        while worktodo:
#            if len(self._buffer) == 0:
#                self.log.debug('Clean break!  There is no buffer left')
#                worktodo = False
#                break

#            if len(self._buffer) < 2:
#                worktodo = False
#                break

#            if self._buffer[0] != 2:
#                self._buffer = self._buffer[1:]
#                self.log.debug('Trimming leading buffer garbage')

#            if len(self._buffer) == lastlooplen:
#                # Buffer size did not change so we should wait for more data
#                worktodo = False
#                break

#            lastlooplen = len(self._buffer)

#            if self._buffer.find(2) < 0:
#                self.log.debug('Buffer does not contain a 2, we should bail')
#                worktodo = False
#                break

##            if self._last_command:
##                self._wait_for_last_command()
##            else:
#            self._wait_for_recognized_message()

#        self._process_queue()
#        self.log.debug("Finishing: _peel_messages_from_buffer")

#    def _process_queue(self):
#        self.log.debug("Starting: _process_queue")
#        self.log.debug('Send queue contains %d items', len(self._send_queue))

#        if self._clear_to_send() is True:
#            command, wait_for = self._send_queue[0]
#            self._send_hex(command, wait_for=wait_for)
#            self._send_queue.remove([command, wait_for])
#        self.log.debug("Finishing: _process_queue")

#    def _clear_to_send(self):
#        self.log.debug("Starting: _clear_to_send")
#        if len(self._buffer) == 0:
#            if len(self._send_queue) > 0:
#                if self._last_command is None:
#                    if self._wait_for == {}:
#                        return True
#        self.log.debug("Finishing: _clear_to_send")

#    def _process_message(self, rawmessage):
#        self.log.debug("Starting: _process_message")
#        self.log.debug('Processing message: %s', binascii.hexlify(rawmessage))
#        if rawmessage[0] != 2 or len(rawmessage) < 2:
#            self.log.warning('process_message called with a malformed message')
#            return

#        if rawmessage == self._last_message:
#            self.log.debug('ignoring duplicate message')
#            return

#        self._last_message = rawmessage

#        msg = Message(rawmessage)

#        # if hasattr(msg, 'target') and msg.target != self._me['address']:
#        #     self.log.info('Ignoring message that is not for me')
#        #     return

#        if self._message_matches_criteria(msg, self._wait_for):
#            if '_callback' in self._wait_for:
#                self._clear_wait()
#                self._process_queue()
#                return
#            else:
#                self._clear_wait()

#        callbacked = False
#        for callback, criteria in self._message_callbacks:
#            if self._message_matches_criteria(msg, criteria):
#                self.log.debug('message callback %s with criteria %s',
#                               callback, criteria)
#                self._loop.call_soon(callback, msg)
#                callbacked = True

#        if callbacked is False:
#            ppc = PP.lookup(msg.code, fullmessage=rawmessage)
#            if hasattr(ppc, 'name') and ppc.name:
#                self.log.info('Unhandled event: %s (%s)', ppc.name,
#                              binascii.hexlify(rawmessage))
#            else:
#                self.log.info('Unrecognized event: UNKNOWN (%s)',
#                              binascii.hexlify(rawmessage))

#        self._process_queue()
#        self.log.debug("Finishing: _process_message")

#    def _message_matches_criteria(self, msg, criteria):
#        self.log.debug("Starting: _message_matches_criteria")
#        match = True

#        if criteria is None or criteria == {}:
#            return True

#        if 'address' in criteria:
#            criteria['address'] = Address(criteria['address'])

#        for key in criteria.keys():
#            if key[0] != '_':
#                mattr = getattr(msg, key, None)
#                if mattr is None:
#                    match = False
#                    break
#                elif criteria[key] != mattr:
#                    match = False
#                    break

#        if match is True:
#            if '_callback' in criteria:
#                self.log.debug('Calback invoked from mmc criteria')
#                criteria['_callback'](msg)

#        self.log.debug("Finishing: _message_matches_criteria")
#        return match

#    def _parse_insteon_standard(self, msg):
#        self.log.debug("Starting: _parse_insteon_standard")
#        try:
#            device = self.devices[msg.address.hex]
#        except:
#            device = None

#        self.log.info('INSTEON standard %r->%r: cmd1:%02x cmd2:%02x flags:%02x',
#                      msg.address, msg.target,
#                      msg.cmd1, msg.cmd2, msg.flagsval)
#        self.log.debug('flags: %r', msg.flags)
#        self.log.debug('device: %r', device)

#        for callback, criteria in self._insteon_callbacks:
#            if self._message_matches_criteria(msg, criteria):
#                self.log.debug('insteon callback %s with criteria %s',
#                               callback, criteria)
#                self._loop.call_soon(callback, msg, device)

#        if msg.cmd1 == 0x03 and msg.cmd2 == 0x00:
##            self._parse_product_data_response(msg.address, msg.userdata)
#            self.get_device_info(msg.address.hex)
#        self.log.debug("Finish: _parse_insteon_standard")

#    def _parse_insteon_extended(self, msg):
#        self.log.debug("Starting: _parse_insteon_extended")
#        try:
#            device = self.devices[msg.address.hex]
#        except:
#            device = None

#        self.log.info('INSTEON extended %r->%r: cmd1:%02x cmd2:%02x flags:%02x data:%s',
#                      msg.address, msg.target, msg.cmd1, msg.cmd2, msg.flagsval,
#                      binascii.hexlify(msg.userdata))
#        self.log.debug('flags: %r', msg.flags)
#        self.log.debug('device: %r', device)

#        for callback, criteria in self._insteon_callbacks:
#            if self._message_matches_criteria(msg, criteria):
#                self.log.debug('insteon callback %s with criteria %s',
#                               callback, criteria)
#                self._loop.call_soon(callback, msg, device)

##        if msg.cmd1 == 0x03 and msg.cmd2 == 0x00:
##            self._parse_product_data_response(msg.address, msg.userdata)
##            self._parse_product_data_response(msg, device)
#        self.log.debug("Finishing: _parse_insteon_extended")

#    def _parse_status_response(self, msg):
#        self.log.debug("Starting: _parse_status_response")
#        onlevel = msg.cmd2

#        self.log.info('INSTEON device status %r is at level %s',
#                      msg.address, hex(onlevel))
#        self.devices.setattr(msg.address, 'onlevel', onlevel)
#        self._do_update_callback(msg)
#        self.log.debug("Finishing: _parse_status_response")

#    def _parse_sensor_response(self, msg):
#        device = self.devices[msg.address.hex]

#        sensorstate = msg.cmd2

#        if device.get('model') == '2450':
#            # Swap the values for a 2450 because it's opposite
#            self.log.debug('Reversing sensorstate %s because 2450', sensorstate)
#            if sensorstate:
#                sensorstate = 0
#            else:
#                sensorstate = 1

#        self.log.info('INSTEON sensor status %r is at level %s',
#                      msg.address, hex(sensorstate))
#        self.devices.setattr(msg.address, 'sensorstate', sensorstate)
#        self._do_update_callback(msg)

#    def _insteon_on(self, msg, device):
#        self.log.info('INSTEON on event: %r, %r', msg, device)

#        attribute = 'onlevel'

#        if 'binary_sensor' in device.get('capabilities'):
#            if msg.flags.get('group', False):
#                #
#                # If this is a group message from a sensor device, then we
#                # treat it as sensorstate instead of onlevel.  This is vital
#                # for I/O Linc 2450 devices, because it's the cleanest way
#                # to differntiate between the sensor on/off notifications and
#                # the relay on/off notifications that come in response to a
#                # turn_on or turn_off command.  Those on/off messages are
#                # direct (not group, not broadcast) and reflect the relay's
#                # status and not the sensor's status.
#                #
#                attribute = 'sensorstate'

#        if msg.cmd2 == 0x00:
#            value = 255
#        else:
#            value = msg.cmd2

#        if device.get('model') == '2477D':
#            if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
#                value = device.get('setlevel', 255)
#                self.log.debug('ON report with no onlevel, using %02x', value)

#        if self.devices.setattr(msg.address, attribute, value):
#            self._do_update_callback(msg)

#    def _insteon_off(self, msg, device):
#        self.log.info('INSTEON off event: %r, %r', msg, device)

#        attribute = 'onlevel'

#        if 'binary_sensor' in device.get('capabilities'):
#            if msg.flags.get('group', False):
#                #
#                # If this is a group message from a sensor device, then we
#                # treat it as sensorstate instead of onlevel.  This is vital
#                # for I/O Linc 2450 devices, because it's the cleanest way
#                # to differntiate between the sensor on/off notifications and
#                # the relay on/off notifications that come in response to a
#                # turn_on or turn_off command.  Those on/off messages are
#                # direct (not group, not broadcast) and reflect the relay's
#                # status and not the sensor's status.
#                #
#                attribute = 'sensorstate'

#        if self.devices.setattr(msg.address, attribute, 0):
#            self._do_update_callback(msg)

#    # pylint: disable=unused-argument
#    def _insteon_manual_change_stop(self, msg, device):
#        self.log.info('Light Stop Manual Change')
#        self.status_request(msg.address)

#    def _parse_extended_status_response(self, msg):
#        device = self.devices[msg.address.hex]

#        self.log.info('INSTEON extended device status %r', msg.address)
#        if device.get('cat') == 0x01:
#            self.devices.setattr(msg.address, 'ramprate', msg.userdata[6])
#            self.devices.setattr(msg.address, 'setlevel', msg.userdata[7])

#    def _do_update_callback(self, msg):
#        for callback, criteria in self._update_callbacks:
#            if self._message_matches_criteria(msg, criteria):
#                self.log.debug('update callback %s with criteria %s',
#                               callback, criteria)
#                self._loop.call_soon(callback, msg)

#    def _parse_product_data_response(self, msg, device):
#        self.log.debug("Starting: _parse_product_data_response")
#        self.log.info("message:")
#        self.log.info(msg)
        
#        if msg.code == binascii.a2b_hex('51'):
#            category = msg.userdata[4]
#            subcategory = msg.userdata[5]
#            firmware = msg.userdata[6]
#            #self.log.info('INSTEON Product Data Response from %r: cat:%r, subcat:%r',
#            #              msg.address.hex, hex(category), hex(subcategory))
#            self.log.info('INSTEON Product Data Response from %r: cat:%02x, subcat:%02x',
#                      msg.address.hex, 
#                      category, 
#                      subcategory)
        
#            self.devices[msg.address.hex] = {'cat': category, 'subcat': subcategory,
#                                            'firmware': firmware}
#        else:
#            self.log.debug('_parse_product_data_response was not an extended message. Defaulting to get_device_info')
#            self.get_device_info(msg.address.hex)

#        self.log.debug("Finishing: _parse_device_info_response")

#    def _parse_device_info_response(self, msg, device):
#        self.log.debug("Starting: _parse_device_info_response")
#        self.log.info("message:")
#        self.log.info(msg)
#        productdata = binascii.unhexlify(msg.target.hex)
#        category = productdata[0]
#        self.log.info("category: %02x", category)
#        subcategory = productdata[1]
#        firmware = productdata[2]
#        #self.log.info('INSTEON Product Data Response from %r: cat:%r, subcat:%r',
#        #              msg.address.hex, hex(category), hex(subcategory))
#        self.log.info('INSTEON Product Data Response from %r: cat:%02x, subcat:%02x',
#                      msg.address.hex, 
#                      category, 
#                      subcategory)

        
#        self.devices[msg.address.hex] = {'cat': category, 'subcat': subcategory,
#                                     'firmware': firmware}

##        if self.devices.state == 'loading':
##            time.sleep(1)
##            self.get_next_all_link_record()
#        self.log.debug("Finishing: _parse_device_info_response")

#    def _parse_button_event(self, msg):
#        self.log.info('PLM button event: %02x (%s)', msg.event, msg.description)

#    def _parse_get_plm_info(self, msg):
#        self.log.debug("Starting: _parse_get_plm_info")
#        self.log.info('PLM Info from %r: category:%02x subcat:%02x firmware:%02x',
#                      msg.address, msg.category, msg.subcategory, msg.firmware)

#        self._me['address'] = msg.address
#        self._me['category'] = msg.category
#        self._me['subcategory'] = msg.subcategory
#        self._me['firmware'] = msg.firmware
#        self.log.debug("Finishing: _parse_get_plm_info")

#    def _parse_get_plm_config(self, msg):
#        self.log.info('PLM Config: flags:%02x spare:%02x spare:%02x',
#                      msg.flagsval, msg.spare1, msg.spare2)

#    def _parse_all_link_record(self, msg):
#        self.log.debug("Starting: _parse_all_link_record")
#        self.log.info('ALL-Link Record for %r: flags:%02x group:%02x data:%02x/%02x/%02x',
#                      msg.address, msg.flagsval, msg.group,
#                      msg.linkdata1, msg.linkdata2, msg.linkdata3)
        
#        if self._me['subcategory'] == 0x20:
#            # USB Stick has a different ALDB message format.  I don't actually
#            # think that linkdata1 is firmware, but whatever.  Shouldn't have
#            # any effect storing the value there anyway.
#            category = msg.linkdata2
#            subcategory = msg.linkdata3
#            firmware = msg.linkdata1
#        else:
#            # Regular PLM format
#            category = msg.linkdata1
#            subcategory = msg.linkdata2
#            firmware = msg.linkdata3

#        if (category > 0x01):
#            if (msg.address.hex in self.devices):
#                self.log.info("Device %r is already added manually.", msg.address.hex)
#                if msg.address.hex in self._userdefineddevices:
#                    self._userdefineddevices[msg.address.hex]["status"] = "found"
#            else: 
#                self.log.info("All-Link Record returned device %r cat %s subcat %s firmware %s.", msg.address.hex, msg.linkdata1, msg.linkdata2, msg.linkdata3)
#                self.devices[msg.address.hex] = {'cat': msg.linkdata1,
#                                         'subcat': msg.linkdata2,
#                                         'firmware': msg.linkdata3}
#        else:
#            self._device_queue.append(msg.address.hex)
        
#        if self.devices.state == 'loading':
#            self.get_next_all_link_record()
#        self.log.debug("Finishing: _parse_all_link_record")

#    def _parse_all_link_completed(self, msg):
#        self.log.debug("Starting: _parse_all_link_completed")
#        self.log.info('ALL-Link Completed %r: group:%d cat:%02x subcat:%02x '
#                      'firmware:%02x linkcode: %02x',
#                      msg.address, msg.group, msg.category, msg.subcategory,
#                      msg.firmware, msg.linkcode)

#        if msg.address.hex in self.devices:
#            self.log.info("Device %r is already added manually.", msg.address.hex)
#            if msg.address.hex in self._userdefineddevices:
#                self._userdefineddevices[msg.address.hex]["status"] = "found"
#        else:
#            self.log.info("Auto Discovering device %r.", msg.address.hex)
#            self.devices[msg.address.hex] = {'cat': msg.category,
#                                         'subcat': msg.subcategory,
#                                         'firmware': msg.firmware}
#        for userdevice in self._userdefineddevices:
#            if self._userdefineddevices[userdevice]["status"] == "notfound":
#                self.log.info("Finished all link, and failed to discover device %r.", userdevice)
#        self.log.debug("Finishing: _parse_all_link_completed")

#    def _queue_hex(self, message, wait_for=None):
#        if wait_for is None:
#            wait_for = {}

#        self.log.debug('Adding command to queue: %s', message)
#        self._send_queue.append([message, wait_for])

#    def _send_hex(self, message, wait_for=None):
#        if wait_for is None:
#            wait_for = {}

#        if self._last_command or self._wait_for:
#            self.log.debug('Still waiting on last_command.')
#            self._queue_hex(message, wait_for)
#        else:
#            self._send_raw(binascii.unhexlify(message))
#            self._schedule_wait(wait_for, 3)

#    def _send_raw(self, message):
#        self.log.debug('Sending %d byte message: %s',
#                      len(message), binascii.hexlify(message))
#        time.sleep(1)
#        self.transport.write(message)
#        self._last_command = message

#    def add_message_callback(self, callback, criteria):
#        """Register a callback for when a matching message is seen."""
#        self._message_callbacks.append([callback, criteria])
#        self.log.debug('Added message callback to %s on %s', callback, criteria)

#    def add_insteon_callback(self, callback, criteria):
#        """Register a callback for when a matching INSTEON command is seen."""
#        self._insteon_callbacks.append([callback, criteria])
#        self.log.debug('Added INSTEON callback to %s on %s', callback, criteria)

#    def add_update_callback(self, callback, criteria):
#        """Register as callback for when a matching device attribute changes."""
#        self._update_callbacks.append([callback, criteria])
#        self.log.debug('Added update callback to %s on %s', callback, criteria)

#    def add_device_callback(self, callback, criteria):
#        """Register a callback for when a matching new device is seen."""
#        self.devices.add_device_callback(callback, criteria)

#    def send_insteon_standard(self, device, cmd1, cmd2, wait_for=None):
#        """Send an INSTEON Standard message to the PLM."""
#        if wait_for is None:
#            wait_for = {}

#        device = Address(device)
#        rawstr = '0262'+device.hex+'00'+cmd1+cmd2
#        self._send_hex(rawstr, wait_for)

#    # pylint: disable=too-many-arguments
#    def send_insteon_extended(self, device, cmd1, cmd2,
#                              userdata='0000000000000000000000000000',
#                              wait_for=None):
#        """Send an INSTEON Extended message to the PLM."""
#        if wait_for is None:
#            wait_for = {}

#        device = Address(device)
#        rawstr = '0262'+device.hex+'10'+cmd1+cmd2+userdata
#        self._send_hex(rawstr, wait_for)

#    def get_plm_info(self):
#        """Request PLM Info."""
#        self.log.info('Requesting PLM Info')
#        self._send_hex('0260')

#    def get_plm_config(self):
#        """Request PLM Config."""
#        self.log.info('Requesting PLM Config')
#        self._send_hex('0273')

#    def factory_reset(self):
#        """Reset the IM and clear the All-Link Database."""
#        self.log.info('Nuking from orbit')
#        self._send_hex('0267')

#    def start_all_linking(self):
#        """Puts the IM into ALL-Linking mode without using the SET Button."""
#        self.log.info('Start ALL-Linking')
#        self._send_hex('02640101')

#    def cancel_all_linking(self):
#        """Cancels the ALL-Linking started previously."""
#        self.log.info('Cancel ALL-Linking')
#        self._send_hex('0265')

#    def get_first_all_link_record(self):
#        """Request first ALL-Link record."""
#        self.log.info('Requesting First ALL-Link Record')
#        self._send_hex('0269') #, wait_for={'code': 0x57})

#    def get_next_all_link_record(self):
#        """Request next ALL-Link record."""
#        self.log.info('Requesting Next ALL-Link Record')
#        self._send_hex('026a') #, wait_for={'code': 0x57})

#    def load_all_link_database(self):
#        """Load the ALL-Link Database into object."""
#        self.devices.state = 'loading'
#        self.get_first_all_link_record()

#    def product_data_request(self, addr):
#        """Request Product Data Record for device."""
#        device = Address(addr)
#        self.log.info('Requesting product data for %s', device.human)
#        #time.sleep(2)
#        self.send_insteon_standard(
#            device, '03', '00') 

#    def get_device_info(self, addr):
#        self.log.debug("Starting: get_device_info")
#        """Request Product Data Record for device."""
#        device = Address(addr)
#        self.log.info('Requesting device info for %s', device.human)
#        #time.sleep(1)
#        self.send_insteon_standard(
#            device, '10', '00') #,
##            wait_for={'code': 0x50, 'cmd1': 0x01})
#        self.log.debug("Finishing: get_device_info")

#    def text_string_request(self, addr):
#        """Request Device Text String."""
#        device = Address(addr)
#        self.log.info('Requesting text string for %s', device.human)
#        self.send_insteon_standard(
#            device, '03', '02',
#            wait_for={'code': 0x51, 'cmd1': 0x03, 'cmd2': 0x02})

#    def status_request(self, addr, cmd2='00'):
#        """Request Device Status."""
#        address = Address(addr)
#        device = self.devices[address.hex]

#        if 'no_requests' in device.get('capabilities'):
#            self.log.debug('Skipping status_request for no_requests device %r (%s)',
#                           address, device.get('model', 'Unknown Model'))
#            return

#        self.log.info('Requesting status for %r', address)

#        callback = self._parse_status_response
#        if device.get('model') == '2450':
#            if cmd2 == '00':
#                self._loop.call_later(1, self.status_request, address, '01')
#            else:
#                callback = self._parse_sensor_response

#        elif 'binary_sensor' in device.get('capabilities'):
#            callback = self._parse_sensor_response

#        self.send_insteon_standard(
#            address, '19', cmd2,
#            wait_for={'code': 0x50, '_callback': callback})

#    def extended_status_request(self, addr):
#        """Request Operating Flags for device."""
#        device = Address(addr)
#        self.log.info('Requesting extended status for %s', device.human)
#        self.send_insteon_extended(
#            device, '2e', '00',
#            wait_for={'code': 0x51, '_callback': self._parse_extended_status_response})

#    def update_setlevel(self, addr, level):
#        """Currently non-functional."""
#        device = Address(addr)
#        self.log.info('Changing setlevel on %s to %02x', device.human, level)
#        self.send_insteon_extended(
#            device, '2e', '00',
#            userdata='00067f0000000000000000000000',
#            wait_for={'code': 0x50})

#    def update_ramprate(self, addr, level):
#        """Currently non-functional."""
#        device = Address(addr)
#        self.log.info('Changing setlevel on %s to %02x', device.human, level)
#        self.send_insteon_extended(
#            device, '2e', '00',
#            userdata='00051b0000000000000000000000',
#            wait_for={'code': 0x50})

#    def get_device_attr(self, addr, attr):
#        """Return attribute on specified device."""
#        return self.devices.getattr(addr, attr)

#    def turn_off(self, addr):
#        """Send command to device to turn off."""
#        address = Address(addr)
#        self.send_insteon_standard(address, '13', '00', {})

#    def turn_on(self, addr, brightness=255, ramprate=None):
#        """Send command to device to turn on."""
#        address = Address(addr)
#        device = self.devices[address.hex]
#        self.log.debug('turn_on %r %s', addr, device.get('model'))

#        if isinstance(ramprate, int):
#            #
#            # The specs say this should work, but I couldn't get my 2477D
#            # switches to respond.  Leaving the code in place for future
#            # hacking.  If you try to use ramprate it probably won't work.
#            #
#            bhex = 'fc'
#            self.send_insteon_standard(address, '2e', bhex, {})
#        else:
#            bhex = str.format('{:02X}', int(brightness)).lower()
#            self.send_insteon_standard(address, '11', bhex, {})

#        if device.get('model') == '2450':
#            #
#            # Request status after two seconds so we can detect if the I/OLinc
#            # is configured in 'momentary contact' mode and turned off right
#            # after we sent the on.  We can't rely on regular INSTEON state
#            # broadcasts with this device because the state broadcasts come
#            # from the sensor and not the relay.
#            #
#            self._loop.call_later(2, self.status_request, address)

#    def poll_devices(self):
#        """Walk through ALDB and populate device information for each device."""
#        self.log.info('Polling all devices in ALDB')
#        for address in self.devices:
#            self.status_request(address)

#    def list_devices(self):
#        """Debugging command to expose ALDB."""
#        for address in self.devices:
#            device = self.devices[address]
#            print(address, ':', device)