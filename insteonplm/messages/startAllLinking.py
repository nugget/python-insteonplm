from .messageBase import MessageBase
from .messageConstants import *

class StartAllLinking(MessageBase):
    """Insteon Start All Linking Message 0x64"""

    code =    MESSAGE_START_ALL_LINKING
    sendSize = MESSAGE_START_ALL_LINKING_SIZE
    receivedSize = MESSAGE_START_ALL_LINKING_RECEIVED_SIZE
    description = 'Insteon Start All Linking Message'

    def __init__(self, linkCode, group, acknak=None):

        self.linkCode = linkCode
        self.group = group

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return StartAllLinking(rawmessage[2], rawmessage[3], rawmessage[4:5])

    @property
    def hex(self):
        return self._messageToHex(self.linkCode,
                                  self.group,
                                  self._acknak)

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



