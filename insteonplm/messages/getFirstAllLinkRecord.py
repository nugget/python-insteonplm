from .messageBase import MessageBase
from .messageConstants import *

class GetFirstAllLinkRecord(MessageBase):
    """Insteon Get First All Link Record Message 0x69"""

    def __init__(self, acknak=None):
        self.code = MESSAGE_GET_FIRST_ALL_LINK_RECORD
        self.sendSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_SIZE
        self.receivedSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_RECEIVED_SIZE
        self.name = 'Insteon Get First All Link Record Message'

        self._acknak = self._setacknak(acknak)


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
