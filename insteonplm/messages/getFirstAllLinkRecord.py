from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class GetFirstAllLinkRecord(MessageBase):
    """Insteon Get First All Link Record Message 0x69"""

    code = MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69
    sendSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_SIZE
    receivedSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_RECEIVED_SIZE
    description = 'Insteon Get First All Link Record Message'

    def __init__(self, acknak=None):

        self._acknak = self._setacknak(acknak)


    @classmethod
    def from_raw_message(cls, rawmessage):
        return GetFirstAllLinkRecord(rawmessage[2:3])

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
