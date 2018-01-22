import binascii
from insteonplm.constants import *
from insteonplm.address import Address
from .messageBase import MessageBase
from .messageFlags import MessageFlags

class StandardReceive(MessageBase):
    """Insteon Standard Length Message Received 0x50"""

    def __init__(self, address, target, flags, cmd1, cmd2):
        super().__init__(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50,
                         MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE, 
                         MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE,
                         'INSTEON Standard Message Received')

        self._address = Address(address)
        self._target = Address(target)
        self._messageFlags = MessageFlags(flags)
        self._cmd1 = cmd1
        self._cmd2 = cmd2

    @classmethod
    def from_raw_message(cls, rawmessage):
        return StandardReceive(rawmessage[2:5], 
                               rawmessage[5:8], 
                               rawmessage[8],
                               rawmessage[9],
                               rawmessage[10])

    @property
    def address(self):
        return self._address

    @property
    def target(self):
        return self._target

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
    def targetLow(self):
        if self.target.addr is not None and self._messageFlags.isBroadcast:
            return self.target.bytes[0]
        else:
            return None

    @property
    def targetMed(self):
        if self.target.addr is not None and self._messageFlags.isBroadcast:
            return self.target.bytes[1]
        else:
            return None

    @property
    def targetHi(self):
        if self.target.addr is not None and self._messageFlags.isBroadcast:
            return self.target.bytes[2]
        else:
            return None

    def to_hex(self):
        return self._messageToHex(self._address, 
                                  self._target,
                                  self._messageFlags.to_byte(),
                                  self._cmd1,
                                  self._cmd2)