from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class AllLinkComplete(MessageBase):
    """INSTEON ALL-Linking Completed Message 0x53"""
    def __init__(self, linkcode, group, address, cat, subcat, firmware):

        self.code = MESSAGE_ALL_LINKING_COMPLETED
        self.sendSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
        self.returnSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
        self.name = 'INSTEON ALL-Linking Completed Message Received'

        # ALL-Linking Complete
        self.linkcode = linkcode
        self.group = group

        if isinstance(address, Address):
            self.address = address
        else:
            self.address = Address(address)

        self.category = cat
        self.subcategory = subcat
        self.firmware = firmware

    @property
    def message(self):
        msg = bytearray([0x02,
                         self.code,
                         self.linkcode,
                         self.group,
                         self.address.hex,
                         self.category,
                         self.subcategory,
                         self.firmware])
        return msg

    @property
    def isresponder(self):
        if self.linkcode == 0:
            return True
        else:
            return False

    @property
    def iscontroller(self):
        if self.linkcode == 1:
            return True
        else:
            return False

    @property
    def isdeleted(self):
        if self.linkcode == 0xFF:
            return True
        else:
            return False


