import logging

from insteonplm.address import Address
from insteonplm.messages.messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.messagecallback import MessageCallback

class DeviceBase(object):
    """INSTEON Device"""

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        self._plm = plm
        self._address = Address(address)
        self._cat = cat
        self._subcat = subcat
        self._product_key = product_key
        self._description = description
        self._model = model 
        self._groupbutton = groupbutton

        self.log = logging.getLogger(__name__)

        self._product_data_in_aldb = False
        self._message_callbacks = MessageCallback()

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
        if self._groupbutton == 0x01:
            return self._address.hex
        else:
            return '{}_{:d}'.format(self._address.hex, self._groupbutton)
    
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

    def processMessage(self, message):
        raise NotImplemented

    def AssignToALLLinkGroup(self, group):
        raise NotImplemented

    def DeleteFromALLLinkGroup(self, group):
        raise NotImplemented

    def ProductDataRequest(self):
        raise NotImplemented

    def FxUsername(self):
        raise NotImplemented

    def DeviceTextStringRequest(self):
        raise NotImplemented

    def EnterLinkingMode(self, group):
        raise NotImplemented

    def EnterUnlinkingMode(self, group):
        raise NotImplemented

    def GetEngineVersion(self):
        raise NotImplemented

    def Ping(self):
        raise NotImplemented

    def IdRequest(self):
        raise NotImplemented

    def ReadALDB(self):
        raise NotImplemented

    def WriteALDB(self):
        raise NotImplemented

    @property
    def prod_data_in_aldb(self):
        """True if Product data (cat, subcat, product_key) is stored in the PLM ALDB.
           False if product data must be aquired via a Device ID message or from a Product Data Request command.
           
           Very few devices store their product data in the ALDB, therefore False is the default.
           The common reason to store product data in the ALDB is for one way devices or battery opperated devices where 
           the ability to send a command request is limited.
           
           To override this setting create a device specific class and override this class method."""
        return self._product_data_in_aldb
