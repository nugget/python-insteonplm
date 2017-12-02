from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class ExtendedReceive(MessageBase):
    """Insteon Extended Length Message Received 0x51"""

    def __init__(self, address, target, flags, cmd1, cmd2, userdata):
        self.code = MESSAGE_EXTENDED_MESSAGE_RECEIVED
        self.sendSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
        self.receivedSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
        self.name = 'INSTEON Extended Message Received'

        self.address = Address(address)
        self.target = Address(target)
        self._messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        self.userdata = userdata

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
