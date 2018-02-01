"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import binascii
import time
from collections import deque, namedtuple
import async_timeout
import json

from .constants import *
from .aldb import ALDB
from .address import Address
from .messagecallback import MessageCallback 
from .messages import *
from .messages.message import Message
from .devices.devicebase import DeviceBase

__all__ = ('PLM')
WAIT_TIMEOUT = 2
DEVICE_INFO_FILE = 'insteon_plm_device_info.dat'

#PP = PLMProtocol()

class PLM(asyncio.Protocol, DeviceBase):
    """The Insteon PLM IP control protocol handler."""

    def __init__(self, loop=None, connection_lost_callback=None, userdefineddevices=(), workdir=None):
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
        self._workdir = workdir

        self._buffer = bytearray()
        self._recv_queue = deque([])
        self._send_queue = asyncio.Queue(loop=self._loop)
        self._wait_acknack_queue = []
        self._aldb_response_queue = {}
        self.devices = ALDB()
        self._write_transport_lock = asyncio.Lock(loop=self._loop)
        self._message_callbacks = MessageCallback()
        self._saved_device_info = []

        self._address = None
        self._cat = None
        self._subcat = None
        self._product_key = None

        self.log = logging.getLogger(__name__)
        self.transport = None
        

        self._message_callbacks.add(StandardSend.template(acknak=MESSAGE_NAK),
                                    self._handle_standard_or_extended_message_nak)
        self._message_callbacks.add(ExtendedSend.template(acknak=MESSAGE_NAK),
                                    self._handle_standard_or_extended_message_nak)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE), 
                                    self._handle_assign_to_all_link_group)

        self._message_callbacks.add(AllLinkRecordResponse(None, None, None, None, None, None), 
                                    self._handle_all_link_record_response)

        self._message_callbacks.add(GetImInfo(), self._handle_get_plm_info)

        self._message_callbacks.add(GetNextAllLinkRecord(acknak=MESSAGE_NAK),
                                    self._handle_get_next_all_link_record_nak)

    @property
    def loop(self):
        return self._loop

    @property
    def message_callbacks(self):
        return self._message_callbacks

    def connection_made(self, transport):
        """Called when asyncio.Protocol establishes the network connection."""
        self.log.info('Connection established to PLM')
        self.transport = transport
        
        # Testing to see if this fixes the 2413S issue
        self.transport.serial.timeout = 1 
        self.transport.serial.write_timeout = 1
        self.transport.set_write_buffer_limits(128)
        # limit = self.transport.get_write_buffer_size()
        # self.log.debug('Write buffer size is %d', limit)
        coro = self._setup_devices()
        asyncio.ensure_future(coro, loop=self._loop)

    def data_received(self, data):
        """Called when asyncio.Protocol detects received data from network."""
        self.log.debug("Starting: data_received")
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
                self.log.debug('Processing message %s', msg)
                callbacks = self._message_callbacks.get_callbacks_from_message(msg)
                if len(callbacks) > 0:
                    for callback in callbacks:
                        self.log.debug('Calling method %s', callback.__func__)
                        self._loop.call_soon(callback, msg)
                else:
                    self.log.debug('No callback found for message %s', str(msg))
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

    def add_device_callback(self, callback):
        """Register a callback for when a matching new device is seen."""
        self.log.debug("Starting: add_device_callback")
        self.devices.add_device_callback(callback)
        self.log.debug("Ending: add_device_callback")

    def poll_devices(self):
        self.log.debug("Starting: poll_devices")
        delay = 0
        for addr in self.devices:
            device = self.devices[addr]
            self._loop.call_later(delay, device.async_refresh_state)
            delay += 0
        self.log.debug("Ending: poll_devices")

    def send_msg(self, msg):
        """Places a message on the send queue for sending in the order they are placed in the queue."""
        self.log.debug("Starting: send_msg")
        write_message_coroutine = self._write_message_from_send_queue()
        self._send_queue.put_nowait(msg)
        asyncio.ensure_future(write_message_coroutine)
        self.log.debug("Ending: send_msg")

    def send_standard(self, addr, commandtuple, cmd2=None, flags=0x00, acknak=None):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError

        if cmd2 is not None:
            cmd2out = cmd2

        if cmd2out is None:
            raise ValueError

        msg = StandardSend(addr, {'cmd1':cmd1, 'cmd2':cmd2out}, flags=flags, acknak=acknak) 
        self.send_msg(msg)

    def send_extended(self, addr, commandtuple, userdata, cmd2=None, flags=0x00, acknak=None):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError

        if cmd2 is not None:
            cmd2out = cmd2

        if cmd2out is None:
            raise ValueError

        msg = ExtendedSend(addr, {'cmd1':cmd1, 'cmd2':cmd2out}, userdata, flags=flags,  acknak=acknak)
        self.send_msg(msg)

    @asyncio.coroutine
    def async_sleep(self, seconds):
        """Utility method to allow devices or message handlers to pause execution and yeild back time to the asyncio loop"""
        yield from asyncio.sleep(seconds, loop=self._loop)

    @asyncio.coroutine
    def _setup_devices(self):
        saved_device_info = yield from self._load_saved_device_info()
        for savedDevice in saved_device_info:
            self.devices.add_saved_device_info(**savedDevice)
        self.log.debug('Found %d saved devices', len(self._saved_device_info))
        self._get_plm_info()
        self._load_all_link_database()

    @asyncio.coroutine
    def _write_message_from_send_queue(self):
        self.log.debug('Starting _get_from_send_queue')
        if not self._write_transport_lock.locked():
            self.log.debug('Aquiring write lock')
            yield from self._write_transport_lock.acquire()
            while True:
                self.log.debug(self._write_transport_lock.locked())
                # wait for an item from the queue
                try:
                    with async_timeout.timeout(WAIT_TIMEOUT):
                        msg = yield from self._send_queue.get()
                except asyncio.TimeoutError:
                    self.log.debug('No new messages received.')
                    break
                # process the item
                self.log.debug('Writing message: %s', msg)
                self.transport.write(msg.bytes)
                yield from asyncio.sleep(1, loop=self._loop)
            self._write_transport_lock.release()
        else:
            pass
        self.log.debug('Ending _get_from_send_queue')

    def _get_plm_info(self):
        """Request PLM Info."""
        self.log.debug("Starting: _get_plm_info")
        self.log.info('Requesting PLM Info')
        msg = GetImInfo()
        self.send_msg(msg)
        self.log.debug("Ending: _get_plm_info")

    def _handle_assign_to_all_link_group(self, msg):
        self.log.debug("Starting _handle_assign_to_all_link_group")

        if msg.flags.isBroadcast:
            cat = msg.targetLow
            subcat = msg.targetMed
            product_key = msg.targetHi
            self.log.info('Received Device ID with address: %s  cat: 0x%x  subcat: 0x%x  firmware: 0x%x', 
                            msg.address, cat, subcat, product_key)
            device = self.devices.create_device_from_category(self, msg.address, cat, subcat, product_key)
            if device is not None:
                if self.devices[device.id] == None:
                    self.devices[device.id] = device
                    self.log.info('Device with id %s added to device list.', device.id)
            else:
                self.log.error('Did not add device to list because the device came back None')
            self.log.info('Total Devices Found: %d', len(self.devices))
        self.log.debug("Ending _handle_assign_to_all_link_group")

    def _handle_standard_or_extended_message_received(self, msg):
        self.log.debug("Starting: _handle_standard_or_extended_message_received")
        # If it is not a broadcast message then it is device specific and we call the device's receive_message method
        # TODO: Is there a situation where the PLM is the device? If this is the case the PLM device will not be in the ALDB (Why not?)
        device = self.devices[msg.address.hex]
        if device is not None:
            device.receive_message(msg)

        self.log.debug("Ending: _handle_standard_or_extended_message_received")

    def _handle_all_link_record_response(self, msg):
        self.log.debug('Starting _handle_all_link_record_response')
        self.log.info('Found all link record for device %s', msg.address.hex)
        if self.devices[msg.address.hex] is None:
            cat = msg.linkdata1
            subcat = msg.linkdata2
            product_key = msg.linkdata3
            
            self.log.debug('Product data: address %s cat: %02x subcat: %02x product_key: %02x', 
                           msg.address.hex, cat, subcat, product_key)

            # Get a device from the ALDB based on cat, subcat and product_key
            device = self.devices.create_device_from_category(self, msg.address, cat, subcat, product_key)

            # If a device is returned and that device is of a type tha stores the product data in the ALDB record
            # we can use that as the device type for this record
            # Otherwise we need to request the device ID.
            if device is not None:
                if device.prod_data_in_aldb or self.devices.has_override(device.address.hex) or self.devices.has_saved(device.address.hex):
                    if self.devices[device.id] == None:
                        self.devices[device.id] = device
                        self.log.info('Device with id %s added to device list from ALDB data.', device.id)
        #Check again that the device is not alreay added, otherwise queue it up for Get ID request
        if self.devices[msg.address.hex] is None:
            unknowndevice = self.devices.create_device_from_category(self, msg.address.hex, None, None, None)
            self._aldb_response_queue[msg.address.hex] = {'device':unknowndevice, 'retries':0}

        self._get_next_all_link_record()
        
        self.log.debug('Ending _handle_all_link_record_response')

    def _handle_get_next_all_link_record_nak(self, msg):
        self.log.debug('Starting _handle_get_next_all_link_record_nak')

        # When the last All-Link record is reached the PLM sends a NAK
        self.log.debug('All-Link device records found in ALDB: %d', len(self._aldb_response_queue))

        # Remove records for devices found in the ALDB 
        # or in previous calls to _handle_get_next_all_link_record_nak
        for addr in self.devices:
            try:
                self._aldb_response_queue.pop(addr)
            except:
                pass

        staleaddr = []
        for addr in self._aldb_response_queue:
            retries = self._aldb_response_queue[addr]['retries']
            if retries < 5:
                self._aldb_response_queue[addr]['device'].id_request()
                self._aldb_response_queue[addr]['retries'] = retries + 1
            else:
                self.log.warn('Device %s found in the ALDB did not respond and is being removed from the list.', addr)
                self.log.warn('If this device is still active you can add it to the device_override configuration.')
                staleaddr.append(addr)

        for addr in staleaddr:
            self._aldb_response_queue.pop(addr)
        
        num_devices_not_added = len(self._aldb_response_queue)

        if num_devices_not_added > 0:
            # Schedule _handle_get_next_all_link_record_nak to run again later if some devices did not respond
            delay = num_devices_not_added*3
            self._loop.call_later(delay, self._handle_get_next_all_link_record_nak, None)
        else:
            self._save_device_info()
            self._loop.call_soon(self.poll_devices)
        self.log.debug('Ending _handle_get_next_all_link_record_nak')

    def _handle_standard_or_extended_message_nak(self, msg):
        if msg.flags.isExtended:
            self.send_extended(msg.address, {'cmd1':msg.cmd1, 'cmd2':msg.cmd2},  msg.userdata, flags=MESSAGE_FLAG_EXTENDED_0X10)
        else:
            self.send_standard(msg.address, {'cmd1':msg.cmd1, 'cmd2':msg.cmd2})

    def _handle_get_plm_info(self, msg):
        self.log.debug('Starting _handle_get_plm_info')
        self._address = msg.address
        self._cat = msg.category
        self._subcat = msg.subcategory
        self._product_key = msg.firmware
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

    @asyncio.coroutine
    def _load_saved_device_info(self):
        deviceinfo = []
        if self._workdir is not None:
            try:
                with open(self._workdir + '/' + DEVICE_INFO_FILE, 'r') as infile:
                    deviceinfo = json.load(infile)
            except:
                pass
        return deviceinfo

    def _save_device_info(self):
        if self._workdir is not None:
            devices = []
            for addr in self.devices:
                device = self.devices[addr]
                deviceInfo = {'address': device.address.hex, 
                              'cat': device.cat, 
                              'subcat': device.subcat, 
                              'product_key': device.product_key}
                devices.append(deviceInfo)
            coro = self._write_device_info_file(devices)
            asyncio.ensure_future(coro, loop=self._loop)

    @asyncio.coroutine
    def _write_device_info_file(self, devices):
        if self._workdir is not None:
            self.log.debug('Writing %d devices to save file', len(devices))
            with open(self._workdir + '/' + DEVICE_INFO_FILE, 'w') as outfile:
                json.dump(devices, outfile)



