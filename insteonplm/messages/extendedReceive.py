from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class ExtendedReceive(MessageBase):
    """Insteon Extended Length Message Received 0x51"""
    def __init__(self, address, target, flags, cmd1, cmd2, userdata):
        self.code = 0x51
        self.sendSize = 25
        self.returnSize = 25
        self.name = 'INSTEON Extended Message Received'

        if isinstance(address, Address):
            self.address = address
        else:
            self.address = Address(address)

        if isinstance(target, Address):
            self.target = target
        else:
            self.target = Address(target)

        self.__messageFlags = flags
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        self.userdata = userdata

    @property
    def rawmessage(self):
        message = bytearray([0x02, 
                             self.code, 
                             self.address, 
                             self.target, 
                             self.__messageFlags, 
                             self.cmd1, 
                             self.cmd2,
                             self.userdata])
        return message

