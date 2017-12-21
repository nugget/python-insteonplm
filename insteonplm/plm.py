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

        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, 
                                                     None, self._handle_standard_or_extended_message_received, MESSAGE_ACK)

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
        self.log.debug('Total buffer: %s', binascii.hexlify(self._buffer))
        self._peel_messages_from_buffer()

        self.log.debug('Messages in queue: %d', len(self._recv_queue))
        worktodo = True
        while worktodo:
            try:
                msg = self._recv_queue.pop()
                self.log.debug('Processing message %s', msg.hex)
                callback = self._message_callbacks.get_callback_from_message(msg)
                if callback is not None:
                    self._loop.call_soon(callback, msg)
                else:             
                    if hasattr(msg, 'cmd1'):
                        self.log.debug('No callback found for message code %02x with cmd1 %02x and cmd2 %02x and acknak %02x', msg.code, msg.cmd1, msg.cmd2, msg.acknak)
                    else:
                        self.log.debug('No call back found for message %s', msg.hex)
            except IndexError:
                self.log.debug('Last item in self._recv_queue reached.')
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
        time.sleep(.5)
        self.log.debug('Sending %d byte message: %s', len(msg.bytes), msg.hex)
        self.transport.write(msg.bytes)

        self.log.debug("Ending: send_msg")

    def send_standard(self, target, commandtuple, cmd2=None, flags=0x00, acknak=None):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError

        if cmd2 is not None:
            cmd2out = cmd2

        if cmd2out is None:
            raise ValueError

        msg = StandardSend(target, cmd1, cmd2out, flags, acknak)
        self.send_msg(msg)

    def send_extended(self, target, commandtuple, cmd2=None, flags=0x00, acknak=None, **userdata):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError

        if cmd2 is not None:
            cmd2out = cmd2

        if cmd2out is None:
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
            device = self.devices.create_device_from_category(self, msg.address.hex, 
                                                              int.from_bytes(cat, byteorder='big'), 
                                                              int.from_bytes(subcat, byteorder='big'), 
                                                              int.from_bytes(product_key, byteorder='big'))
            if device is not None:
                if isinstance(device, list):
                    for currdev in device:
                        self.devices[currdev.id] = currdev
                        self.log.info('Device with id %s added to device list.', currdev.id)
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
            retries = self._aldb_response_queue[msg.address.hex]['retries']
            if retries < 5:
                self.log.info('Device %s did not respond to %d tries for a device ID. Retrying.', msg.address, retries)
                self._aldb_response_queue[msg.address.hex]['retries'] = retries + 1
                self._loop.call_later(2, self._device_id_request, msg.address.hex)
            else:
                # If we have tried 5 times and did not get a device ID and
                # the ALDB record did not return a device type either
                # we remove the device from the list of devices assuming it is offline
                # If it is online it can be added manually via the device overrides
                self.log.error("Device with address %s did not respond to a request for a device ID.", msg.address.hex)
                self.log.error("Device with address %s is being removed from the list.", msg.address.hex)
                self._aldb_response_queue.pop(msg.address.hex)
        
        self.log.debug("Ending _handle_send_standard_or_exteded_message_nak")

    def _handle_standard_or_extended_message_received(self, msg):
        self.log.debug("Starting: _handle_standard_or_extended_message_received")
        # If it is not a broadcast message then it is device specific and we call the device's receive_message method
        # TODO: Is there a situation where the PLM is the device? If this is the case the PLM device will not be in the ALDB
        device = self.devices[msg.address.hex]
        if device is not None:
            device.receive_message(msg)

        self.log.debug("Ending: _handle_standard_or_extended_message_received")

    def _handle_all_link_record_response(self, msg):
        self.log.debug('Starting _handle_all_link_record_response')
        self.log.info('Found all link record for device %s', msg.address.hex)
        if self.devices[addr] is None:
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
                if isinstance(device, list):
                    for currdev in device:
                        if currdev.prod_data_in_aldb:
                            self.devices[currdev.id] = currdev
                            self.log.info('Device with id %s added to device list from ALDB Data.', currdev.id)
                else:
                    if device.prod_data_in_aldb:
                        self.devices[device.id] = device
                        self.log.info('Device with id %s added to device list from ALDB data.', device.id)
        #Check again that the device is not alreay added, otherwise queue it up for Get ID request
        if self.devices[addr] is None:
            self._aldb_response_queue[msg.address.hex] = {'msg':msg, 'retries':0}

        self._get_next_all_link_record()
        
        self.log.debug('Ending _handle_all_link_record_response')

    def _handle_get_next_all_link_record_nak(self, msg):
        self.log.debug('Starting _handle_get_next_all_link_record_nak')

        # When the last All-Link record is reached the PLM sends a NAK
        self.log.debug('All-Link device records found in ALDB: %d', len(self._aldb_response_queue))
        # Remove records for devices found in the ALDB (should not be any so may remove this)
        for addr in self.devices:
            try:
                self._aldb_response_queue.pop(addr)
            except:
                pass
        delay = 2
        for addr in self._aldb_response_queue:
            self._loop.call_later(delay, self._device_id_request, addr)
            delay += 2

        self.log.debug('Ending _handle_get_next_all_link_record_nak')

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
        self.log.info('Requesting ALL-Link Records')
        msg = GetFirstAllLinkRecord()
        self.send_msg(msg)
        self.log.debug("Ending: _get_first_all_link_record")

    def _get_next_all_link_record(self):
        """Request next ALL-Link record."""
        self.log.debug("Starting: _get_next_all_link_recor")
        self.log.info("Requesting Next All-Link Record")
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
        self.log.debug('Requesting device ID for %s', device.human)
        msg = StandardSend(device, COMMAND_ID_REQUEST_0X10_0X00['cmd1'], COMMAND_ID_REQUEST_0X10_0X00['cmd1'])
        self.send_msg(msg)
        self.log.debug("Ending: _device_id_request")

    def _product_data_request(self, addr):
        """Request Product Data Record for device."""
        self.log.debug("Starting: _product_data_request")
        device = Address(addr)
        self.log.debug('Requesting product data for %s', device.human)
        msg = StandardSend(device, COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00['cmd1'], COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00['cmd2'])    
        self.send_msg(msg)
        self.log.debug("Starting: _product_data_request")
    
    def _peel_messages_from_buffer(self):
        self.log.debug("Starting: _peel_messages_from_buffer")
        lastlooplen = 0
        worktodo = True

        while worktodo:
            if len(self._buffer) == 0:
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


