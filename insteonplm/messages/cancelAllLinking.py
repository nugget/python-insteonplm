from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class CancelAllLinking(MessageBase):
    """INSTEON Cancel All-Linking 0x65"""

    def __init__(self, acknak = None):
        super().__init__(MESSAGE_CANCEL_ALL_LINKING_0X65,
                         MESSAGE_CANCEL_ALL_LINKING_SIZE,
                         MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE,
                         'INSTEON Cancel All-Linking')

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return CancelAllLinking(rawmessage[2:3])

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


