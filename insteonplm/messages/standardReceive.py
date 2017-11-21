from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class StandardReceive(MessageBase):
    """Insteon Standard Length Message Received 0x50"""

    def __init__(self, address, target, __messageFlags, cmd1, cmd2):
        self.code = MESSAGE_STANDARD_MESSAGE_RECEIVED
        self.sendSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
        self.returnSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
        self.name = 'INSTEON Standard Message Received'

        if isinstance(address, Address):
            self.address = address
        else:
            self.address = Address(address)

        if isinstance(target, Address):
            self.target = target
        else:
            self.target = Address(target)

        self.__messageFlags = __messageFlags
        self.cmd1 = cmd1
        self.cmd2 = cmd2

    @property
    def message(self):
        msg = bytearray([0x02,
                         self.code,
                         self.address.hex, 
                         self.target.hex, 
                         self.__messageFlags, 
                         self.cmd1, 
                         self.cmd2])
        return msg
