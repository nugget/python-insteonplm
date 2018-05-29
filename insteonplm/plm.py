"""Module to maintain PLM state information and network interface."""

import asyncio
import logging
import binascii
from collections import deque

import async_timeout

import insteonplm.messages
from insteonplm.constants import (COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK,
                                  X10CommandType,
                                  X10_COMMAND_ALL_UNITS_OFF,
                                  X10_COMMAND_ALL_LIGHTS_ON,
                                  X10_COMMAND_ALL_LIGHTS_OFF)
from insteonplm.address import Address
from insteonplm.devices import Device, ALDBRecord, ALDBStatus
from insteonplm.linkedDevices import LinkedDevices
from insteonplm.messagecallback import MessageCallback
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.startAllLinking import StartAllLinking
from insteonplm.messages.x10received import X10Received
from insteonplm.messages.x10send import X10Send
from insteonplm.utils import (byte_to_housecode,
                              byte_to_unitcode,
                              rawX10_to_bytes,
                              x10_command_type)

__all__ = ('PLM, Hub')
WAIT_TIMEOUT = 1.5
ACKNAK_TIMEOUT = 2


class IM(Device, asyncio.Protocol):
    """The Insteon PLM IP control protocol handler.

        This class is expected to be wrapped inside a Connection class object
        which will maintain the socket and handle auto-reconnects.

            :param connection_lost_callback:
                called when connection is lost to device (optional)
            :param loop:
                asyncio event loop (optional)
            :param workdir:
                Working directory name to save device information (optional)

            :type: connection_lost_callback:
                callable
            :type loop:
                asyncio.loop
            :type workdir:
                string - valid directory path
        """

    def __init__(self, loop=None, connection_lost_callback=None,
                 workdir=None, poll_devices=True):
        """Protocol handler that handles all status and changes on PLM."""
        self._loop = loop
        self._connection_lost_callback = connection_lost_callback

        self._buffer = bytearray()
        self._recv_queue = deque([])
        self._send_queue = asyncio.Queue(loop=self._loop)
        self._acknak_queue = asyncio.Queue(loop=self._loop)
        self._aldb_response_queue = {}
        self._devices = LinkedDevices(loop, workdir)
        self._poll_devices = poll_devices
        self._write_transport_lock = asyncio.Lock(loop=self._loop)
        self._message_callbacks = MessageCallback()
        self._x10_address = None

        # Callback lists
        self._cb_load_all_link_db_done = []
        self._cb_device_not_active = []

        super().__init__(self, '000000', 0x03, None, None, '', '')

        self.log = logging.getLogger(__name__)
        self.transport = None

        self._register_message_handlers()

    # public properties
    @property
    def devices(self):
        """Return the list of devices linked to the IM."""
        return self._devices

    @property
    def loop(self):
        """Return the asyncio loop."""
        return self._loop

    @property
    def message_callbacks(self):
        """Return the list of message callbacks."""
        return self._message_callbacks

    # asyncio.protocol interface methods
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
                callbacks = \
                    self._message_callbacks.get_callbacks_from_message(msg)
                if hasattr(msg, 'isack') or hasattr(msg, 'isnak'):
                    self._acknak_queue.put_nowait(msg)
                if hasattr(msg, 'address'):
                    device = self.devices[msg.address.id]
                    if device:
                        device.receive_message(msg)
                for callback in callbacks:
                    self._loop.call_soon(callback, msg)
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

    # Methods used to trigger callbacks for specific events
    def add_device_callback(self, callback):
        """Register a callback for when a matching new device is seen."""
        self.devices.add_device_callback(callback)

    def add_all_link_done_callback(self, callback):
        """Register a callback to be invoked when the ALDB is loaded."""
        self.log.debug('Added new callback %s ',
                       callback)
        self._cb_load_all_link_db_done.append(callback)

    def add_device_not_active_callback(self, callback):
        """Register callback to be invoked when a device is not repsonding."""
        self.log.debug('Added new callback %s ',
                       callback)
        self._cb_device_not_active.append(callback)

    # Public methods
    def poll_devices(self):
        """Request status updates from each device."""
        for addr in self.devices:
            device = self.devices[addr]
            if not device.address.is_x10:
                device.async_refresh_state()

    def send_msg(self, msg, wait_nak=True, wait_timeout=WAIT_TIMEOUT):
        """Place a message on the send queue for sending.

        Message are sent in the order they are placed in the queue.
        """
        self.log.debug("Starting: send_msg")
        write_message_coroutine = self._write_message_from_send_queue()
        wait_info = {'msg': msg,
                     'wait_nak': wait_nak,
                     'wait_timeout': wait_timeout}
        self._send_queue.put_nowait(wait_info)
        asyncio.ensure_future(write_message_coroutine, loop=self._loop)
        self.log.debug("Ending: send_msg")

    def start_all_linking(self, mode, group):
        """Put the IM into All-Linking mode.

        Puts the IM into All-Linking mode for 4 minutes.

        Parameters:
            mode: 0 | 1 | 3 | 255
                  0 - PLM is responder
                  1 - PLM is controller
                  3 - Device that initiated All-Linking is Controller
                255 = Delete All-Link
            group: All-Link group number (0 - 255)
        """
        msg = StartAllLinking(mode, group)
        self.send_msg(msg)

    def add_x10_device(self, housecode, unitcode, feature='OnOff'):
        """Add an X10 device based on a feature description.

        Current features are:
        - OnOff
        - Dimmable
        """
        device = insteonplm.devices.create_x10(self, housecode,
                                               unitcode, feature)
        if device:
            self.devices[device.address.id] = device
        return device

    @asyncio.coroutine
    def _setup_devices(self):
        yield from self.devices.load_saved_device_info()
        self.log.debug('Found %d saved devices',
                       len(self.devices.saved_devices))
        self._get_plm_info()
        self.devices.add_known_devices(self)
        self._load_all_link_database()

    @asyncio.coroutine
    def _write_message_from_send_queue(self):
        if not self._write_transport_lock.locked():
            self.log.debug('Aquiring write lock')
            yield from self._write_transport_lock.acquire()
            while True:
                # wait for an item from the queue
                try:
                    with async_timeout.timeout(WAIT_TIMEOUT):
                        msg_info = yield from self._send_queue.get()
                        msg = msg_info.get('msg')
                        wait_nak = msg_info.get('wait_nak')
                        wait_timeout = msg_info.get('wait_timeout')
                except asyncio.TimeoutError:
                    self.log.debug('No new messages received.')
                    break
                # process the item
                self.log.debug('Writing message: %s', msg)
                write_bytes = msg.bytes
                if hasattr(msg, 'acknak') and msg.acknak:
                    write_bytes = write_bytes[:-1]
                self.transport.write(msg.bytes)
                if wait_nak:
                    self.log.debug('Waiting for ACK or NAK message')
                    is_nak = False
                    try:
                        with async_timeout.timeout(ACKNAK_TIMEOUT):
                            while True:
                                acknak = yield from self._acknak_queue.get()
                                if msg.matches_pattern(acknak):
                                    self.log.debug('ACK or NAK received')
                                    self.log.debug(acknak)
                                    is_nak = acknak.isnak
                                break
                    except asyncio.TimeoutError:
                        self.log.debug('No ACK or NAK message received.')
                        is_nak = True
                    if is_nak:
                        self._handle_nak(msg)
                yield from asyncio.sleep(wait_timeout, loop=self._loop)
            self._write_transport_lock.release()

    def _get_plm_info(self):
        """Request PLM Info."""
        self.log.info('Requesting PLM Info')
        msg = GetImInfo()
        self.send_msg(msg, wait_nak=True, wait_timeout=.5)

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
        self.send_msg(msg, wait_nak=True, wait_timeout=.5)
        self.log.debug("Ending: _get_first_all_link_record")

    def _get_next_all_link_record(self):
        """Request next ALL-Link record."""
        self.log.debug("Starting: _get_next_all_link_recor")
        self.log.debug("Requesting Next All-Link Record")
        msg = GetNextAllLinkRecord()
        self.send_msg(msg, wait_nak=True, wait_timeout=.5)
        self.log.debug("Ending: _get_next_all_link_recor")

    # Inbound message handlers sepcific to the IM
    def _register_message_handlers(self):
        template_assign_all_link = StandardReceive.template(
            commandtuple=COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE)
        template_all_link_response = AllLinkRecordResponse(None, None, None,
                                                           None, None, None)
        template_get_im_info = GetImInfo()
        template_next_all_link_rec = GetNextAllLinkRecord(acknak=MESSAGE_NAK)
        template_all_link_complete = AllLinkComplete(None, None, None,
                                                     None, None, None)
        template_x10_send = X10Send(None, None, MESSAGE_ACK)
        template_x10_received = X10Received(None, None)

        self._message_callbacks.add(
            template_assign_all_link,
            self._handle_assign_to_all_link_group)

        self._message_callbacks.add(
            template_all_link_response,
            self._handle_all_link_record_response)

        self._message_callbacks.add(
            template_get_im_info,
            self._handle_get_plm_info)

        self._message_callbacks.add(
            template_next_all_link_rec,
            self._handle_get_next_all_link_record_nak)

        self._message_callbacks.add(
            template_all_link_complete,
            self._handle_assign_to_all_link_group)

        self._message_callbacks.add(
            template_x10_send,
            self._handle_x10_send_receive)

        self._message_callbacks.add(
            template_x10_received,
            self._handle_x10_send_receive)

    def _peel_messages_from_buffer(self):
        self.log.debug("Starting: _peel_messages_from_buffer")
        lastlooplen = 0
        worktodo = True

        while worktodo:
            if len(self._buffer) == 0:
                worktodo = False
                break
            msg = insteonplm.messages.create(self._buffer)

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

    def _handle_assign_to_all_link_group(self, msg):
        cat = 0xff
        subcat = 0
        product_key = 0
        if msg.code == StandardReceive.code and msg.flags.isBroadcast:
            self.log.debug('Received broadcast ALDB group assigment request.')
            cat = msg.targetLow
            subcat = msg.targetMed
            product_key = msg.targetHi
            self._add_device_from_prod_data(msg.address, cat,
                                            subcat, product_key)
        elif msg.code == AllLinkComplete.code:
            if msg.linkcode in [0, 1, 3]:
                self.log.debug('Received ALDB complete response.')
                cat = msg.category
                subcat = msg.subcategory
                product_key = msg.firmware
                self._add_device_from_prod_data(msg.address, cat,
                                                subcat, product_key)
                self._update_aldb_records(msg.linkcode, msg.address, msg.group)
            else:
                self.log.debug('Received ALDB delete response.')
                self._update_aldb_records(msg.linkcode, msg.address, msg.group)

    def _add_device_from_prod_data(self, address, cat, subcat, product_key):
        self.log.debug('Received Device ID with address: %s  '
                       'cat: 0x%x  subcat: 0x%x', address, cat, subcat)
        device = self.devices.create_device_from_category(
            self, address, cat, subcat, product_key)
        if device:
            if self.devices[device.id] is None:
                self.devices[device.id] = device
                self.log.info('Device with id %s added to device list.',
                              device.id)
        else:
            self.log.error('Device %s not in the IPDB.',
                           Address(address).human)
        self.log.info('Total Devices Found: %d', len(self.devices))

    def _update_aldb_records(self, linkcode, address, group):
        """Refresh the IM and device ALDB records."""
        device = self.devices[Address(address).id]
        if device and device.aldb.status in [ALDBStatus.LOADED,
                                             ALDBStatus.PARTIAL]:
            for mem_addr in device.aldb:
                rec = device.aldb[mem_addr]
                if linkcode in [0, 1, 3]:
                    if rec.control_flags.is_high_water_mark:
                        self.log.info('Removing HWM recordd %04x', mem_addr)
                        device.aldb.pop(mem_addr)
                    elif not rec.control_flags.is_in_use:
                        self.log.info('Removing not in use recordd %04x',
                                      mem_addr)
                        device.aldb.pop(mem_addr)
                else:
                    if rec.address == self.address and rec.group == group:
                        self.log.info('Removing record %04x with addr %s and '
                                      'group %d', mem_addr, rec.address,
                                      rec.group)
                        device.aldb.pop(mem_addr)
            device.read_aldb()
            device.aldb.add_loaded_callback(self._refresh_aldb())

    def _refresh_aldb(self):
        self.aldb.clear()
        self._load_all_link_database()

    def _handle_standard_or_extended_message_received(self, msg):
        device = self.devices[msg.address.id]
        if device is not None:
            device.receive_message(msg)

    def _handle_all_link_record_response(self, msg):
        self.log.debug('Found all link record for device %s', msg.address.hex)
        cat = msg.linkdata1
        subcat = msg.linkdata2
        product_key = msg.linkdata3
        rec_num = len(self._aldb)
        self._aldb[rec_num] = ALDBRecord(rec_num, msg.controlFlags,
                                         msg.group, msg.address,
                                         cat, subcat, product_key)
        if self.devices[msg.address.id] is None:
            self.log.debug('Product data: address %s cat: %02x '
                           'subcat: %02x product_key: %02x',
                           msg.address.id, cat, subcat, product_key)

            # Get a device from the ALDB based on cat, subcat and product_key
            device = self.devices.create_device_from_category(
                self, msg.address, cat, subcat, product_key)

            # If a device is returned and that device is of a type tha stores
            # the product data in the ALDB record we can use that as the device
            # type for this record. Otherwise we need to request the device ID.
            if device is not None:
                if device.prod_data_in_aldb or \
                        self.devices.has_override(device.address.id) or \
                        self.devices.has_saved(device.address.id):
                    if self.devices[device.id] is None:
                        self.devices[device.id] = device
                        self.log.info('Device with id %s added to device list '
                                      'from ALDB data.',
                                      device.id)
        # Check again that the device is not alreay added, otherwise queue it
        # up for Get ID request
        if self.devices[msg.address.id] is None:
            unknowndevice = self.devices.create_device_from_category(
                self, msg.address.hex, None, None, None)
            self._aldb_response_queue[msg.address.id] = {
                'device': unknowndevice, 'retries': 0}

        self._get_next_all_link_record()

    def _handle_get_next_all_link_record_nak(self, msg):
        # When the last All-Link record is reached the PLM sends a NAK
        self._aldb.status = ALDBStatus.LOADED
        self.log.debug('All-Link device records found in ALDB: %d',
                       len(self._aldb_response_queue))

        # Remove records for devices found in the ALDB
        # or in previous calls to _handle_get_next_all_link_record_nak
        for addr in self.devices:
            try:
                self._aldb_response_queue.pop(addr)
            except KeyError:
                pass

        staleaddr = []
        for addr in self._aldb_response_queue:
            retries = self._aldb_response_queue[addr]['retries']
            if retries < 5:
                self._aldb_response_queue[addr]['device'].id_request()
                self._aldb_response_queue[addr]['retries'] = retries + 1
            else:
                self.log.warning('Device %s found in the ALDB not responding.',
                                 addr)
                self.log.warning('It is being removed from the device list. '
                                 'If this device')
                self.log.warning('is still active you can add it to the '
                                 'device_override')
                self.log.warning('configuration.')
                staleaddr.append(addr)

                for callback in self._cb_device_not_active:
                    callback(Address(addr))

        for addr in staleaddr:
            self._aldb_response_queue.pop(addr)

        num_devices_not_added = len(self._aldb_response_queue)

        if num_devices_not_added > 0:
            # Schedule _handle_get_next_all_link_record_nak to run again later
            # if some devices did not respond
            delay = num_devices_not_added * 3
            self._loop.call_later(delay,
                                  self._handle_get_next_all_link_record_nak,
                                  None)
        else:
            self.devices.save_device_info()
            while len(self._cb_load_all_link_db_done) > 0:
                callback = self._cb_load_all_link_db_done.pop()
                callback()
            if self._poll_devices:
                self._loop.call_soon(self.poll_devices)
        self.log.debug('Ending _handle_get_next_all_link_record_nak')

    def _handle_nak(self, msg):
        if msg.code == GetFirstAllLinkRecord.code or \
           msg.code == GetNextAllLinkRecord.code:
            return
        self.log.debug('No response or NAK message received for message')
        self.log.debug(msg)
        self.send_msg(msg)

    def _handle_get_plm_info(self, msg):
        from insteonplm.devices import ALDB
        self.log.debug('Starting _handle_get_plm_info')
        from insteonplm.devices.ipdb import IPDB
        ipdb = IPDB()
        self._address = msg.address
        self._cat = msg.category
        self._subcat = msg.subcategory
        self._product_key = msg.firmware
        product = ipdb[[self._cat, self._subcat]]
        self._description = product.description
        self._model = product.model
        self._aldb = ALDB(self._send_msg, self._plm.loop, self._address)

        self.log.debug('Ending _handle_get_plm_info')

    # X10 Device methods
    def x10_all_units_off(self, housecode):
        """Send the X10 All Units Off command."""
        if isinstance(housecode, str):
            housecode = housecode.upper()
        else:
            raise TypeError('Housecode must be a string')
        msg = X10Send.command_msg(housecode, X10_COMMAND_ALL_UNITS_OFF)
        self.send_msg(msg)
        self._x10_command_to_device(housecode, X10_COMMAND_ALL_UNITS_OFF, msg)

    def x10_all_lights_off(self, housecode):
        """Send the X10 All Lights Off command."""
        msg = X10Send.command_msg(housecode, X10_COMMAND_ALL_LIGHTS_OFF)
        self.send_msg(msg)
        self._x10_command_to_device(housecode, X10_COMMAND_ALL_LIGHTS_OFF, msg)

    def x10_all_lights_on(self, housecode):
        """Send the X10 All Lights Off command."""
        msg = X10Send.command_msg(housecode, X10_COMMAND_ALL_LIGHTS_ON)
        self.send_msg(msg)
        self._x10_command_to_device(housecode, X10_COMMAND_ALL_LIGHTS_ON, msg)

    def _handle_x10_send_receive(self, msg):
        housecode_byte, unit_command_byte = rawX10_to_bytes(msg.rawX10)
        housecode = byte_to_housecode(housecode_byte)
        if msg.flag == 0x00:
            unitcode = byte_to_unitcode(unit_command_byte)
            self._x10_address = Address.x10(housecode, unitcode)
            if self._x10_address:
                device = self.devices[self._x10_address.id]
                if device:
                    device.receive_message(msg)
        else:
            self._x10_command_to_device(housecode, unit_command_byte, msg)

    def _x10_command_to_device(self, housecode, command, msg):
        if isinstance(housecode, str):
            housecode = housecode.upper()
        else:
            raise TypeError('Housecode must be a string')
        if x10_command_type(command) == X10CommandType.DIRECT:
            if self._x10_address and self.devices[self._x10_address.id]:
                if self._x10_address.x10_housecode == housecode:
                    self.devices[self._x10_address.id].receive_message(msg)
        else:
            for id in self.devices:
                if self.devices[id].address.is_x10:
                    if (self.devices[id].address.x10_housecode == housecode):
                        self.devices[id].receive_message(msg)
        self._x10_address = None


class PLM(IM):
    """Insteon PowerLinc Modem device.

        This class is expected to be wrapped inside a Connection class object
        which will maintain the socket and handle auto-reconnects.

            :param connection_lost_callback:
                called when connection is lost to device (optional)
            :param loop:
                asyncio event loop (optional)
            :param workdir:
                Working directory name to save device information (optional)

            :type: connection_lost_callback:
                callable
            :type loop:
                asyncio.loop
            :type workdir:
                string - valid directory path
    """


class Hub(IM):
    """Insteon Hub device.

        This class is expected to be wrapped inside a Connection class object
        which will maintain the socket and handle auto-reconnects.

            :param connection_lost_callback:
                called when connection is lost to device (optional)
            :param loop:
                asyncio event loop (optional)
            :param workdir:
                Working directory name to save device information (optional)

            :type: connection_lost_callback:
                callable
            :type loop:
                asyncio.loop
            :type workdir:
                string - valid directory path
    """
