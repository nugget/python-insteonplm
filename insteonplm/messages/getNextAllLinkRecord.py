from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class GetNextAllLinkRecord(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""

    code = MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A
    sendSize = MESSAGE_GET_NEXT_ALL_LINK_RECORD_SIZE
    receivedSize = MESSAGE_GET_NEXT_ALL_LINK_RECORD_RECEIVED_SIZE
    description = 'Insteon Get Next All Link Record Message'


    def __init__(self, acknak=None):
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return GetNextAllLinkRecord(rawmessage[2:3])

    @property
    def hex(self):
        return self._messageToHex(self._acknak)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

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



