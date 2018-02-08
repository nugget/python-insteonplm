from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class CancelAllLinking(MessageBase):
    """INSTEON Cancel All-Linking 0x65"""
    
    _code = MESSAGE_CANCEL_ALL_LINKING_0X65
    _sendSize = MESSAGE_CANCEL_ALL_LINKING_SIZE
    _receivedSize = MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE
    _description = 'INSTEON Cancel All-Linking'


    def __init__(self, acknak = None):
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return CancelAllLinking(rawmessage[2:3])

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
        return [{'acknak': self._acknak}]


