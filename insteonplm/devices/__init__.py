"""Insteon Device Classes."""
# pylint: disable=too-many-lines
import asyncio
from collections import namedtuple
from concurrent.futures import CancelledError
import datetime
from enum import Enum
import logging

import async_timeout

from insteonplm.address import Address
from insteonplm.constants import (
    COMMAND_ID_REQUEST_0X10_0X00,
    COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00,
    COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
    COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE,
    COMMAND_FX_USERNAME_0X03_0X01,
    COMMAND_ENTER_LINKING_MODE_0X09_NONE,
    COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE,
    COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00,
    COMMAND_PING_0X0F_0X00,
    COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
    MESSAGE_ACK,
    MESSAGE_TYPE_BROADCAST_MESSAGE,
    MESSAGE_TYPE_DIRECT_MESSAGE,
    MESSAGE_FLAG_DIRECT_MESSAGE_NAK_0XA0,
    MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50,
    MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51
)
from insteonplm.messagecallback import MessageCallback
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.userdata import Userdata
from insteonplm.states import State

_LOGGER = logging.getLogger(__name__)
DIRECT_ACK_WAIT_TIMEOUT = 3
ALDB_RECORD_TIMEOUT = 10
ALDB_RECORD_RETRIES = 20
ALDB_ALL_RECORD_TIMEOUT = 30
ALDB_ALL_RECORD_RETRIES = 5


LoadAction = namedtuple('LoadAction', 'mem_addr rec_count retries')
DeviceInfo = namedtuple('DeviceInfo', 'address cat subcat firmware')


# pylint: disable=unused-argument
# pylint: disable=cyclic-import
def create(plm, address, cat, subcat, firmware=None):
    """Create a device from device info data."""
    from insteonplm.devices.ipdb import IPDB
    ipdb = IPDB()
    product = ipdb[[cat, subcat]]
    deviceclass = product.deviceclass
    device = None
    if deviceclass is not None:
        device = deviceclass(plm, address, cat, subcat,
                             product.product_key,
                             product.description,
                             product.model)
    return device


def create_x10(plm, housecode, unitcode, feature):
    """Create an X10 device from a feature definition."""
    from insteonplm.devices.ipdb import IPDB
    ipdb = IPDB()
    product = ipdb.x10(feature)
    deviceclass = product.deviceclass
    device = None
    if deviceclass:
        device = deviceclass(plm, housecode, unitcode)
    return device


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
class Device():
    """INSTEON Device Class."""

    def __init__(self, plm, address, cat, subcat, product_key=0x00,
                 description='', model=''):
        """Init the Device class."""
        self._plm = plm
        self._address = Address(address)
        self._cat = cat
        self._subcat = subcat
        if self._subcat is None:
            self._subcat = 0x00
        self._product_key = product_key
        if self._product_key is None:
            self._product_key = 0x00
        self._description = description
        self._model = model

        self._last_communication_received = datetime.datetime(1, 1, 1, 1, 1, 1)
        self._product_data_in_aldb = False
        self._stateList = StateList()
        self._sent_msg_wait_for_directACK = {}
        self._message_callbacks = MessageCallback()
        self._aldb = ALDB(self._send_msg, self._plm.loop, self._address)

        self._recent_messages = asyncio.Queue(loop=self._plm.loop)
        self._send_msg_queue = asyncio.Queue(loop=self._plm.loop)
        self._directACK_received_queue = asyncio.Queue(loop=self._plm.loop)
        self._device_info_queue = asyncio.Queue(loop=self._plm.loop)
        self._send_msg_lock = asyncio.Lock(loop=self._plm.loop)
        self._setup_default_links_lock = asyncio.Lock(loop=self._plm.loop)
        self._device_info_retries = 0
        self._all_link_complete_callback = None

        self._register_messages()

    # Public properties
    @property
    def address(self):
        """Return the INSTEON device address."""
        return self._address

    @property
    def cat(self):
        """Return the INSTEON device category."""
        return self._cat

    @property
    def subcat(self):
        """Return the INSTEON device subcategory."""
        return self._subcat

    @property
    def product_key(self):
        """Return the INSTEON product key."""
        return self._product_key

    @property
    def description(self):
        """Return the INSTEON device description."""
        return self._description

    @property
    def model(self):
        """Return the INSTEON device model number."""
        return self._model

    @property
    def id(self):
        """Return the ID of the device."""
        return self._address.id

    @property
    def states(self):
        """Return the device states/groups."""
        return self._stateList

    @property
    def prod_data_in_aldb(self):
        """Return if the PLM use the ALDB data to setup the device.

        True if Product data (cat, subcat) is stored in the PLM ALDB.
        False if product data must be acquired via a Device ID message or from
        a Product Data Request command.

        The method of linking determines if product data in the ALDB,
        therefore False is the default. The common reason to store product data
        in the ALDB is for one way devices or battery opperated devices where
        the ability to send a command request is limited.
        """
        return self._product_data_in_aldb

    @property
    def aldb(self):
        """Return the device All-Link Database."""
        return self._aldb

    # Public Methods
    def async_refresh_state(self):
        """Request each state to provide status update."""
        for state in self._stateList:
            self._stateList[state].async_refresh_state()

    def id_request(self):
        """Request a device ID from a device."""
        import inspect
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        _LOGGER.debug('caller name: %s', calframe[1][3])
        msg = StandardSend(self.address, COMMAND_ID_REQUEST_0X10_0X00)
        self._plm.send_msg(msg)

    def product_data_request(self):
        """Request product data from a device.

        Not supported by all devices.
        Required after 01-Feb-2007.
        """
        msg = StandardSend(self._address,
                           COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00)
        self._send_msg(msg)

    def assign_to_all_link_group(self, group=0x01):
        """Assign a device to an All-Link Group.

        The default is group 0x01.
        """
        msg = StandardSend(self._address,
                           COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
                           cmd2=group)
        self._send_msg(msg)

    def delete_from_all_link_group(self, group):
        """Delete a device to an All-Link Group."""
        msg = StandardSend(self._address,
                           COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE,
                           cmd2=group)
        self._send_msg(msg)

    def fx_username(self):
        """Get FX Username.

        Only required for devices that support FX Commands.
        FX Addressee responds with an ED 0x0301 FX Username Response message
        """
        msg = StandardSend(self._address, COMMAND_FX_USERNAME_0X03_0X01)
        self._send_msg(msg)

    def device_text_string_request(self):
        """Get FX Username.

        Only required for devices that support FX Commands.
        FX Addressee responds with an ED 0x0301 FX Username Response message.
        """
        msg = StandardSend(self._address, COMMAND_FX_USERNAME_0X03_0X01)
        self._send_msg(msg)

    def enter_linking_mode(self, group=0x01):
        """Tell a device to enter All-Linking Mode.

        Same as holding down the Set button for 10 sec.
        Default group is 0x01.

        Not supported by i1 devices.
        """
        msg = ExtendedSend(self._address,
                           COMMAND_ENTER_LINKING_MODE_0X09_NONE,
                           cmd2=group,
                           userdata=Userdata())
        msg.set_checksum()
        self._send_msg(msg)

    def enter_unlinking_mode(self, group):
        """Unlink a device from an All-Link group.

        Not supported by i1 devices.
        """
        msg = StandardSend(self._address,
                           COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE,
                           cmd2=group)
        self._send_msg(msg)

    def get_engine_version(self):
        """Get the device engine version."""
        msg = StandardSend(self._address,
                           COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00)
        self._send_msg(msg)

    def ping(self):
        """Ping a device."""
        msg = StandardSend(self._address, COMMAND_PING_0X0F_0X00)
        self._send_msg(msg)

    def create_default_links(self):
        """Create the default links between the IM and the device."""
        self._plm.manage_aldb_record(0x40, 0xe2, 0x00, self.address,
                                     self.cat, self.subcat, self.product_key)
        self.manage_aldb_record(0x41, 0xa2, 0x00, self._plm.address,
                                self._plm.cat, self._plm.subcat,
                                self._plm.product_key)
        for link in self._stateList:
            state = self._stateList[link]
            if state.is_responder:
                # IM is controller
                self._plm.manage_aldb_record(0x40, 0xe2, link, self._address,
                                             0x00, 0x00, 0x00)
                # Device is responder
                self.manage_aldb_record(0x41, 0xa2, link, self._plm.address,
                                        state.linkdata1, state.linkdata2,
                                        state.linkdata3)
            if state.is_controller:
                # IM is responder
                self._plm.manage_aldb_record(0x41, 0xa2, link, self._address,
                                             0x00, 0x00, 0x00)
                # Device is controller
                self.manage_aldb_record(0x40, 0xe2, link, self._plm.address,
                                        0x00, 0x00, 0x00)
        self.read_aldb()

    def read_aldb(self, mem_addr=0x0000, num_recs=0):
        """Read the device All-Link Database."""
        if self._aldb.version == ALDBVersion.Null:
            _LOGGER.info('Device %s does not contain an All-Link Database',
                         self._address.human)
        else:
            _LOGGER.info('Reading All-Link Database for device %s',
                         self._address.human)
            asyncio.ensure_future(self._aldb.load(mem_addr, num_recs),
                                  loop=self._plm.loop)
            self._aldb.add_loaded_callback(self._aldb_loaded_callback)

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    def manage_aldb_record(self, control_code, control_flags, group, address,
                           data1, data2, data3):
        """Update an IM All-Link record.

        Control Code values:
        - 0x00 Find First Starting at the top of the ALDB, search for the
        first ALL-Link Record matching the <ALL-Link Group> and <ID> in bytes
        5 – 8. The search ignores byte 4, <ALL-Link Record Flags>. You will
        receive an ACK at the end of the returned message if such an ALL-Link
        Record exists, or else a NAK if it doesn’t.  If the record exists, the
        IM will return it in an ALL-Link Record Response (0x51) message.

        - 0x01 Find Next Search for the next ALL-Link Record following the one
        found using <Control Code> 0x00 above.  This allows you to find both
        Controller and Responder records for a given <ALL-Link Group> and
        <ID>. Be sure to use the same <ALL-Link Group> and <ID> (bytes 5 – 8)
        as you used for <Control Code> 0x00. You will receive an ACK at the
        end of the returned message if another matching ALL-Link Record
        exists, or else a NAK if it doesn’t.  If the record exists, the IM
        will return it in an ALL-Link Record Response (0x51) message.

        - 0x20 Modify First Found or Add Modify an existing or else add a new
        ALL-Link Record for either a Controller or Responder. Starting at the
        top of the ALDB, search for the first ALL-Link Record matching the
        <ALL-Link Group> and <ID> in bytes 5 – 8.  The search ignores byte 4,
        <ALL-Link Record Flags>. If such an ALL-Link Record exists, overwrite
        it with the data in bytes 4 – 11; otherwise, create a new ALL-Link
        Record using bytes 4 – 11. Note that the IM will copy
        <ALL-Link Record Flags> you supplied in byte 4 below directly into the
        <ALL-Link Record Flags> byte of the ALL-Link Record in an ALDB-L
        (linear) database.  Use caution, because you can damage an ALDB-L if
        you misuse this Command.  For instance, if you zero the
        <ALL-Link Record Flags> byte in the first ALL-Link Record, the IM’s
        ALDB-L database will then appear empty.

        - 0x40 Modify First Controller Found or Add Modify an existing or else
        add a new Controller (master) ALL-Link Record. Starting at the top of
        the ALDB, search for the first ALL-Link Controller Record matching the
        <ALL-Link Group> and <ID> in bytes 5 – 8.  An ALL-Link Controller
        Record has bit 6 of its <ALL-Link Record Flags> byte set to 1. If such
        a Controller ALL-Link Record exists, overwrite it with the data in
        bytes 5 – 11; otherwise, create a new ALL-Link Record using bytes
        5 – 11.  In either case, the IM will set bit 6 of the
        <ALL-Link Record Flags> byte in the ALL-Link Record to 1 to indicate
        that the record is for a Controller.

        - 0x41 Modify First Responder Found or Add Modify an existing or else
        add a new Responder (slave) ALLLink Record. Starting at the top of the
        ALDB, search for the first ALL-Link Responder Record matching the
        <ALL-Link Group> and <ID> in bytes 5 – 8.  An ALL-Link Responder
        Record has bit 6 of its <ALL-Link Record Flags> byte cleared to 0. If
        such a Responder ALL-Link Record exists, overwrite it with the data in
        bytes 5 – 11; otherwise, create a new ALL-Link Record using bytes
        5 – 11.  In either case, The IM will clear bit 6 of the
        <ALL-Link Record Flags> byte in the ALL-Link Record to 0 to indicate
        that the record is for a Responder.

        - 0x80 Delete First Found Delete an ALL-Link Record. Starting at the
        top of the ALDB, search for the first ALL-Link Record matching the
        <ALL-Link Group> and <ID> in bytes 5 – 8.  The search ignores byte 4,
        <ALL-Link Record Flags>. You will receive an ACK at the end of the
        returned message if such an ALL-Link Record existed and was deleted,
        or else a NAK no such record exists.
        """
        found_first = False
        for memaddr in self.aldb:
            found = False
            rec = self.aldb[memaddr]
            found = Address(address) == rec.address
            found = found & int(group) == rec.group
            if control_code == 0x00:
                if found:
                    return (True, rec)
                if rec.control_flags.is_high_water_mark:
                    return (False, None)
            if control_code == 0x01:
                if found & found_first:
                    return (True, rec)
                if rec.control_flags.is_high_water_mark:
                    return (False, None)
                if found:
                    found_first = True
            elif control_code == 0x20:
                if found or rec.control_flags.is_high_water_mark:
                    new_rec = self._write_new_aldb_rec(
                        rec.mem_addr, control_flags, group, address,
                        data1, data2, data3)
                    return (found, new_rec)
            elif control_code == 0x40:
                found = found & rec.control_flags.is_controller
                if found or rec.control_flags.is_high_water_mark:
                    new_rec = self._write_new_aldb_rec(
                        rec.mem_addr, control_flags, group, address,
                        data1, data2, data3)
                    return (found, new_rec)
            elif control_code == 0x41:
                found = found & rec.control_flags.is_responder
                if found or rec.control_flags.is_high_water_mark:
                    new_rec = self._write_new_aldb_rec(
                        rec.mem_addr, control_flags, group, address,
                        data1, data2, data3)
                    return (found, new_rec)
            elif control_code == 0x80:
                if found:
                    cf = rec.control_flags
                    new_control_flags = ControlFlags(False, cf.is_controller,
                                                     cf.is_high_water_mark,
                                                     False, False)
                    new_rec = self._write_new_aldb_rec(
                        rec.mem_addr, new_control_flags, rec.group,
                        rec.address, rec.data1, rec.data2, rec.data3)
                    return (found, new_rec)
            return (False, rec)

    def _write_new_aldb_rec(self, mem_addr: int, mode: str, group: int, target,
                            data1=0x00, data2=0x00, data3=0x00):
        new_rec = ALDBRecord(mem_addr, mode, group, target,
                             data1, data2, data3)
        self.write_aldb(new_rec.mem_addr, new_rec.control_flags, new_rec.group,
                        new_rec.address, new_rec.data1, new_rec.data2,
                        new_rec.data3)
        return new_rec

    def write_aldb(self, mem_addr: int, mode: str, group: int, target,
                   data1=0x00, data2=0x00, data3=0x00):
        """Write to the device All-Link Database.

        Parameters:
            Required:
            mode:   r - device is a responder of target
                    c - device is a controller of target
            group:  Link group
            target: Address of the other device

            Optional:
            data1:  Device dependant
            data2:  Device dependant
            data3:  Device dependant

        """
        if isinstance(mode, str) and mode.lower() in ['c', 'r']:
            pass
        else:
            _LOGGER.error('Insteon link mode: %s', mode)
            raise ValueError("Mode must be 'c' or 'r'")
        if isinstance(group, int):
            pass
        else:
            raise ValueError("Group must be an integer")

        target_addr = Address(target)

        _LOGGER.debug('calling aldb write_record')
        self._aldb.write_record(mem_addr, mode, group, target_addr,
                                data1, data2, data3)
        self._aldb.add_loaded_callback(self._aldb_loaded_callback)

    def del_aldb(self, mem_addr: int):
        """Delete an All-Link Database record."""
        self._aldb.del_record(mem_addr)
        self._aldb.add_loaded_callback(self._aldb_loaded_callback)

    def _handle_aldb_record_received(self, msg):
        self._aldb.record_received(msg)

    # pylint: disable=unused-argument
    def _handle_pre_nak(self, msg):
        _LOGGER.warning('Device %s returned a pre-NAK message',
                        self._address.human)
        _LOGGER.warning('Checking status to confirm if message was processed')
        self.async_refresh_state()

    def _handle_get_device_info_ack(self, msg):
        _LOGGER.debug('Starting _handle_get_device_info_ack with message:')
        _LOGGER.debug(msg)
        asyncio.ensure_future(self._wait_device_info(msg), loop=self._plm.loop)

    def _handle_assign_to_all_link_group(self, msg):
        cat = 0xff
        subcat = 0
        product_key = 0
        if msg.code == StandardReceive.code and msg.flags.isBroadcast:
            _LOGGER.debug('Received broadcast ALDB group assigment request.')
            cat = msg.targetLow
            subcat = msg.targetMed
            product_key = msg.targetHi
            self._add_device_from_prod_data(msg.address, cat,
                                            subcat, product_key)
        elif msg.code == AllLinkComplete.code:
            if msg.linkcode in [0, 1, 3]:
                _LOGGER.debug('Received ALDB complete response.')
                cat = msg.category
                subcat = msg.subcategory
                product_key = msg.firmware
                self._add_device_from_prod_data(msg.address, cat,
                                                subcat, product_key)
            else:
                _LOGGER.debug('Received ALDB delete response.')
            self._refresh_aldb_records(msg.linkcode, msg.address, msg.group)

    def _add_device_from_prod_data(self, address, cat, subcat, product_key):
        _LOGGER.debug('Received Device ID with address: %s  '
                      'cat: 0x%x  subcat: 0x%x', address, cat, subcat)
        device = self._plm.devices.create_device_from_category(
            self._plm, address, cat, subcat, product_key)
        if device:
            if not self._plm.devices[device.id]:
                self._plm.devices[device.id] = device
                _LOGGER.debug('Device with id %s added to device list.',
                              device.id)
            _LOGGER.info('Total Insteon devices found: %d',
                         len(self._plm.devices))
            self._plm.aldb_device_handled(self._address)
            self._plm.devices.save_device_info()
        else:
            _LOGGER.warning('Device %s not in the Insteon Product Database',
                            Address(address).human)
            self._plm.device_not_active(self.address)

    def _refresh_aldb_records(self, linkcode, address, group):
        """Refresh the IM and device ALDB records."""
        if self.aldb.status in [ALDBStatus.LOADED, ALDBStatus.PARTIAL]:
            for mem_addr in self.aldb:
                rec = self.aldb[mem_addr]
                if linkcode in [0, 1, 3]:
                    if rec.control_flags.is_high_water_mark:
                        _LOGGER.debug('Removing HWM record %04x', mem_addr)
                        self.aldb.pop(mem_addr)
                    elif not rec.control_flags.is_in_use:
                        _LOGGER.debug('Removing not in use record %04x',
                                      mem_addr)
                        self.aldb.pop(mem_addr)
                else:
                    if rec.address == self.address and rec.group == group:
                        _LOGGER.debug('Removing record %04x with addr %s and '
                                      'group %d', mem_addr, rec.address,
                                      rec.group)
                        self.aldb.pop(mem_addr)
            self.read_aldb()
            # self.aldb.add_loaded_callback(self._refresh_aldb)

    async def _wait_device_info(self, msg):
        _LOGGER.debug('Starting _wait_device_info for device %s in %s',
                      msg.address.human, self._address.human)
        try:
            with async_timeout.timeout(6):
                device_info_msg = await self._device_info_queue.get()
                _LOGGER.debug('_wait_device_info got device_id message %s',
                              device_info_msg)
        except asyncio.TimeoutError:
            _LOGGER.debug('_wait_device_info timed out for message %s in %s',
                          msg.address.human, self._address.human)
            if self._device_info_retries < 5:
                self._device_info_retries += 1
                _LOGGER.debug('Device %s id_request retry %d',
                              self.address.human, self._device_info_retries)
                self.id_request()
            else:
                _LOGGER.warning('Device %s did not respond to an ID request',
                                self.address.human)
                _LOGGER.warning('Use a device override to define the device '
                                'type')
                self._plm.device_not_active(self.address)
            return
        self._device_info_retries = 0
        address = device_info_msg.address
        cat = device_info_msg.targetLow
        subcat = device_info_msg.targetMed
        product_key = device_info_msg.targetHi
        self._add_device_from_prod_data(address, cat, subcat, product_key)

    def _handle_device_info_response(self, msg):
        _LOGGER.debug('Got device_id for %s in %s', msg.address.human,
                      self._address.human)
        self._device_info_queue.put_nowait(msg)

    def _handle_all_link_complete(self, msg):
        if msg and msg.group == 0 and msg.linkcode == 0x01:
            # IM is controller of group 1
            # Set up other needed links
            self.aldb.add_loaded_callback(self.create_default_links)

        last_record = None
        for mem_addr in self.aldb:
            aldb_rec = self.aldb[mem_addr]
            if aldb_rec.control_flags.is_high_water_mark:
                last_record = mem_addr
        if last_record:
            self.aldb.pop(last_record)
        self.read_aldb()

    def _register_messages(self):
        _LOGGER.debug('Registering messages for %s', self._address.human)
        std_device_info_request_ack = StandardSend.template(
            address=self._address,
            commandtuple=COMMAND_ID_REQUEST_0X10_0X00,
            acknak=MESSAGE_ACK)
        _LOGGER.debug('ID ACK: %s', std_device_info_request_ack)
        self._message_callbacks.add(std_device_info_request_ack,
                                    self._handle_get_device_info_ack)

        std_device_info_response = StandardReceive.template(
            address=self._address,
            commandtuple=COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
            flags=MessageFlags.template(
                messageType=MESSAGE_TYPE_BROADCAST_MESSAGE))
        self._message_callbacks.add(std_device_info_response,
                                    self._handle_device_info_response)

        std_assign_all_link = StandardReceive.template(
            address=self._address,
            commandtuple=COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE))
        self._message_callbacks.add(std_assign_all_link,
                                    self._handle_assign_to_all_link_group)

        ext_msg_aldb_record = ExtendedReceive.template(
            address=self._address,
            commandtuple=COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
            userdata=Userdata.template({'d2': 1}),
            flags=MessageFlags.template(
                messageType=MESSAGE_TYPE_DIRECT_MESSAGE,
                extended=1))
        self._message_callbacks.add(ext_msg_aldb_record,
                                    self._handle_aldb_record_received)

        std_msg_pre_nak = StandardReceive.template(
            address=self._address,
            flags=MessageFlags.template(
                messageType=MESSAGE_FLAG_DIRECT_MESSAGE_NAK_0XA0),
            cmd2=0xfc)
        self._message_callbacks.add(std_msg_pre_nak,
                                    self._handle_pre_nak)

        ext_msg_pre_nak = ExtendedReceive.template(
            address=self._address,
            flags=MessageFlags.template(
                messageType=MESSAGE_FLAG_DIRECT_MESSAGE_NAK_0XA0),
            cmd2=0xfc)
        self._message_callbacks.add(ext_msg_pre_nak,
                                    self._handle_pre_nak)

        template_all_link_complete = AllLinkComplete(None, None, self._address,
                                                     None, None, None)
        self._message_callbacks.add(template_all_link_complete,
                                    self._handle_all_link_complete)

    # Send / Receive message processing
    def receive_message(self, msg):
        """Receive a messages sent to this device."""
        _LOGGER.debug('Starting Device.receive_message')
        if hasattr(msg, 'isack') and msg.isack:
            _LOGGER.debug('Got Message ACK')
            if self._sent_msg_wait_for_directACK.get('callback') is not None:
                _LOGGER.debug('Look for direct ACK')
                asyncio.ensure_future(self._wait_for_direct_ACK(),
                                      loop=self._plm.loop)
            else:
                _LOGGER.debug('DA queue: %s',
                              self._sent_msg_wait_for_directACK)
                _LOGGER.debug('Message ACK with no callback')
        if (hasattr(msg, 'flags') and
                hasattr(msg.flags, 'isDirectACK') and
                msg.flags.isDirectACK):
            _LOGGER.debug('Got Direct ACK message')
            if self._send_msg_lock.locked():
                self._directACK_received_queue.put_nowait(msg)
            else:
                _LOGGER.debug('But Direct ACK not expected')
        if not self._is_duplicate(msg):
            callbacks = self._message_callbacks.get_callbacks_from_message(msg)
            for callback in callbacks:
                _LOGGER.debug('Scheduling msg callback: %s', callback)
                self._plm.loop.call_soon(callback, msg)
        else:
            _LOGGER.debug('msg is duplicate')
            _LOGGER.debug(msg)
        self._last_communication_received = datetime.datetime.now()
        _LOGGER.debug('Ending Device.receive_message')

    def _is_duplicate(self, msg):
        if msg.code not in [MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50,
                            MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51]:
            return False

        recent_messages = []
        while not self._recent_messages.empty():
            recent_message = self._recent_messages.get_nowait()
            if recent_message:
                msg_received = recent_message.get("received")
                if msg_received >= (datetime.datetime.now() -
                                    datetime.timedelta(0, 0, 500000)):
                    recent_messages.append(recent_message)
        if not recent_messages:
            self._save_recent_message(msg)
            return False

        for recent_message in recent_messages:
            prev_msg = recent_message.get('msg')
            self._recent_messages.put_nowait(recent_message)
            prev_cmd1 = prev_msg.cmd1
            if prev_msg.flags.isAllLinkBroadcast:
                prev_group = prev_msg.target.bytes[2]
            elif prev_msg.flags.isAllLinkCleanup:
                prev_group = prev_msg.cmd2

            if msg.flags.isAllLinkCleanup or msg.flags.isAllLinkBroadcast:
                cmd1 = msg.cmd1
                if msg.flags.isAllLinkBroadcast:
                    group = msg.target.bytes[2]
                else:
                    group = msg.cmd2
                if prev_cmd1 == cmd1 and prev_group == group:
                    return True
                self._save_recent_message(msg)
            else:
                self._save_recent_message(msg)
                return False

    def _save_recent_message(self, msg):
        recent_message = {"msg": msg,
                          "received": datetime.datetime.now()}
        self._recent_messages.put_nowait(recent_message)

    def _send_msg(self, msg, callback=None, on_timeout=False):
        _LOGGER.debug('Starting Device._send_msg')
        msg_info = {'msg': msg,
                    'callback': callback,
                    'on_timeout': on_timeout}
        self._send_msg_queue.put_nowait(msg_info)
        asyncio.ensure_future(self._process_send_queue(), loop=self._plm.loop)
        _LOGGER.debug('Ending Device._send_msg')

    async def _process_send_queue(self):
        _LOGGER.debug('Starting %s Device._process_send_queue',
                      self._address.human)
        await self._send_msg_lock
        if self._send_msg_lock.locked():
            _LOGGER.debug("Lock is locked from yield from")
        msg_info = await self._send_msg_queue.get()
        msg = msg_info.get('msg')
        callback = msg_info.get('callback')
        self._plm.send_msg(msg)
        if callback:
            self._sent_msg_wait_for_directACK = msg_info
        else:
            if self._send_msg_lock.locked():
                self._send_msg_lock.release()
                _LOGGER.debug('Device %s msg_lock unlocked',
                              self._address.human)
        _LOGGER.debug('Ending %s Device._process_send_queue',
                      self._address.human)

    async def _wait_for_direct_ACK(self):
        _LOGGER.debug('Starting Device._wait_for_direct_ACK')
        msg = None
        while True:
            # wait for an item from the queue
            try:
                with async_timeout.timeout(DIRECT_ACK_WAIT_TIMEOUT):
                    msg = await self._directACK_received_queue.get()
                    _LOGGER.debug('Direct ACK: %s', msg)
                    break
            except asyncio.TimeoutError:
                _LOGGER.debug('No direct ACK messages received.')
                break
            except CancelledError:
                break

        # _LOGGER.debug('Holding lock for 10 seconds')
        # await asyncio.sleep(10, loop=self._plm.loop)
        _LOGGER.debug('Releasing lock after processing direct ACK')
        if self._send_msg_lock.locked():
            self._send_msg_lock.release()
            _LOGGER.debug('Device %s msg_lock unlocked', self._address.human)
        if msg or self._sent_msg_wait_for_directACK.get('on_timeout'):
            callback = self._sent_msg_wait_for_directACK.get('callback', None)
            if callback is not None:
                callback(msg)
        self._sent_msg_wait_for_directACK = {}
        _LOGGER.debug('Ending Device._wait_for_direct_ACK')

    def _aldb_loaded_callback(self):
        self._plm.devices.save_device_info()


# pylint: disable=too-many-instance-attributes
class X10Device():
    """X10 device class."""

    def __init__(self, plm, housecode, unitcode):
        """Init the X10Device class."""
        self._address = Address.x10(housecode, unitcode)
        self._plm = plm
        self._description = "Generic X10 device"
        self._model = ''
        self._aldb = ALDB(None, None, self._address, version=ALDBVersion.Null)
        self._message_callbacks = MessageCallback()
        self._stateList = StateList()
        self._send_msg_lock = asyncio.Lock(loop=self._plm.loop)
        self._last_communication_received = datetime.datetime(1, 1, 1, 1, 1, 1)

    @property
    def address(self):
        """X10 device address."""
        return self._address

    @property
    def description(self):
        """Return the INSTEON device description."""
        return self._description

    @property
    def model(self):
        """Return the INSTEON device model number."""
        return self._model

    @property
    def id(self):
        """Return the ID of the device."""
        return self._address.id

    @property
    def states(self):
        """Return the device states/groups."""
        return self._stateList

    @property
    def aldb(self):
        """Return the device All-Link Database."""
        return self._aldb

    # Send / Receive message processing
    def receive_message(self, msg):
        """Receive a message sent to this device."""
        _LOGGER.debug('Starting X10Device.receive_message')
        if hasattr(msg, 'isack') and msg.isack:
            _LOGGER.debug('Got Message ACK')
            if self._send_msg_lock.locked():
                self._send_msg_lock.release()
        callbacks = self._message_callbacks.get_callbacks_from_message(msg)
        _LOGGER.debug('Found %d callbacks for msg %s', len(callbacks), msg)
        for callback in callbacks:
            _LOGGER.debug('Scheduling msg callback: %s', callback)
            self._plm.loop.call_soon(callback, msg)
        self._last_communication_received = datetime.datetime.now()
        _LOGGER.debug('Ending Device.receive_message')

    async def close(self):
        """Close the writer for a clean shutdown."""
        # Nothing actually needed here.

    def _send_msg(self, msg, wait_ack=True):
        _LOGGER.debug('Starting Device._send_msg')
        asyncio.ensure_future(self._process_send_queue(msg, wait_ack),
                              loop=self._plm.loop)
        _LOGGER.debug('Ending Device._send_msg')

    async def _process_send_queue(self, msg, wait_ack):
        _LOGGER.debug('Starting Device._process_send_queue')
        await self._send_msg_lock
        if self._send_msg_lock.locked():
            _LOGGER.debug("Lock is locked from yield from")

        self._plm.send_msg(msg, wait_timeout=2)
        if not wait_ack:
            _LOGGER.debug("No directACK wait")
            _LOGGER.debug("Releasing lock")
            self._send_msg_lock.release()
        _LOGGER.debug('Ending Device._process_send_queue')


class StateList():
    """Internal class used to hold a list of device states."""

    def __init__(self):
        """Init the StateList Class."""
        self._stateList = {}

    def __len__(self):
        """Get the number of states in the StateList."""
        return len(self._stateList)

    def __iter__(self):
        """Iterate through each state in the StateList."""
        for state in self._stateList:
            yield state

    def __getitem__(self, group):
        """Get a state from the StateList."""
        return self._stateList.get(group, None)

    def __setitem__(self, group, state):
        """Add or update a state in the StateList."""
        if not isinstance(state, State):
            raise ValueError

        self._stateList[group] = state

    def __repr__(self):
        """Juman representation of a state in the StateList."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def add(self, plm, device, stateType, stateName, group, defaultValue=None):
        """Add a state to the StateList."""
        self._stateList[group] = stateType(plm, device, stateName, group,
                                           defaultValue=defaultValue)


class ALDBRecord():
    """Represents an ALDB record."""

    def __init__(self, memory, control_flags, group, address,
                 data1, data2, data3):
        """Initialze the ALDBRecord class."""
        self._memoryLocation = memory
        self._address = Address(address)
        self._group = group
        self._data1 = data1
        self._data2 = data2
        self._data3 = data3
        self._control_flags = ControlFlags.create_from_byte(control_flags)

    def __str__(self):
        """Return the string representation of an ALDB record."""
        props = self._record_properties()
        msgstr = "{"
        first = True
        for prop in props:
            if not first:
                msgstr = '{}, '.format(msgstr)
            for key, val in prop.items():
                if isinstance(val, Address):
                    msgstr = "{}'{}': {}".format(msgstr, key, val.human)
                elif key == 'memory':
                    msgstr = "{}'{}': 0x{:04x}".format(msgstr, key, val)
                elif isinstance(val, int):
                    msgstr = "{}'{}': 0x{:02x}".format(msgstr, key, val)
                else:
                    msgstr = "{}'{}': {}".format(msgstr, key, val)
            first = False
        msgstr = "{}{}".format(msgstr, '}')
        return msgstr

    @property
    def mem_addr(self):
        """Return the memory address of the database record."""
        return self._memoryLocation

    @property
    def memhi(self):
        """Return the memory address MSB."""
        return self._memoryLocation >> 8

    @property
    def memlo(self):
        """Return the memory address LSB."""
        return self._memoryLocation & 0xff

    @property
    def address(self):
        """Return the address of the device the record points to."""
        return self._address

    @property
    def group(self):
        """Return the group the record responds to."""
        return self._group

    @property
    def control_flags(self):
        """Return the record control flags."""
        return self._control_flags

    @property
    def data1(self):
        """Return the data1 field of the ALDB record."""
        return self._data1

    @property
    def data2(self):
        """Return the data2 field of the ALDB record."""
        return self._data2

    @property
    def data3(self):
        """Return the data3 field of the ALDB record."""
        return self._data3

    @staticmethod
    def create_from_userdata(userdata):
        """Create ALDB Record from the userdata dictionary."""
        memhi = userdata.get('d3')
        memlo = userdata.get('d4')
        memory = memhi << 8 | memlo
        control_flags = userdata.get('d6')
        group = userdata.get('d7')
        addrhi = userdata.get('d8')
        addrmed = userdata.get('d9')
        addrlo = userdata.get('d10')
        addr = Address(bytearray([addrhi, addrmed, addrlo]))
        data1 = userdata.get('d11')
        data2 = userdata.get('d12')
        data3 = userdata.get('d13')
        return ALDBRecord(memory, control_flags, group, addr,
                          data1, data2, data3)

    def to_userdata(self):
        """Return a Userdata dictionary."""
        userdata = Userdata({'d3': self.memhi,
                             'd4': self.memlo,
                             'd6': self.control_flags,
                             'd7': self.group,
                             'd8': self.address.bytes[2],
                             'd9': self.address.bytes[1],
                             'd10': self.address.bytes[0],
                             'd11': self.data1,
                             'd12': self.data2,
                             'd13': self.data3})
        return userdata

    def _record_properties(self):
        if self._control_flags.is_controller:
            mode = 'C'
        else:
            mode = 'R'
        rec = [{'memory': self._memoryLocation},
               {'inuse': self._control_flags.is_in_use},
               {'mode': mode},
               {'highwater': self._control_flags.is_high_water_mark},
               {'group': self.group},
               {'address': self.address},
               {'data1': self.data1},
               {'data2': self.data2},
               {'data3': self.data3}]
        return rec


class ControlFlags():
    """Represents a ControlFlag byte of an ALDB record."""

    def __init__(self, in_use, controller, used_before, bit5=0, bit4=0):
        """Init the ControlFlags Class."""
        self._in_use = bool(in_use)
        self._controller = bool(controller)
        self._used_before = bool(used_before)
        self._bit5 = bool(bit5)
        self._bit4 = bool(bit4)

    @property
    def is_in_use(self):
        """Return True if the record is in use."""
        return self._in_use

    @property
    def is_available(self):
        """Return True if the record is available for use."""
        return not self._in_use

    @property
    def is_controller(self):
        """Return True if the device is a controller."""
        return self._controller

    @property
    def is_responder(self):
        """Return True if the device is a responder."""
        return not self._controller

    @property
    def is_high_water_mark(self):
        """Return True if this is the last record."""
        return not self._used_before

    @property
    def is_used_before(self):
        """Return True if this is not the last record."""
        return self._used_before

    @property
    def byte(self):
        """Return a byte representation of ControlFlags."""
        flags = int(self._in_use) << 7 \
            | int(self._controller) << 6 \
            | int(self._bit5) << 5 \
            | int(self._bit4) << 4 \
            | int(self._used_before) << 1
        return flags

    @staticmethod
    def create_from_byte(control_flags):
        """Create a ControlFlags class from a control flags byte."""
        in_use = bool(control_flags & 1 << 7)
        controller = bool(control_flags & 1 << 6)
        bit5 = bool(control_flags & 1 << 5)
        bit4 = bool(control_flags & 1 << 4)
        used_before = bool(control_flags & 1 << 1)
        flags = ControlFlags(in_use, controller, used_before,
                             bit5=bit5, bit4=bit4)
        return flags


class ALDBStatus(Enum):
    """All-Link Database load status."""

    EMPTY = 0
    LOADING = 1
    LOADED = 2
    FAILED = 3
    PARTIAL = 4


class ALDBVersion(Enum):
    """All-Link Database version."""

    Null = 0
    v1 = 1
    v2 = 2
    v2cs = 20


# pylint: disable=too-many-instance-attributes
class ALDB():
    """Represents a device All-Link database."""

    def __init__(self, send_method, loop, address,
                 version=ALDBVersion.v2, mem_addr=0x0000):
        """Instantiate the ALL-Link Database object."""
        self._records = {}
        self._status = ALDBStatus.EMPTY
        self._prior_status = self._status
        self._version = version

        self._send_method = send_method
        self._loop = loop
        self._address = address
        self._mem_addr = mem_addr

        self._rec_mgr_lock = asyncio.Lock(loop=self._loop)
        self._load_action = LoadAction(0, 0, 0)
        self._cb_aldb_loaded = []

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return len(self._records)

    def __iter__(self):
        """Iterate through each ALDB device record."""
        keys = list(self._records.keys())
        keys.sort(reverse=True)
        for key in keys:
            yield key

    def __getitem__(self, mem_addr):
        """Fetch a device from the ALDB."""
        return self._records.get(mem_addr)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    @property
    def status(self):
        """Return the ALDB load status."""
        return self._status

    @status.setter
    def status(self, val: ALDBStatus):
        """Set the ALDB status value."""
        self._status = val

    @property
    def version(self):
        """Return the ALDB version."""
        return self._version

    def pop(self, key):
        """Pop and remove an item from the ALDB."""
        return self._records.pop(key)

    def add_loaded_callback(self, callback):
        """Add a callback to be run when the ALDB load is complete."""
        if callback not in self._cb_aldb_loaded:
            self._cb_aldb_loaded.append(callback)

    async def load(self, mem_addr=0x0000, rec_count=0, retry=0):
        """Read the device database and load."""
        if self._version == ALDBVersion.Null:
            self._status = ALDBStatus.LOADED
            _LOGGER.debug('Device has no ALDB')
        else:
            self._status = ALDBStatus.LOADING
            _LOGGER.debug('Tring to lock from load')
            await self._rec_mgr_lock
            _LOGGER.debug('load yielded lock')

            mem_hi = mem_addr >> 8
            mem_lo = mem_addr & 0xff
            log_output = 'ALDB read'
            max_retries = 0
            if rec_count:
                max_retries = ALDB_RECORD_RETRIES
                if mem_addr == 0x0000:
                    log_output = '{:s} first record'.format(log_output)
                else:
                    log_output = '{:s} record {:04x}'.format(log_output,
                                                             mem_addr)
            else:
                max_retries = ALDB_ALL_RECORD_RETRIES
                log_output = '{:s} all records'.format(log_output)

            if retry:
                log_output = '{:s} retry {:d} of {:d}'.format(log_output,
                                                              retry,
                                                              max_retries)
            _LOGGER.info(log_output)
            userdata = Userdata({'d1': 0,
                                 'd2': 0,
                                 'd3': mem_hi,
                                 'd4': mem_lo,
                                 'd5': rec_count})
            msg = ExtendedSend(self._address,
                               COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
                               userdata=userdata)
            msg.set_checksum()
            self._send_method(msg, self._handle_read_aldb_ack, True)

            if not self._load_action:
                self._set_load_action(mem_addr, rec_count, -1, False)

    def get(self, mem_addr):
        """Return an All-Link record at a memory address."""
        return self._records.get(mem_addr)

    def clear(self):
        """Remove all records."""
        self._records.clear()

    # pylint: disable=too-many-locals
    def write_record(self, mem_addr: int, mode: str, group: int, target,
                     data1=0x00, data2=0x00, data3=0x00):
        """Write an All-Link database record."""
        if not (self._have_first_record() and self._have_last_record()):
            _LOGGER.error('Must load the Insteon All-Link Database before '
                          'writing to it')
        else:
            self._prior_status = self._status
            self._status = ALDBStatus.LOADING
            mem_hi = mem_addr >> 8
            mem_lo = mem_addr & 0xff
            controller = mode == 'c'
            control_flag = ControlFlags(True, controller, True, False, False)
            addr = Address(target)
            addr_lo = addr.bytes[0]
            addr_mid = addr.bytes[1]
            addr_hi = addr.bytes[2]
            userdata = Userdata({'d1': 0,
                                 'd2': 0x02,
                                 'd3': mem_hi,
                                 'd4': mem_lo,
                                 'd5': 0x08,
                                 'd6': control_flag.byte,
                                 'd7': group,
                                 'd8': addr_lo,
                                 'd9': addr_mid,
                                 'd10': addr_hi,
                                 'd11': data1,
                                 'd12': data2,
                                 'd13': data3})
            msg = ExtendedSend(self._address,
                               COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
                               userdata=userdata)
            msg.set_checksum()
            _LOGGER.debug('writing message %s', msg)
            self._send_method(msg, self._handle_write_aldb_ack, True)
            self._load_action = LoadAction(mem_addr, 1, 0)

    # pylint: disable=too-many-locals
    def del_record(self, mem_addr: int):
        """Write an All-Link database record."""
        record = self._records.get(mem_addr)
        if not record:
            _LOGGER.error('Must load the Insteon All-Link Database record '
                          'before deleting it')
        else:
            self._prior_status = self._status
            self._status = ALDBStatus.LOADING
            mem_hi = mem_addr >> 8
            mem_lo = mem_addr & 0xff
            controller = record.control_flags.is_controller
            control_flag = ControlFlags(False, controller, True, False, False)
            addr = record.address
            addr_lo = addr.bytes[0]
            addr_mid = addr.bytes[1]
            addr_hi = addr.bytes[2]
            group = record.group
            data1 = record.data1
            data2 = record.data2
            data3 = record.data3
            userdata = Userdata({'d1': 0,
                                 'd2': 0x02,
                                 'd3': mem_hi,
                                 'd4': mem_lo,
                                 'd5': 0x08,
                                 'd6': control_flag.byte,
                                 'd7': group,
                                 'd8': addr_lo,
                                 'd9': addr_mid,
                                 'd10': addr_hi,
                                 'd11': data1,
                                 'd12': data2,
                                 'd13': data3})
            msg = ExtendedSend(self._address,
                               COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
                               userdata=userdata)
            msg.set_checksum()
            _LOGGER.debug('writing message %s', msg)
            self._send_method(msg, self._handle_write_aldb_ack, True)
            self._load_action = LoadAction(mem_addr, 1, 0)

    def find_matching_link(self, mode, group, addr):
        """Find a matching link in the current device.

        Mode: r | c is the mode of the link in the linked device
              This method will search for a corresponding link in the
              reverse direction.
        group: All-Link group number
        addr:  Inteon address of the linked device
        """
        found_rec = None
        mode_test = None
        if mode.lower() in ['c', 'r']:
            link_group = int(group)
            link_addr = Address(addr)
            for mem_addr in self:
                rec = self[mem_addr]
                if mode.lower() == 'r':
                    mode_test = rec.control_flags.is_controller
                else:
                    mode_test = rec.control_flags.is_responder
                if (mode_test and
                        rec.group == link_group and
                        rec.address == link_addr):
                    found_rec = rec
        return found_rec

    def record_received(self, msg):
        """Handle ALDB record received from device."""
        release_lock = False
        userdata = msg.userdata
        rec = ALDBRecord.create_from_userdata(userdata)
        self._records[rec.mem_addr] = rec

        _LOGGER.debug('ALDB Record: %s', rec)

        rec_count = self._load_action.rec_count
        if rec_count == 1 or self._have_all_records():
            release_lock = True

        if self._is_first_record(rec):
            self._mem_addr = rec.mem_addr

        if release_lock and self._rec_mgr_lock.locked():
            _LOGGER.debug('Releasing lock because record received')
            self._rec_mgr_lock.release()

    def load_saved_records(self, status, records):
        """Load ALDB records from a set of saved records."""
        if isinstance(status, ALDBStatus):
            self._status = status
        else:
            self._status = ALDBStatus(status)
        for mem_addr in records:
            rec = records[mem_addr]
            control_flags = int(rec.get('control_flags', 0))
            group = int(rec.get('group', 0))
            rec_addr = rec.get('address', '000000')
            data1 = int(rec.get('data1', 0))
            data2 = int(rec.get('data2', 0))
            data3 = int(rec.get('data3', 0))
            self[int(mem_addr)] = ALDBRecord(int(mem_addr), control_flags,
                                             group, rec_addr,
                                             data1, data2, data3)
        if self._status == ALDBStatus.LOADED:
            keys = list(self._records.keys())
            keys.sort(reverse=True)
            first_key = keys[0]
            self._mem_addr = first_key

    # pylint: disable=unused-argument
    def _handle_read_aldb_ack(self, msg):
        _LOGGER.debug('Read ALDB directACK received or timeout reached')
        asyncio.ensure_future(self._read_timeout_manager(), loop=self._loop)

    def _handle_write_aldb_ack(self, msg):
        if msg:
            _LOGGER.info('Device %s confirmed All-Link record was written',
                         self._address.human)
            try:
                self._records.pop(self._load_action.mem_addr)
            except KeyError:
                pass
            asyncio.ensure_future(self.load(self._load_action.mem_addr, 1, 0),
                                  loop=self._loop)
        else:
            _LOGGER.info('Device %s did not confirm All-Link record was '
                         'written', self._address.human)
            self._status = self._prior_status

    async def _read_timeout_manager(self):
        _LOGGER.debug('_read_timeout_manager started.')
        read_complete = False
        rec_count = self._load_action.rec_count
        timeout = ALDB_RECORD_TIMEOUT if rec_count else ALDB_ALL_RECORD_TIMEOUT

        try:
            with async_timeout.timeout(timeout + self._load_action.retries):
                _LOGGER.debug('Tring to get lock in _read_timeout_manager.')
                await self._rec_mgr_lock
                _LOGGER.debug('_read_timeout_manager lock yielded.')
                read_complete = True
        except asyncio.TimeoutError:
            if (self._load_action.rec_count and
                    self._load_action.mem_addr == 0x0000 and
                    self._have_first_record()):
                read_complete = False
            elif self.get(self._load_action.mem_addr):
                read_complete = True
            else:
                _LOGGER.debug('ALDB record response timeout.')
                read_complete = False

        self._set_load_action(self._load_action.mem_addr,
                              self._load_action.rec_count,
                              self._load_action.retries,
                              read_complete)

        mem_addr = self._load_action.mem_addr
        rec_count = self._load_action.rec_count
        retries = self._load_action.retries

        if self._rec_mgr_lock.locked():
            self._rec_mgr_lock.release()

        if mem_addr is not None:
            asyncio.ensure_future(self.load(mem_addr, rec_count, retries),
                                  loop=self._loop)
        elif read_complete or self._have_all_records():
            _LOGGER.info('All-Link Database load complete for device %s',
                         self._address)
            self._load_finished(ALDBStatus.LOADED)
        else:
            if self._records:
                _LOGGER.warning('Insteon All-Link Database partially loaded '
                                'for device %s', self._address)
                self._load_finished(ALDBStatus.PARTIAL)
            else:
                _LOGGER.warning('Insteon All-Link Database  failed to load '
                                'for device %s', self._address)
                self._load_finished(ALDBStatus.FAILED)

    def _load_finished(self, status):
        self._status = status
        while self._cb_aldb_loaded:
            _LOGGER.debug('Calling aldb loaded callback')
            callback = self._cb_aldb_loaded.pop()
            if callback:
                callback()
        self._load_action = LoadAction(0, 0, 0)

    def _set_load_action(self, mem_addr, rec_count, retries,
                         read_complete=False):
        """Calculate the next record to read.

        If the last record was successful and one record was being read then
        look for the next record until we get to the high water mark.

        If the last read was successful and all records were being read then
        look for the first record.

        if the last read was unsuccessful and one record was being read then
        repeat the last read until max retries

        If the last read was unsuccessful and all records were being read then
        repeat the last read until max retries or look for the first record.
        """
        if self._have_all_records():
            mem_addr = None
            rec_count = 0
            retries = 0
        elif read_complete:
            retries = 0
            if rec_count:
                mem_addr = self._next_address(mem_addr)
            else:
                mem_addr = self._next_address(mem_addr)
                rec_count = 1
                retries = 0
        elif rec_count and retries < ALDB_RECORD_RETRIES:
            retries = retries + 1
        elif not rec_count and retries < ALDB_ALL_RECORD_RETRIES:
            retries = retries + 1
        elif not rec_count and retries >= ALDB_ALL_RECORD_RETRIES:
            mem_addr = self._next_address(mem_addr)
            rec_count = 1
            retries = 0
        else:
            mem_addr = None
            rec_count = 0
            retries = 0

        self._load_action = LoadAction(mem_addr, rec_count, retries)
        if mem_addr is not None:
            _LOGGER.debug('Load action: addr: %04x rec_count: %d retries: %d',
                          self._load_action.mem_addr,
                          self._load_action.rec_count,
                          self._load_action.retries)

    def _next_address(self, mem_addr):
        if self._have_first_record() and mem_addr == 0x0000:
            mem_addr = self._mem_addr
        while self.get(mem_addr):
            if self.get(mem_addr).control_flags.is_high_water_mark:
                mem_addr = None
            else:
                mem_addr = mem_addr - 8
        return mem_addr

    def _have_first_record(self):
        have_first_record = False
        if self._records:
            keys = list(self._records.keys())
            keys.sort(reverse=True)
            first_key = int(keys[0])
            if first_key == self._mem_addr:
                have_first_record = True
            elif first_key == 0x0fff:
                self._mem_addr = first_key
                have_first_record = True
        return have_first_record

    def _have_last_record(self):
        have_last_record = False
        if self._records:
            keys = list(self._records.keys())
            keys.sort(reverse=False)
            last_key = keys[0]
            if self[last_key].control_flags.is_high_water_mark:
                have_last_record = True
        return have_last_record

    def _is_first_record(self, rec):
        is_first_record = False
        mem_addr = self._load_action.mem_addr
        rec_count = self._load_action.rec_count
        if rec_count and mem_addr == 0x0000:
            is_first_record = True
        elif self._mem_addr == rec.mem_addr:
            is_first_record = True
        elif (self._mem_addr == 0x0000 and
              rec.mem_addr == 0x0fff):
            is_first_record = True
        return is_first_record

    def _have_all_records(self):
        have_all_recs = False
        if self._have_first_record() and self._have_last_record():
            prev_mem_addr = None
            for mem_addr in self:
                if not prev_mem_addr:
                    prev_mem_addr = mem_addr
                elif mem_addr == (prev_mem_addr - 8):
                    if self[mem_addr].control_flags.is_high_water_mark:
                        have_all_recs = True
                    else:
                        prev_mem_addr = mem_addr
                else:
                    have_all_recs = False
                    break
        return have_all_recs
