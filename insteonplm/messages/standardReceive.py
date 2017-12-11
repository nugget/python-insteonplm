from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address
import binascii

class StandardReceive(MessageBase):
    """Insteon Standard Length Message Received 0x50"""

    code = MESSAGE_STANDARD_MESSAGE_RECEIVED
    sendSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
    receivedSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
    description = 'INSTEON Standard Message Received'

    def __init__(self, address, target, flags, cmd1, cmd2):

        self.address = Address(address)
        self.target = Address(target)
        self._messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2

    @classmethod
    def from_raw_message(cls, rawmessage):
        return StandardReceive(rawmessage[2:5], 
                               rawmessage[5:8], 
                               rawmessage[8],
                               rawmessage[9],
                               rawmessage[10])
    @property
    def hex(self):
        return self._messageToHex(self.address, 
                                  self.target,
                                  self._messageFlags,
                                  self.cmd1,
                                  self.cmd2)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)
