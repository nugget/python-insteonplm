from insteonplm.address import Address
from insteonplm.messages.messageBase import MessageBase
from insteonplm.constants import *

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

        self._product_data_in_aldb = False
        self._messageHandlers = {}
        self._commandHandlers = {}

        self.register_message_handler(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, self._standard_or_extended_message_received)
        self.register_message_handler(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, self._standard_or_extended_message_received)
        self.register_message_handler(MESSAGE_SEND_STANDARD_MESSAGE_0X62, self._send_standard_or_extended_message_acknak)
        self.register_message_handler(MESSAGE_SEND_EXTENDED_MESSAGE_0X62, self._send_standard_or_extended_message_acknak)

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

    def id(self):
        if self._groupbutton == 0x01:
            return self._address
        else:
            return '{}_{:d}'.format(self._address, self._groupbuttons)
    
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

    def register_message_handler(self, messagecode, callback):
        self._messageHandlers[messagecode] =  callback

    def register_command_handler(self, commandtuple, callback):
        self._commandHandlers[self._command_tuple_to_string(**commandtuple)] = callback

    def receive_message(self, msg):
        callback = self._messageHandlers[msg.code]
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

    def prod_data_in_aldb(self):
        """True if Product data (cat, subcat, product_key) is stored in the PLM ALDB.
           False if product data must be aquired via a Device ID message or from a Product Data Request command.
           
           Very few devices store their product data in the ALDB, therefore False is the default.
           The common reason to store product data in the ALDB is for one way devices or battery opperated devices where 
           the ability to send a command request is limited.
           
           To override this setting create a device specific class and override this class method."""
        return self._product_data_in_aldb

    def _standard_or_extended_message_received(self, msg):
        commandtuple = {'cmd1':msg.cmd1, 'cmd2':msg.cmd2}
        try:
            callback = self._commandHandlers[self._command_tuple_to_string(**commandtuple)]
        except KeyError:
            try:
                commandtuple = {'cmd1':msg.cmd1, 'cmd2':None}
                callback = self._commandHandlers[self._command_tuple_to_string(**commandtuple)]
            except KeyError:
                raise KeyError
        callback(msg)

    def _send_standard_or_extended_message_acknak(self, msg):
        commandtuple = {'cmd1': msg.cmd1, 'cmd2': msg.cmd2}
        try:
            callback = self._commandHandlers[self._command_tuple_to_string(**commandtuple)]
        except KeyError:
            try:
                commandtuple = {'cmd1':msg.cmd1, 'cmd2':None}
                callback = self._commandHandlers[self._command_tuple_to_string(**commandtuple)]
            except KeyError:
                raise KeyError
        callback(msg)

    def _command_tuple_to_string(self, **kwarg):
        for key in kwarg:
            if key == 'cmd1':
                cmd1 = kwarg[key]
            else:
                cmd2 = kwarg[key]
        txtcmd2 = 'None'
        if cmd2 is not None:
            txtcmd2 = '{:02x}'.format(cmd2)
        
        return 'cmd1: {0:02x}, cmd2: {1}'.format(cmd1, txtcmd2)