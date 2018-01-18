import logging
import asyncio

from insteonplm.address import Address
from insteonplm.messages.messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.messagecallback import MessageCallback
from insteonplm.statechangesignal import StateChangeSignal

class DeviceBase(object):
    """INSTEON Device"""

    def __init__(self, plm, address, cat, subcat, product_key=0x00, description='', model='', groupbutton=0x01):
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
        self._groupbutton = groupbutton

        self.log = logging.getLogger(__name__)

        self._product_data_in_aldb = False
        self._message_callbacks = MessageCallback()
        self._state_status_callback = None
        self._state_status_lock = asyncio.Lock(loop=self._plm.loop)

    @property
    def address(self):
        return self._address

    @property
    def cat(self):
        return self._cat

    @property
    def subcat(self):
        return self._subcat

    @property
    def product_key(self):
        return self._product_key

    @property
    def description(self):
        return self._description

    @property
    def model(self):
        return self._model

    @property
    def groupbutton(self):
        return self._groupbutton

    @property
    def id(self):
        return self._get_device_id(self._groupbutton)

    @property 
    def state_status_lock(self):
        return self._state_status_lock 
    
    @property
    def prod_data_in_aldb(self):
        """True if Product data (cat, subcat, product_key) is stored in the PLM ALDB.
            False if product data must be aquired via a Device ID message or from a Product Data Request command.
           
            Very few devices store their product data in the ALDB, therefore False is the default.
            The common reason to store product data in the ALDB is for one way devices or battery opperated devices where 
            the ability to send a command request is limited."""

        return self._product_data_in_aldb

    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        return cls(plm, address, cat, subcat, product_key, description, model, groupbutton)

    def receive_message(self, msg):
        self.log.debug('Starting DeviceBase.receive_message')
        # if msg.isnakflag or msg.isgroupflag:  #Need to work on this more. In this case the high bite, 0x04 bit indicates cleanup
        #    pass
        # else:
        self.log.debug('Total callbacks: %d', len(self._message_callbacks))
        callback = self._message_callbacks.get_callback_from_message(msg)
        if callback is None:
            if hasattr(msg, 'cmd1'):
                if msg.acknak is None:
                    self.log.debug('No callback found in device %s for message code %02x with cmd1 %02x and cmd2 %02x and acknak %s', self.id, msg.code, msg.cmd1, msg.cmd2, 'None')
                else:
                    self.log.debug('No callback found in device %s for message code %02x with cmd1 %02x and cmd2 %02x and acknak %02x', self.id, msg.code, msg.cmd1, msg.cmd2, msg.acknak)
            else:
                self.log.debug('No call back found in device %s for message %s', self.id, msg.hex)
        else:
            callback(msg)
        self.log.debug('Ending DeviceBase.receive_message')

    def async_refresh_state(self):
        for prop in dir(self):
            propAttr = getattr(self, prop)
            if type(propAttr) == StateChangeSignal:
                propAttr.async_refresh_state()

    def set_status_callback(self, callback):
        self._state_status_callback = callback

    def id_request(self):
        """Request a device ID from a device"""
        self.log.debug("Starting: devicebase.Id_Request")
        self._plm.send_standard(self._address, COMMAND_ID_REQUEST_0X10_0X00)
        self.log.debug("Ending: devicebase.Id_Request")

    def product_data_request(self):
        """equest product data from a device. \nNot supported by all devices. \nRequired after 01-Feb-2007.
        """
        self.log.debug("Starting: devicebase.product_data_request")
        self._plm.send_standard(self._address, COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00)
        self.log.debug("Ending: devicebase.product_data_request")

    def assign_to_all_link_group(self, group=0x01):
        """Assign a device to an All-Link Group. \nThe default is group 0x01."""
        self.log.debug("Starting: devicebase.assign_to_all_link_group")
        self._plm.send_standard(self._address, COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE, group)
        self.log.debug("Ending: devicebase.assign_to_all_link_group")

    def delete_from_all_link_group(self, group):
        """Delete a device to an All-Link Group."""
        self.log.debug("Starting: devicebase.delete_from_all_link_group")
        self._plm.send_standard(self._address, COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE, group)
        self.log.debug("Ending: devicebase.delete_from_all_link_group")

    def fx_username(self):
        """Get FX Username. \nOnly required for devices that support FX Commands. \nFX Addressee responds with an ED 0x0301 FX Username Response message"""
        self.log.debug("Starting: devicebase.fx_username")
        self._plm.send_standard(self._address, COMMAND_FX_USERNAME_0X03_0X01)
        self.log.debug("Ending: devicebase.fx_username")

    def device_text_string_request(self):
        """Get FX Username. \nOnly required for devices that support FX Commands. \nFX Addressee responds with an ED 0x0301 FX Username Response message"""
        self.log.debug("Starting: devicebase.device_text_string_request")
        self._plm.send_standard(self._address, COMMAND_FX_USERNAME_0X03_0X01)
        self.log.debug("Ending: devicebase.device_text_string_request")

    def enter_linking_mode(self, group=0x01):
        """Tell a device to enter All-Linking Mode.\nSame as holding down the Set button for 10 sec.\nDefault group is 0x01. \nNot supported by i1 devices."""
        self.log.debug("Starting: devicebase.enter_linking_mode")
        self._plm.send_standard(self._address, COMMAND_ENTER_LINKING_MODE_0X09_NONE, group)
        self.log.debug("Ending: devicebase.enter_linking_mode")

    def enter_unlinking_mode(self, group):
        """Unlink a device from an All-Link group. \nNot supported by i1 devices."""
        self.log.debug("Starting: devicebase.enter_unlinking_mode")
        self._plm.send_standard(self._address, COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE, group)
        self.log.debug("Ending: devicebase.enter_unlinking_mode")

    def get_engine_version(self):
        """Get the device engine version."""
        self.log.debug("Starting: devicebase.get_engine_version")
        self._plm.send_standard(self._address, COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00)
        self.log.debug("Ending: devicebase.get_engine_version")

    def ping(self):
        """Ping a device."""
        self.log.debug("Starting: devicebase.ping")
        self._plm.send_standard(self._address, COMMAND_PING_0X0F_0X00)
        self.log.debug("Ending: devicebase.ping")

    def read_aldb(self):
        raise NotImplemented

    def write_aldb(self):
        raise NotImplemented

    def _get_device_id(self, groupbutton=0x01):
        if groupbutton == 0x01:
            return self._address.hex
        else:
            return '{}_{:d}'.format(self._address.hex, groupbutton)