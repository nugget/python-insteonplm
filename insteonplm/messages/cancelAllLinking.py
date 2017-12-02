from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class CancelAllLinking(MessageBase):
    """INSTEON Cancel All-Linking 0x65"""

    def __init__(self, acknak = None):
        self.code = MESSAGE_CANCEL_ALL_LINKING
        self.sendSize = MESSAGE_CANCEL_ALL_LINKING_SIZE
        self.receivedSize = MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE
        self.name = 'INSTEON Cancel All-Linking'

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


