from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class StartAllLinking(MessageBase):
    """Insteon Start All Linking Message 0x64"""

    def __init__(self, linkCode, group, acknak=None):
        super().__init__(MESSAGE_START_ALL_LINKING_0X64,
                         MESSAGE_START_ALL_LINKING_SIZE,
                         MESSAGE_START_ALL_LINKING_RECEIVED_SIZE,
                         'Insteon Start All Linking Message')

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
        return self._messageToHex(self._linkCode,
                                  self._group,
                                  self._acknak)


