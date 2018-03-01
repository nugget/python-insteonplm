"""Insteon Device Classes."""
import asyncio
import datetime
import logging
import async_timeout

from insteonplm.address import Address
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.constants import (
    MESSAGE_ACK, COMMAND_ID_REQUEST_0X10_0X00,
    COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00,
    COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
    COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE,
    COMMAND_FX_USERNAME_0X03_0X01,
    COMMAND_ENTER_LINKING_MODE_0X09_NONE,
    COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE,
    COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00,
    COMMAND_PING_0X0F_0X00
)

from insteonplm.devices.stateList import StateList

WAIT_TIMEOUT = 2

def create(plm, address, cat, subcat, firmware=None):
    """Create a device from device info data."""
    import insteonplm.devices.ipdb
    ipdb = insteonplm.devices.ipdb.IPDB()
    product = ipdb[[cat, subcat]]
    deviceclass = product.deviceclass
    device = None
    if deviceclass is not None:
        device = deviceclass.create(plm, address, cat, subcat,
                                    product.product_key,
                                    product.description,
                                    product.model)
    return device


class DeviceBase(object):
    """INSTEON Device"""

    def __init__(self, plm, address, cat, subcat, product_key=0x00,
                 description='', model=''):
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
        self._send_queue = asyncio.Queue(loop=self._plm.loop)
        self._sent_msg_wait_for_directACK = {}
        self._directACK_received_queue = asyncio.Queue(loop=self._plm.loop)

        if not hasattr(self, '_noRegisterCallback'):
            std_msg_recd = StandardReceive.template(address=self._address)
            ext_msg_recd = ExtendedReceive.template(address=self._address)
            std_msg_ack_recd = StandardSend.template(address=self._address,
                                                     acknak=MESSAGE_ACK)
            ext_msg_ack_recd = ExtendedSend.template(address=self._address,
                                                     acknak=MESSAGE_ACK)

            self._plm.message_callbacks.add(std_msg_recd,
                                            self._receive_message)
            self._plm.message_callbacks.add(ext_msg_recd,
                                            self._receive_message)
            self._plm.message_callbacks.add(std_msg_ack_recd,
                                            self._receive_message)
            self._plm.message_callbacks.add(ext_msg_ack_recd,
                                            self._receive_message)

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
        """Returns the device states/groups."""
        return self._stateList

    @property
    def prod_data_in_aldb(self):
        """Indicates if the PLM use the ALDB data to setup the device.

        True if Product data (cat, subcat) is stored in the PLM ALDB.
        False if product data must be aquired via a Device ID message or from a
        Product Data Request command.

        The method of linking determines if product data in the ALDB,
        therefore False is the default. The common reason to store product data
        in the ALDB is for one way devices or battery opperated devices where
        the ability to send a command request is limited.
        """
        return self._product_data_in_aldb

    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None,
               description=None, model=None):
        """Factory method to create a device."""
        return cls(plm, address, cat, subcat, product_key,
                   description, model)

    def _receive_message(self, msg):
        self.log.debug('Starting DeviceBase._receive_message')
        if hasattr(msg, 'isack') and msg.isack:
            self.log.debug('Got Message ACK')
            if self._sent_msg_wait_for_directACK.get('callback') is not None:
                self.log.debug('Look for direct ACK')
                coro = self._wait_for_direct_ACK()
                asyncio.ensure_future(coro, loop=self._plm.loop)
            else:
                self.log.debug('Message ACK with no callback')
        if (hasattr(msg, 'flags')
                and hasattr(msg.flags, 'isDirectACK')
                and msg.flags.isDirectACK):
            self.log.debug('Got Direct ACK message')
            if self._send_msg_lock.locked():
                self.log.debug('Lock is locked')
                self._directACK_received_queue.put_nowait(msg)
        self._last_communication_received = datetime.datetime.now()
        self.log.debug('Ending DeviceBase._receive_message')

    def async_refresh_state(self):
        """Request each state to provide status update."""
        for state in self._stateList:
            self._stateList[state].async_refresh_state()

    def _send_msg(self, msg, directACK_Method=None):
        self.log.debug('Starting DeviceBase._send_msg')
        write_message_coroutine = self._process_send_queue(msg,
                                                           directACK_Method)
        self._send_queue.put_nowait(msg)
        asyncio.ensure_future(write_message_coroutine,
                              loop=self._plm.loop)
        self.log.debug('Ending DeviceBase._send_msg')

    @asyncio.coroutine
    def _process_send_queue(self, msg, directACK_Method=None):
        self.log.debug('Starting DeviceBase._process_send_queue')
        yield from self._send_msg_lock
        if directACK_Method is not None:
            self._sent_msg_wait_for_directACK = {'msg': msg,
                                                 'callback': directACK_Method}
            self.log.debug('Attempt to acquire lock')
            self._send_msg_lock.acquire()
            self.log.debug('Lock acquired')
        self._plm.send_msg(msg)
        self.log.debug('Ending DeviceBase._process_send_queue')

    @asyncio.coroutine
    def _wait_for_direct_ACK(self):
        self.log.debug('Starting DeviceBase._wait_for_direct_ACK')
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
        self.log.debug('Ending DeviceBase._wait_for_direct_ACK')

    def id_request(self):
        """Request a device ID from a device"""
        self._plm.send_standard(self._address,
                                COMMAND_ID_REQUEST_0X10_0X00)

    def product_data_request(self):
        """Request product data from a device.

        Not supported by all devices.
        Required after 01-Feb-2007.
        """
        self._plm.send_standard(self._address,
                                COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00)

    def assign_to_all_link_group(self, group=0x01):
        """Assign a device to an All-Link Group.

        The default is group 0x01.
        """
        self._plm.send_standard(self._address,
                                COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE,
                                group)

    def delete_from_all_link_group(self, group):
        """Delete a device to an All-Link Group."""
        self._plm.send_standard(self._address,
                                COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE,
                                group)

    def fx_username(self):
        """Get FX Username.

        Only required for devices that support FX Commands.
        FX Addressee responds with an ED 0x0301 FX Username Response message
        """
        self._plm.send_standard(self._address, COMMAND_FX_USERNAME_0X03_0X01)

    def device_text_string_request(self):
        """Get FX Username.

        Only required for devices that support FX Commands.
        FX Addressee responds with an ED 0x0301 FX Username Response message.
        """
        self.log.debug("Starting: devicebase.device_text_string_request")
        self._plm.send_standard(self._address, COMMAND_FX_USERNAME_0X03_0X01)

    def enter_linking_mode(self, group=0x01):
        """Tell a device to enter All-Linking Mode.

        Same as holding down the Set button for 10 sec.
        Default group is 0x01. \nNot supported by i1 devices.
        """
        self._plm.send_standard(self._address,
                                COMMAND_ENTER_LINKING_MODE_0X09_NONE,
                                group)

    def enter_unlinking_mode(self, group):
        """Unlink a device from an All-Link group.

        Not supported by i1 devices.
        """
        self._plm.send_standard(self._address,
                                COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE,
                                group)

    def get_engine_version(self):
        """Get the device engine version."""
        self._plm.send_standard(self._address,
                                COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00)

    def ping(self):
        """Ping a device."""
        self._plm.send_standard(self._address, COMMAND_PING_0X0F_0X00)

    def read_aldb(self):
        """Read the device All-Link Database."""
        pass

    def write_aldb(self):
        """Write to the device All-Link Database."""
        pass
