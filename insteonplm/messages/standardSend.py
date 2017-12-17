from .messageBase import MessageBase
from .extendedSend import ExtendedSend
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class StandardSend(MessageBase):
    """Insteon Standard Length Message Received 0x62"""

    code = MESSAGE_SEND_STANDARD_MESSAGE_0X62
    sendSize = MESSAGE_SEND_STANDARD_MESSAGE_SIZE
    receivedSize = MESSAGE_SEND_STANDARD_MESSAGE_RECEIVED_SIZE
    description = 'INSTEON Standard Message Send'

    def __init__(self, target, flags, cmd1, cmd2, acknak = None):

        self.address = Address(bytes([0x00,0x00,0x00]))

        if isinstance(target, Address):
            self.target = target
        else:
            self.target = Address(target)

        self._messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        msg = StandardSend(rawmessage[2:5],
                            rawmessage[5],
                            rawmessage[6],
                            rawmessage[7],
                            rawmessage[8:9])
        if msg.isextendedflag:
            msg = ExtendedSend.from_raw_message(rawmessage)
        return msg

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

