"""Insteon Device Classes."""
import asyncio
import datetime
import logging
import async_timeout

from insteonplm.address import Address
from insteonplm.constants import (
    MESSAGE_ACK, COMMAND_ID_REQUEST_0X10_0X00,
    COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00,
    COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
    COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE,
    COMMAND_FX_USERNAME_0X03_0X01,
    COMMAND_ENTER_LINKING_MODE_0X09_NONE,
    COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE,
    COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00,
    COMMAND_PING_0X0F_0X00,
    COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
    MESSAGE_TYPE_DIRECT_MESSAGE
)
from insteonplm.messagecallback import MessageCallback
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.userdata import Userdata
from insteonplm.states import State

WAIT_TIMEOUT = 2


def create(plm, address, cat, subcat, firmware=None):
    """Create a device from device info data."""
    from insteonplm.devices.ipdb import IPDB
    ipdb = IPDB()
    product = ipdb[[cat, subcat]]
    deviceclass = product.deviceclass
    device = None
    if deviceclass is not None:
        device = deviceclass.create(plm, address, cat, subcat,
                                    product.product_key,
                                    product.description,
                                    product.model)
    return device


class Device(object):
    """INSTEON Device Class."""

    def __init__(self, plm, address, cat, subcat, product_key=0x00,
                 description='', model=''):
        """Initialize the Device class."""
        self.log = logging.getLogger(__name__)

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
        self._send_msg_lock = asyncio.Lock(loop=self._plm.loop)
        self._sent_msg_wait_for_directACK = {}
        self._directACK_received_queue = asyncio.Queue(loop=self._plm.loop)
        self._message_callbacks = MessageCallback()
        self._aldb = []

        if not hasattr(self, '_noRegisterCallback'):
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
        return self._address.hex

    @property
    def states(self):
        """Return the device states/groups."""
        return self._stateList

    @property
    def prod_data_in_aldb(self):
        """Return if the PLM use the ALDB data to setup the device.

        True if Product data (cat, subcat) is stored in the PLM ALDB.
        False if product data must be aquired via a Device ID message or from a
        Product Data Request command.

        The method of linking determines if product data in the ALDB,
        therefore False is the default. The common reason to store product data
        in the ALDB is for one way devices or battery opperated devices where
        the ability to send a command request is limited.
        """
        return self._product_data_in_aldb

    @property
    def aldb(self):
        return self._aldb

    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None,
               description=None, model=None):
        """Factory method to create a device."""
        return cls(plm, address, cat, subcat, product_key,
                   description, model)

    # Public Methods
    def async_refresh_state(self):
        """Request each state to provide status update."""
        for state in self._stateList:
            self._stateList[state].async_refresh_state()

    def id_request(self):
        """Request a device ID from a device."""
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
        msg = StandardSend(self._address,COMMAND_FX_USERNAME_0X03_0X01)
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
        msg = StandardSend(self._address,
                                COMMAND_ENTER_LINKING_MODE_0X09_NONE,
                                cmd2=group)
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

    def read_aldb(self, mem_addr=None):
        """Read the device All-Link Database."""
        if mem_addr:
            mem_hi = mem_addr >> 8
            mem_lo = mem_addr & 0xff
        if self.aldb:
            last_rec = self.aldb[-1]
            mem_addr = (last_rec.memhi << 8) + last_rec.memlo - 8
            mem_hi = mem_addr >> 8
            mem_lo = mem_addr & 0xff
        else:
            mem_hi = self._mem_addr >> 8
            mem_lo = self._mem_addr & 0xff
        userdata = Userdata({'d1': 0,
                             'd2': 0,
                             'd3': mem_hi,
                             'd4': mem_lo,
                             'd5': 1})
        # userdata = Userdata({'d1': 0,
        #                      'd2': 0,
        #                      'd3': 0,
        #                      'd4': 0,
        #                      'd5': 0})
        msg = ExtendedSend(self.address,
                           COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
                           userdata=userdata)
        self._send_msg(msg)
        yield from asyncio.sleep(.1, loop=self._plm.loop)

    def write_aldb(self):
        """Write to the device All-Link Database."""
        pass

    def _handle_aldb_record_received(self, msg):
        userdata = msg.userdata
        rec = ALDBRecord.create_from_userdata(userdata)
        self._aldb.append(rec)
        self.log.debug('ALDB Record: %s', rec)
        if rec.control_flags.is_high_water_mark:
            self.log.debug('Device ALDB high water mark reached')
        else:
            mem_addr = (userdata['d3'] << 8) + userdata['d4'] - 8
            self.read_aldb(mem_addr)

    def _register_messages(self):
            ext_msg_aldb_record = ExtendedReceive.template(
                address=self._address,
                commandtuple=COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
                userdata=Userdata.template({'d2': 1}),
                flags=MessageFlags.template(
                    messageType=MESSAGE_TYPE_DIRECT_MESSAGE,
                    extended=1))
            self._message_callbacks.add(ext_msg_aldb_record,
                                            self._handle_aldb_record_received)

    # Send / Receive message processing
    def receive_message(self, msg):
        self.log.debug('Starting Device.receive_message')
        if hasattr(msg, 'isack') and msg.isack:
            self.log.debug('Got Message ACK')
            if self._sent_msg_wait_for_directACK.get('callback') is not None:
                self.log.debug('Look for direct ACK')
                coro = self._wait_for_direct_ACK()
                asyncio.ensure_future(coro, loop=self._plm.loop)
            else:
                self.log.debug('DA queue: %s', self._sent_msg_wait_for_directACK)
                self.log.debug('Message ACK with no callback')
        if (hasattr(msg, 'flags')
                and hasattr(msg.flags, 'isDirectACK')
                and msg.flags.isDirectACK):
            self.log.debug('Got Direct ACK message')
            if self._send_msg_lock.locked():
                self.log.debug('Lock is locked')
                self._directACK_received_queue.put_nowait(msg)
        callbacks = self._message_callbacks.get_callbacks_from_message(msg)
        self.log.debug('Found %d callbacks for msg %s', len(callbacks), msg)
        for callback in callbacks:
            self.log.debug('Scheduling msg callback: %s', callback)
            self._plm.loop.call_soon(callback, msg)
        self._last_communication_received = datetime.datetime.now()
        self.log.debug('Ending Device.receive_message')

    def _send_msg(self, msg, directACK_Method=None):
        self.log.debug('Starting Device._send_msg')
        write_message_coroutine = self._process_send_queue(msg,
                                                           directACK_Method)
        asyncio.ensure_future(write_message_coroutine,
                              loop=self._plm.loop)
        self.log.debug('Ending Device._send_msg')

    @asyncio.coroutine
    def _process_send_queue(self, msg, directACK_Method=None):
        self.log.debug('Callback: %s', directACK_Method)
        yield from self._send_msg_lock
        if directACK_Method:
            self.log.debug('Writing directACK callback')
            self._sent_msg_wait_for_directACK = {'msg': msg,
                                                 'callback': directACK_Method}
            self.log.debug('Attempt to acquire lock')
            self._send_msg_lock.acquire()
            self.log.debug('Lock acquired')
        self._plm.send_msg(msg)
        self.log.debug('Ending Device._process_send_queue')

    @asyncio.coroutine
    def _wait_for_direct_ACK(self):
        self.log.debug('Starting Device._wait_for_direct_ACK')
        msg = None
        while True:
            # wait for an item from the queue
            try:
                with async_timeout.timeout(WAIT_TIMEOUT):
                    msg = yield from self._directACK_received_queue.get()
                    break
            except asyncio.TimeoutError:
                self.log.debug('No direct ACK messages received.')
                break
        self.log.debug('Releasing lock')
        self._send_msg_lock.release()
        if msg is not None:
            callback = self._sent_msg_wait_for_directACK.get('callback', None)
            if callback is not None:
                callback(msg)
        self._sent_msg_wait_for_directACK = {}
        self.log.debug('Ending Device._wait_for_direct_ACK')


class StateList(object):
    """Internal class used to hold a list of device states."""

    def __init__(self):
        """Initialize the StateList Class."""
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
            return ValueError

        self._stateList[group] = state

    def __repr__(self):
        """Juman representation of a state in the StateList."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def add(self, plm, device, stateType, stateName, group, defaultValue=None):
        """Add a state to the StateList."""
        self._stateList[group] = stateType(plm, device, stateName, group,
                                           defaultValue=defaultValue)

class ALDBRecord(object):
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
                             'd8': self.address[2],
                             'd9': self.address[1],
                             'd10': self.address[0],
                             'd11': self.data1,
                             'd12': self.data2,
                             'd13': self.data3})
        return userdata

    def _record_properties(self):
        if not self._control_flags.is_controller:
            mode = 'Controller'
        else:
            mode = 'Responder'
        rec = [{'memory': self._memoryLocation},
               {'inuse': self._control_flags.is_in_use},
               {'mode':  mode},
               {'highwater': self._control_flags.is_high_water_mark},
               {'group': self.group},
               {'address': self.address},
               {'data1': self.data1},
               {'data2': self.data2},
               {'data3': self.data3}]
        return rec


class ControlFlags(object):
    """Represents a ControlFlag byte of an ALDB record."""

    def __init__(self, in_use, controller, used_before, bit5=0, bit4=0):
        """Initialize the ControlFlags Class."""
        self._in_use = bool(in_use)
        self._controller = bool(controller)
        self._used_before = bool(used_before)
        self._bit5 = bool(bit5)
        self._bit4 = bool(bit4)

    @property
    def is_in_use(self):
        """Returns True if the record is in use."""
        return self._in_use

    @property
    def is_available(self):
        """Returns True if the recored is availabe for use."""
        return not self._in_use

    @property
    def is_controller(self):
        """Returns True if the device is a controller."""
        return self._controller

    @property
    def is_responder(self):
        """Returns True if the device is a responder."""
        return not self._controller

    @property
    def is_high_water_mark(self):
        """Returns True if this is the last record."""
        return not self._used_before

    @property
    def is_used_before(self):
        """Returns True if this is not the last record."""
        return self._used_before

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

    def to_byte(self):
        """Returns a byte representation of ControlFlags."""
        flags = int(self._in_use) << 7 \
            | int(self._controller) << 6 \
            | int(self._bit5) << 5 \
            | int(self._bit4) << 4 \
            | int(self._used_before) << 1
        return flags
