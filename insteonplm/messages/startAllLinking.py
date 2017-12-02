from .messageBase import MessageBase
from .messageConstants import *

class StartAllLinking(MessageBase):
    """Insteon Start All Linking Message 0x64"""

    def __init__(self, linkCode, group, acknak=None):
        self.code =    MESSAGE_START_ALL_LINKING
        self.sendSize = MESSAGE_START_ALL_LINKING_SIZE
        self.receivedSize = MESSAGE_START_ALL_LINKING_RECEIVED_SIZE
        self.name = 'Insteon Start All Linking Message'

        self.linkCode = linkCode
        self.group = group

        self._acknak = self._setacknak(acknak)

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



