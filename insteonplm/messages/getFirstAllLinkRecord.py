from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class GetFirstAllLinkRecord(MessageBase):
    """Insteon Get First All Link Record Message 0x69"""

    def __init__(self, acknak=None):
        super().__init__(MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69,
                         MESSAGE_GET_FIRST_ALL_LINK_RECORD_SIZE, 
                         MESSAGE_GET_FIRST_ALL_LINK_RECORD_RECEIVED_SIZE,
                         'Insteon Get First All Link Record Message')

        self._acknak = self._setacknak(acknak)


    @classmethod
    def from_raw_message(cls, rawmessage):
        return GetFirstAllLinkRecord(rawmessage[2:3])

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
        return self._messageToHex(self._acknak)
