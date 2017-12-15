from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class AllLinkComplete(MessageBase):
    """INSTEON ALL-Linking Completed Message 0x53"""

    code = MESSAGE_ALL_LINKING_COMPLETED_0X53
    sendSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
    receivedSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
    description = 'INSTEON ALL-Linking Completed Message Received'

    def __init__(self, linkcode, group, address, cat, subcat, firmware):

        # ALL-Linking Complete
        self.linkcode = linkcode
        self.group = group
        self.address = Address(address)
        self.category = cat
        self.subcategory = subcat
        self.firmware = firmware

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkComplete(rawmessage[2],
                               rawmessage[3],
                               rawmessage[4:7],
                               rawmessage[7],
                               rawmessage[8],
                               rawmessage[9])
    @property
    def hex(self):
        return self._messageToHex(self.linkcode,
                                  self.group,
                                  self.address,
                                  self.category,
                                  self.subcategory, 
                                  self.firmware)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

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


