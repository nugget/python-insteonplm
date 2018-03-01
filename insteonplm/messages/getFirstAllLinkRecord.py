from insteonplm.messages import MessageBase
from insteonplm.constants import *
import binascii

class GetFirstAllLinkRecord(MessageBase):
    """Insteon Get First All Link Record Message 0x69"""
    
    _code = MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69
    _sendSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_SIZE
    _receivedSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_RECEIVED_SIZE
    _description = 'Insteon Get First All Link Record Message'


    def __init__(self, acknak=None):
        self._acknak = self._setacknak(acknak)


    @classmethod
    def from_raw_message(cls, rawmessage):
        return GetFirstAllLinkRecord(rawmessage[2:3])

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
