from insteonplm.address import Address
from insteonplm.messages.messageBase import MessageBase
from insteonplm.constants import *

class BaseDevice(object):
    """INSTEON Device"""

    def __init__(self, plm, address, cat, subcat, firmware, description, model):
        self.plm = plm
        self.address = Address(address)
        self.cat = cat
        self.subcat = subcat
        self.firmware = firmware
        self.description = description
        self.model = model  

        self._messageHandlers = {}
        self._commandHandlers = {}

        self.register_message_handler(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, _standard_or_extended_message_received)
        self.register_message_handler(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, _standard_or_extended_message_received)
        self.register_message_handler(MESSAGE_SEND_STANDARD_MESSAGE_0X62, _send_standard_or_extended_message_acknak)
        self.register_message_handler(MESSAGE_SEND_EXTENDED_MESSAGE_0X62, _send_standard_or_extended_message_acknak)

    def register_message_handler(self, messagecode, callback):
        self._messageHanlders[code] =  callback

    def register_command_handler(self, commandtuple, callback):
        self._commandHandlers[commandtuple] = callback

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

    @classmethod
    def prod_data_in_aldb(self):
        """True if Product data (cat, subcat, product_key) is stored in the PLM ALDB.
           False if product data must be aquired via a Device ID message or from a Product Data Request command.
           
           Very few devices store their product data in the ALDB, therefore False is the default.
           The common reason to store product data in the ALDB is for one way devices or battery opperated devices where 
           the ability to send a command request is limited.
           
           To override this setting create a device specific class and override this class method."""
        return False

    def _standard_or_extended_message_received(self, msg):
        commandtuple = {'cmd1':msg.cmd1, 'cmd2':msg.cmd2}
        try:
            callback = self._commandHandlers[commandtuple]
        except KeyError:
            try:
                commandtuple = {'cmd1':msg.cmd1, 'cmd2':None}
                callback = self._commandHandlers[commandtuple]
            except KeyError:
                raise KeyError
        callback(msg)

    def _send_standard_or_extended_message_acknak(self, msg):
        commandtuple = {'cmd1': msg.cmd1, 'cmd2': msg.cmd2}
        try:
            callback = self._commandHandlers[commandtuple]
        except KeyError:
            try:
                commandtuple = {'cmd1':msg.cmd1, 'cmd2':None}
                callback = self._commandHandlers[commandtuple]
            except KeyError:
                raise KeyError
        callback(msg)