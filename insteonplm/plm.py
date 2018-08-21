"""Module to maintain PLM state information and network interface."""

import asyncio
import logging
import binascii
from collections import deque, namedtuple

import async_timeout

import insteonplm.messages
from insteonplm.constants import (MESSAGE_ACK,
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
from insteonplm.messages.setImConfiguration import SetIMConfiguration
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


MessageInfo = namedtuple('MessageInfo', 'msg wait_nak wait_timeout')


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
                 workdir=None, poll_devices=True, load_aldb=True):
        """Protocol handler that handles all status and changes on PLM."""
        self._loop = loop
        self._connection_lost_callback = connection_lost_callback

        self._buffer = asyncio.Queue(loop=self._loop)
        self._recv_queue = deque([])
        self._send_queue = asyncio.Queue(loop=self._loop)
        self._acknak_queue = asyncio.Queue(loop=self._loop)
        self._next_all_link_rec_nak_retries = 0
        self._aldb_devices = {}
        self._devices = LinkedDevices(loop, workdir)
        self._poll_devices = poll_devices
        self._load_aldb = load_aldb
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
        self._quick_start = False
        self._writer_task = None
        self._restart_writer = False
        self.resume_writing()

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
        raise NotImplementedError

    def data_received(self, data):
        """Called when asyncio.Protocol detects received data from network."""
        self.log.debug("Starting: data_received")
        self.log.debug('Received %d bytes from PLM: %s',
                       len(data), binascii.hexlify(data))
        self._buffer.put_nowait(data)
        asyncio.ensure_future(self._peel_messages_from_buffer(),
                              loop=self._loop)

        self.log.debug("Finishing: data_received")

    def connection_lost(self, exc):
        """Called when asyncio.Protocol loses the network connection."""
        if exc is None:
            self.log.warning('eof from modem?')
        else:
            self.log.warning('Lost connection to modem: %s', exc)

        self.transport = None
        asyncio.ensure_future(self.pause_writing(), loop=self.loop)

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
        msg_info = MessageInfo(msg=msg, wait_nak=wait_nak,
                               wait_timeout=wait_timeout)
        self.log.debug("Queueing msg: %s", msg)
        self._send_queue.put_nowait(msg_info)

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
        - Sensor
        - AllUnitsOff
        - AllLightsOn
        - AllLightsOff
        """
        device = insteonplm.devices.create_x10(self, housecode,
                                               unitcode, feature)
        if device:
            self.devices[device.address.id] = device
        return device

    def monitor_mode(self):
        """Put the Insteon Modem in monitor mode."""
        msg = SetIMConfiguration(0x40)
        self.send_msg(msg)

    def device_not_active(self, addr):
        """Handle inactive devices."""
        self.aldb_device_handled(addr)
        for callback in self._cb_device_not_active:
            callback(addr)

    def aldb_device_handled(self, addr):
        """Remove device from ALDB device list."""
        if isinstance(addr, Address):
            remove_addr = addr.id
        else:
            remove_addr = addr
        try:
            self._aldb_devices.pop(remove_addr)
            self.log.debug('Removed ALDB device %s', remove_addr)
        except KeyError:
            self.log.debug('Device %s not in ALDB device list', remove_addr)
        self.log.debug('ALDB device count: %d', len(self._aldb_devices))

    @asyncio.coroutine
    def pause_writing(self):
        """Pause writing."""
        self._restart_writer = False
        if self._writer_task:
            self._writer_task.remove_done_callback(self.resume_writing)
            self._writer_task.cancel()
            yield from self._writer_task
            yield from asyncio.sleep(0, loop=self._loop)

    def resume_writing(self, task=None):
        """Resume writing."""
        if self._restart_writer:
            self._writer_task = asyncio.ensure_future(
                self._get_message_from_send_queue(), loop=self._loop)
            self._writer_task.add_done_callback(self.resume_writing)

    @asyncio.coroutine
    def close(self):
        """Close all writers for all devices for a clean shutdown."""
        yield from self.pause_writing()
        yield from asyncio.sleep(0, loop=self._loop)

    @asyncio.coroutine
    def _setup_devices(self):
        yield from self.devices.load_saved_device_info()
        self.log.debug('Found %d saved devices',
                       len(self.devices.saved_devices))
        self._get_plm_info()
        self.devices.add_known_devices(self)
        if self._quick_start:
            self._complete_setup()
        else:
            self._load_all_link_database()
        self.log.debug('Ending _setup_devices in IM')

    @asyncio.coroutine
    def _get_message_from_send_queue(self):
        self.log.debug('Starting PLM write message from send queue')
        if self._write_transport_lock.locked():
            return
        self.log.debug('Aquiring write lock')
        yield from self._write_transport_lock.acquire()
        while self._restart_writer:
            # wait for an item from the queue
            try:
                msg_info = yield from self._send_queue.get()
                message_sent = False
                while not message_sent:
                    message_sent = yield from self._write_message(msg_info)
                yield from asyncio.sleep(msg_info.wait_timeout,
                                         loop=self._loop)
            except asyncio.CancelledError:
                self.log.error('Stopping Insteon Modem writer due to CancelledError')
                self._restart_writer = False
            except GeneratorExit:
                self.log.error('Stopping Insteon Modem writer due to GeneratorExit')
                self._restart_writer = False
            except Exception as e:
                self.log.error('Stopping Insteon Modem writer due to %s', str(e))
                self._restart_writer = False
        if self._write_transport_lock.locked():
            self._write_transport_lock.release()
        self.log.debug('Ending PLM write message from send queue')

    def _get_plm_info(self):
        """Request PLM Info."""
        self.log.info('Requesting PLM Info')
        msg = GetImInfo()
        self.send_msg(msg, wait_nak=True, wait_timeout=.5)

    @asyncio.coroutine
    def _write_message(self, msg_info: MessageInfo):
        self.log.debug('TX: %s', msg_info.msg)
        is_sent = False
        if not self.transport.is_closing():
            self.transport.write(msg_info.msg.bytes)
            if msg_info.wait_nak:
                self.log.debug('Waiting for ACK or NAK message')
                is_sent = yield from self._wait_ack_nak(msg_info.msg)
                #if not is_sent:
                #    self._handle_nak(msg_info)
            else:
                is_sent = True
        else:
            self.log.debug("Transport is not open, waiting 5 seconds")
            is_sent = False
            yield from asyncio.sleep(5, loop=self._loop)
        return is_sent

    @asyncio.coroutine
    def _wait_ack_nak(self, msg):
        is_sent = False
        is_ack_nak = False
        try:
            with async_timeout.timeout(ACKNAK_TIMEOUT):
                while not is_ack_nak:
                    acknak = yield from self._acknak_queue.get()
                    is_ack_nak = self._msg_is_ack_nak(msg, acknak)
                    is_sent = self._msg_is_sent(acknak)
        except asyncio.TimeoutError:
            self.log.debug('No ACK or NAK message received.')
            is_sent = False
        return is_sent

    def _msg_is_ack_nak(self, msg, acknak):
        if not hasattr(acknak, 'isack'):
            return False
        if msg.matches_pattern(acknak):
            self.log.debug('ACK or NAK received')
            return True
        return False

    def _msg_is_sent(self, acknak):
        # All Link record NAK is a valid last record response
        # However, we want to retry 3 times to make sure
        # it is a valid last record response and not a true NAK
        if ((acknak.code == GetFirstAllLinkRecord.code or
                acknak.code == GetNextAllLinkRecord.code) and
                acknak.isnak):
            return True

        return acknak.isack

    def _load_all_link_database(self):
        """Load the ALL-Link Database into object."""
        self.log.debug("Starting: _load_all_link_database")
        self.devices.state = 'loading'
        self._next_all_link_rec_nak_retries = 0
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
        self.log.debug("Starting: _get_next_all_link_record")
        self.log.debug("Requesting Next All-Link Record")
        msg = GetNextAllLinkRecord()
        self.send_msg(msg, wait_nak=True, wait_timeout=.5)
        self.log.debug("Ending: _get_next_all_link_record")

    def _new_device_added(self, device):
        self.aldb_device_handled(device.address.id)
        if self._poll_devices:
            device.async_refresh_state()

    # Inbound message handlers sepcific to the IM
    def _register_message_handlers(self):
        template_all_link_response = AllLinkRecordResponse(None, None, None,
                                                           None, None, None)
        template_get_im_info = GetImInfo()
        template_next_all_link_rec = GetNextAllLinkRecord(acknak=MESSAGE_NAK)
        template_x10_send = X10Send(None, None, MESSAGE_ACK)
        template_x10_received = X10Received(None, None)

        # self._message_callbacks.add(
        #    template_assign_all_link,
        #    self._handle_assign_to_all_link_group)

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
            template_x10_send,
            self._handle_x10_send_receive)

        self._message_callbacks.add(
            template_x10_received,
            self._handle_x10_send_receive)

    @asyncio.coroutine
    def _peel_messages_from_buffer(self):
        lastlooplen = 0
        worktodo = True
        buffer = bytearray()
        while worktodo:
            buffer.extend(self._unpack_buffer())
            if len(buffer) < 2:
                worktodo = False
                break
            self.log.debug('Total buffer: %s', binascii.hexlify(buffer))
            msg, buffer = insteonplm.messages.create(buffer)

            if msg is not None:
                # self.log.debug('Msg buffer: %s', msg.hex)
                self._recv_queue.appendleft(msg)

            # self.log.debug('Post buffer: %s', binascii.hexlify(buffer))
            if len(buffer) < 2:
                self.log.debug('Buffer too short to have a message')
                worktodo = False
                break

            if len(buffer) == lastlooplen:
                self.log.debug("Buffer size did not change wait for more data")
                worktodo = False
                break

            lastlooplen = len(buffer)
        if len(buffer) > 0:
            buffer.extend(self._unpack_buffer())
            self._buffer.put_nowait(buffer)

        self.log.debug('Messages in queue: %d', len(self._recv_queue))
        worktodo = True
        while worktodo:
            try:
                msg = self._recv_queue.pop()
                self.log.debug('RX: %s', msg)
                callbacks = \
                    self._message_callbacks.get_callbacks_from_message(msg)
                if hasattr(msg, 'isack') or hasattr(msg, 'isnak'):
                    self._acknak_queue.put_nowait(msg)
                if hasattr(msg, 'address'):
                    device = self.devices[msg.address.hex]
                    if device:
                        device.receive_message(msg)
                    else:
                        try:
                            device = self._aldb_devices[msg.address.id]
                            device.receive_message(msg)
                        except KeyError:
                            pass
                for callback in callbacks:
                    self._loop.call_soon(callback, msg)
            except IndexError:
                self.log.debug('Last item in self._recv_queue reached.')
                worktodo = False

    def _unpack_buffer(self):
        buffer = bytearray()
        while not self._buffer.empty():
            buffer.extend(self._buffer.get_nowait())
        return buffer

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
            self.log.debug('ALDB Data: address %s data1: %02x '
                           'data1: %02x data3: %02x',
                           msg.address.hex, cat, subcat, product_key)

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

        # Check again that the device is not already added, otherwise queue it
        # up for Get ID request
        if not self.devices[msg.address.id]:
            self.log.debug('Found new device %s', msg.address.id)
            unknowndevice = self.devices.create_device_from_category(
                self, msg.address.hex, None, None, None)
            self._aldb_devices[msg.address.id] = unknowndevice

        self._next_all_link_rec_nak_retries = 0
        self._get_next_all_link_record()

    def _handle_get_next_all_link_record_nak(self, msg):
        # When the last All-Link record is reached the PLM sends a NAK
        if self._next_all_link_rec_nak_retries < 3:
            self._next_all_link_rec_nak_retries += 1
            self._get_next_all_link_record()
            return
        self._aldb.status = ALDBStatus.LOADED
        self.log.debug('All-Link device records found in ALDB: %d',
                       len(self._aldb_devices))

        while self._cb_load_all_link_db_done:
            callback = self._cb_load_all_link_db_done.pop()
            callback()

        self._get_device_info()

    def _get_device_info(self):
        self.log.debug('Starting _get_device_info')
        # Remove saved records for devices found in the ALDB
        for addr in self.devices:
            self.aldb_device_handled(addr)

        self._complete_setup()

        self.devices.add_device_callback(self._new_device_added)

        for addr in self._aldb_devices:
            self.log.debug('Getting device info for %s', Address(addr).human)
            self._aldb_devices[addr].id_request()

        self.log.debug('Ending _get_device_info')

    def _complete_setup(self):
        self.devices.save_device_info()
        if self._poll_devices:
            self._loop.call_soon(self.poll_devices)

    def _handle_nak(self, msg_info):
        if msg_info.msg.code == GetFirstAllLinkRecord.code or \
           msg_info.msg.code == GetNextAllLinkRecord.code:
            return
        self.log.debug('No response or NAK message received')
        self.send_msg(msg_info.msg, msg_info.wait_nak, msg_info.wait_timeout)

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

    # asyncio.protocol interface methods
    def connection_made(self, transport):
        """Called when asyncio.Protocol establishes the network connection."""
        self.log.info('Connection established to PLM')
        self.transport = transport

        self._restart_writer = True
        self.resume_writing()

        # Testing to see if this fixes the 2413S issue
        self.transport.serial.timeout = 1
        self.transport.serial.write_timeout = 1
        self.transport.set_write_buffer_limits(128)
        # limit = self.transport.get_write_buffer_size()
        # self.log.debug('Write buffer size is %d', limit)
        coro = self._setup_devices()
        asyncio.ensure_future(coro, loop=self._loop)


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

    # asyncio.protocol interface methods
    def connection_made(self, transport):
        """Called when asyncio.Protocol establishes the network connection."""
        self.log.info('Connection established to Hub')
        self.log.debug('Transport: %s', transport)
        self.transport = transport

        self._restart_writer = True
        self.resume_writing()

        coro = self._setup_devices()
        asyncio.ensure_future(coro, loop=self._loop)
