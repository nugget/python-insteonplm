import binascii
from insteonplm.constants import *
from .messageBase import MessageBase
from .messageFlags import MessageFlags

class X10Send(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""
    
    _code = MESSAGE_X10_MESSAGE_SEND_0X63
    _sendSize = MESSAGE_X10_MESSAGE_SEND_SIZE
    _receivedSize = MESSAGE_X10_MESSAGE_SEND_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'


    def __init__(self, rawX10, flag, acknak=None):
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
    def acknak(self):
        return self._acknak

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

    def _message_properties(self):
        return [{'rawX10': self._rawX10},
                {'flag': self._flag},
                {'acknak': self._acknak}]



