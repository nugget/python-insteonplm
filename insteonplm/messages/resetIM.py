from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class ResetIM(MessageBase):
    """Insteon Reset IM Message 0x67"""
    
    _code = MESSAGE_RESET_IM_0X67
    _sendSize = MESSAGE_RESET_IM_SIZE
    _receivedSize = MESSAGE_RESET_IM_RECEIVED_SIZE
    _description = 'Insteon Reset IM Message'


    def __init__(self, acknak=None):
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return ResetIM(rawmessage[2:3])

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



