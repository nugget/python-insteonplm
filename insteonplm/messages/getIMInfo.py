from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class GetImInfo(MessageBase):
    """INSTEON Get Insteon Modem Info Message 0x60"""

    def __init__(self, address=None, cat=None, subcat=None, firmware=None):
        self.code = MESSAGE_GET_IM_INFO
        self.sendSize = MESSAGE_GET_IM_INFO_SIZE
        self.returnSize = MESSAGE_GET_IM_INFO_RECEIVED_SIZE
        self.name = 'INSTEON Get Insteon Modem Info Message Received'
        
        self.address = Address(address)
        self.category = cat
        self.subcategory = subcat
        self.firmware = firmware

    @property
    def hex(self):
        return self._messageToHex(self.address,
                                    self.category,
                                    self.subcategory,
                                    self.firmware)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)


