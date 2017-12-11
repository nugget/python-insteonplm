from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address
import binascii

class ExtendedReceive(MessageBase):
    """Insteon Extended Length Message Received 0x51"""

    code = MESSAGE_EXTENDED_MESSAGE_RECEIVED
    sendSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    receivedSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    description = 'INSTEON Extended Message Received'

    def __init__(self, address, target, flags, cmd1, cmd2, userdata):

        self.address = Address(address)
        self.target = Address(target)
        self._messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        self.userdata = userdata

    @classmethod
    def from_raw_message(cls, rawmessage):
        return ExtendedReceive(rawmessage[2:5], 
                               rawmessage[5:8],
                               rawmessage[8],
                               rawmessage[9],
                               rawmessage[10],
                               rawmessage[11:25])
    @property
    def hex(self):
        return self._messageToHex(self.address, 
                                  self.target, 
                                  self._messageFlags, 
                                  self.cmd1, 
                                  self.cmd2,
                                  self.userdata)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)
