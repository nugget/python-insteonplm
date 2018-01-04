from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class CancelAllLinking(MessageBase):
    """INSTEON Cancel All-Linking 0x65"""

    code = MESSAGE_CANCEL_ALL_LINKING_0X65
    sendSize = MESSAGE_CANCEL_ALL_LINKING_SIZE
    receivedSize = MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE
    description = 'INSTEON Cancel All-Linking'

    def __init__(self, acknak = None):

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return CancelAllLinking(rawmessage[2:3])

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


