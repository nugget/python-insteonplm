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

        if (acknak is not None and len(acknak) > 0):
            if (isinstance(acknak, bytearray)):
                self._acknak = acknak[0]
            else:
                self._acknak = acknak
        else:
            self._acknak = None

    @property
    def message(self):
        msg = bytearray([0x02,
                         self.code,
                         self.target.hex,
                         self._messageFlags,
                         self.cmd1,
                         self.cmd2])
        if self.isack or self.isnak:
            msg.append(self.acknak)

        return msg

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

