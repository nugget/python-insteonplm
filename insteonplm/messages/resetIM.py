from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class ResetIM(MessageBase):
    """Insteon Reset IM Message 0x67"""

    def __init__(self, acknak=None):
        super().__init__(MESSAGE_RESET_IM_0X67,
                         MESSAGE_RESET_IM_SIZE, 
                         MESSAGE_RESET_IM_RECEIVED_SIZE,
                         'Insteon Reset IM Message')

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return ResetIM(rawmessage[2:3])

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



