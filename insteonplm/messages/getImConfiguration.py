import binascii
from insteonplm.constants import *
from .messageBase import MessageBase
from .messageFlags import MessageFlags

class GetImConfiguration(MessageBase):
    """Insteon Get IM Configuration Message 0x62"""
    
    _code = MESSAGE_GET_IM_CONFIGURATION_0X73
    _sendSize = MESSAGE_GET_IM_CONFIGURATION_SIZE
    _receivedSize = MESSAGE_GET_IM_CONFIGURATION_RECEIVED_SIZE
    _description = 'Insteon Get IM Configuration Message'
        

    def __init__(self, flags = None, acknak = None):
        self._imConfigurationFlags = flags
        self._spare1 = None
        self._spare2 = None
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmesssage):
        return GetImConfiguration(rawmessage[2],
                                  rawmessage[5])

    @property
    def ImConfigurationFlags(self):
        return self._imConfigurationFlags

    @property
    def isack(self):
        if (self._acknak is not None and self._acknak == MESSAGE_ACK):
            return True
        else:
            return False

    @property
    def isnak(self):
        if (self._acknak is not None and self._acknak == MESSAGE_NAK):
            return True
        else:
            return False

    def to_hex(self):
        if self._imConfigurationFlags is not None:
            self._spare1 = 0x00
            self._spare2 = 0x00
        return self._messageToHex(self._imConfigurationFlags,
                                  self._spare1,
                                  self._spare2,
                                  self._acknak)
