from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class AllLinkRecordResponse(MessageBase):
    """INSTEON ALL-Link Record Response 0x57"""

    def __init__(self, flags, group, address, linkdata1, linkdata2, linkdata3):
        self.code = MESSAGE_ALL_LINK_RECORD_RESPONSE
        self.sendSize = MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE
        self.returnSize = MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE
        self.name = 'INSTEON ALL-Link Record Response'

        # ALL-Link Record Response
        self.__controlFlags = flags
        self.group = group

        if isinstance(address, Address):
            self.address = address
        else:
            #self.address = Address(rawmessage[2:5])
            self.address = Address(address)

        self.linkdata1 = linkdata1
        self.linkdata2 = linkdata2
        self.linkdata3 = linkdata3

    @property
    def message(self):
        return bytearray([0x02,
                          self.code,
                          self.__allLinkFlags,
                          self.group,
                          self.address.hex,
                          self.linkdata1,
                          self.linkdata2,
                          self.linkdata3])

    @property
    def isrecordinuse(self):
        return (self.__controlFlags & self.CONTROL_FLAG_RECORD_IN_USE) == self.CONTROL_FLAG_RECORD_IN_USE

    @property
    def iscontroller(self):
        return (self.__controlFlags & self.CONTROL_FLAG_CONTROLLER) == self.CONTROL_FLAG_CONTROLER

    @property
    def isslave(self):
        return not self.iscontroller
