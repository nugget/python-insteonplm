from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class StandardSend(MessageBase):
    """Insteon Standard Length Message Received 0x62"""

    def __init__(self, target, flags, cmd1, cmd2, acknak = None):
        self.code = MESSAGE_STANDARD_MESSAGE_RECEIVED
        self.sendSize = MESSAGE_SEND_STANDARD_MESSAGE_SIZE
        self.returnSize = MESSAGE_SEND_STANDARD_MESSAGE_RECEIVED_SIZE
        self.name = 'INSTEON Standard Message Send'

        self.address = Address(bytes([0x00,0x00,0x00]))

        if isinstance(target, Address):
            self.address = target
        else:
            self.address = Address(target)

        self._messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2

        self._acknak = self._setacknak(acknak)

    @property
    def hex(self):
        return self._messageToHex(self.target,
                                  self._messageFlags,
                                  self.cmd1,
                                  self.cmd2,
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

