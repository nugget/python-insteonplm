import binascii
from insteonplm.constants import *
from .messageBase import MessageBase
from .messageFlags import MessageFlags

class X10Send(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""

    def __init__(self, rawX10, flag, acknak=None):
        super().__init__(MESSAGE_X10_MESSAGE_SEND_0X63,
                         MESSAGE_X10_MESSAGE_SEND_SIZE,
                         MESSAGE_X10_MESSAGE_SEND_RECEIVED_SIZE,
                         'Insteon Get Next All Link Record Message')

        self._rawX10 = rawX10
        self._flag = flag
        self._acknak = self._setacknak(acknak)
    
    @classmethod
    def from_raw_message(cls, rawmessage):
        return X10Send(rawmessage[2], rawmessage[3], rawmessage[4:5])

    @property
    def rawX10(self):
        return self._rawX10
    
    @property
    def flag(self):
        return self._flag

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
        return self._messageToHex(self._rawX10,
                                  self._flag,
                                  self._acknak)



