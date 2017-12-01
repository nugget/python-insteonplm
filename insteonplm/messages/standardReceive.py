from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class StandardReceive(MessageBase):
    """Insteon Standard Length Message Received 0x50"""

    def __init__(self, address, target, flags, cmd1, cmd2):
        self.code = MESSAGE_STANDARD_MESSAGE_RECEIVED
        self.sendSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
        self.returnSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
        self.name = 'INSTEON Standard Message Received'

        self.address = Address(address)
        self.target = Address(target)
        self._messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2

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
