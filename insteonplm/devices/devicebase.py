import logging
import asyncio
import datetime

from insteonplm.address import Address
from insteonplm.messages import (StandardReceive, StandardSend,
                                 ExtendedReceive, ExtendedSend,
                                 MessageBase)
from insteonplm.constants import *
from insteonplm.messagecallback import MessageCallback
from .stateList import StateList
from .states.stateBase import StateBase

class DeviceBase(object):
    """INSTEON Device"""

    def __init__(self, plm, address, cat, subcat, product_key=0x00, description='', model=''):
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

        self._last_communication_received = datetime.datetime(1,1,1,1,1,1)
        self._product_data_in_aldb = False
        self._stateList = StateList()
        self._send_msg_lock = asyncio.Lock(loop=self._plm.loop)

        self._plm.message_callbacks.add(StandardReceive.template(address=self._address), self._receive_message)

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
    def id(self):
        return self._address

    @property
    def states(self):
        return self._stateList

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
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None):
        return cls(plm, address, cat, subcat, product_key, description, model)

    def _receive_message(self, msg):
        self.log.debug('Starting DeviceBase.receive_message')
        self._last_communication_received = datetime.datetime.now()
        self.log.debug('Ending DeviceBase.receive_message')

    def async_refresh_state(self):
        for state in self._stateList:
            self._stateList[state].async_refresh_state()

    #def set_status_callback(self, callback):
    #    self._state_status_callback = callback

    #def add_message_callback(self, msg, callback, override=False):
    #    self._message_callbacks.add(msg, callback, override)

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
