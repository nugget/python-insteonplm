import binascii
from insteonplm.constants import *
from insteonplm.address import Address
from .messageBase import MessageBase
from .extendedSend import ExtendedSend
from .messageFlags import MessageFlags

class StandardSend(MessageBase):
    """Insteon Standard Length Message Received 0x62"""
    
    _code = MESSAGE_SEND_STANDARD_MESSAGE_0X62
    _sendSize = MESSAGE_SEND_STANDARD_MESSAGE_SIZE
    _receivedSize = MESSAGE_SEND_STANDARD_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Standard Message Send'


    def __init__(self, address, cmd1, cmd2, flags=0x00,  acknak = None):
        self._address = Address(address)
        self._messageFlags = MessageFlags(flags)
        self._cmd1 = cmd1
        self._cmd2 = cmd2

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        msg = StandardSend(rawmessage[2:5],
                            rawmessage[6],
                            rawmessage[7],
                            rawmessage[5],
                            rawmessage[8:9])
        if msg.flags.isExtended:
            if len(rawmessage) >= ExtendedSend.receivedSize:
                msg = ExtendedSend.from_raw_message(rawmessage)
            else:
                msg = None
        return msg

    @property
    def address(self):
        return self._address

    @property
    def cmd1(self):
        return self._cmd1

    @property
    def cmd2(self):
        return self._cmd2

    @property
    def flags(self):
        return self._messageFlags

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
        return self._messageToHex(self.address,
                                  self._messageFlags.to_byte(),
                                  self.cmd1,
                                  self.cmd2,
                                  self._acknak)