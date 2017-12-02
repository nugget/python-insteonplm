from .messageBase import MessageBase
from .messageConstants import *

class X10Send(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""

    def __init__(self, rawX10, flag, acknak=None):
        self.code = MESSAGE_X10_MESSAGE_SEND
        self.sendSize = MESSAGE_X10_MESSAGE_SEND_SIZE
        self.receivedSize = MESSAGE_X10_MESSAGE_SEND_RECEIVED_SIZE
        self.name = 'Insteon Get Next All Link Record Message'

        self.rawX10 = rawX10
        self.flag = flag
        self._acknak = self._setacknak(acknak)

    @property
    def hex(self):
        return self._messageToHex(self.rawX10,
                                  self.flag,
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



