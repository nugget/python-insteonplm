from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class AllLinkComplete(MessageBase):
    """INSTEON ALL-Linking Completed Message 0x53"""

    _code = MESSAGE_ALL_LINKING_COMPLETED_0X53
    _sendSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
    _receivedSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
    _description = 'INSTEON ALL-Linking Completed Message Received'

    def __init__(self, linkcode, group, address, cat, subcat, firmware):
        # ALL-Linking Complete
        self._linkcode = linkcode
        self._group = group
        self._address = Address(address)
        self._category = cat
        self._subcategory = subcat
        self._firmware = firmware

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkComplete(rawmessage[2],
                               rawmessage[3],
                               rawmessage[4:7],
                               rawmessage[7],
                               rawmessage[8],
                               rawmessage[9])
    
    @property
    def linkcode(self):
        return self._linkcode
    
    @property
    def group(self):
        return self._group
    
    @property
    def address(self):
        return self._address
    
    @property
    def category(self):
        return self._category
    
    @property
    def subcategory(self):
        return self._subcategory
    
    @property
    def firmware(self):
        return self._firmware

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

    def _message_properties(self):
        return [{'linkcode': self._linkcode},
                {'group': self._group},
                {'address': self._address},
                {'category': self._category},
                {'subcategory': self._subcategory}, 
                {'firmware': self._firmware}]


