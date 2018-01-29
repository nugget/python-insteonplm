from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class StartAllLinking(MessageBase):
    """Insteon Start All Linking Message 0x64"""
    
    _code = MESSAGE_START_ALL_LINKING_0X64
    _sendSize = MESSAGE_START_ALL_LINKING_SIZE
    _receivedSize = MESSAGE_START_ALL_LINKING_RECEIVED_SIZE
    _description = 'Insteon Start All Linking Message'


    def __init__(self, linkCode, group, acknak=None):
        self._linkCode = linkCode
        self._group = group

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return StartAllLinking(rawmessage[2], rawmessage[3], rawmessage[4:5])

    @property
    def linkCode(self):
        return self._linkCode

    @property
    def group(self):
        return self._group

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
        return [{'linkCode': self._linkCode},
                {'group': self._group},
                {'acknak': self._acknak}]


