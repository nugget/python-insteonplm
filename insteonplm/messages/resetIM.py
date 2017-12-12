from .messageBase import MessageBase
from .messageConstants import *

class ResetIM(MessageBase):
    """Insteon Reset IM Message 0x67"""

    code = MESSAGE_RESET_IM
    sendSize = MESSAGE_RESET_IM_SIZE
    receivedSize = MESSAGE_RESET_IM_RECEIVED_SIZE
    description = 'Insteon Reset IM Message'

    def __init__(self, acknak=None):

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return ResetIM(rawmessage[2:3])

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



