from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class GetImInfo(MessageBase):
    """INSTEON Get Insteon Modem Info Message 0x60"""

    def __init__(self, address, cat, subcat, firmware):
        self.code = 0x60
        self.sendSize = 2
        self.returnSize = 9
        self.name = 'INSTEON Get Insteon Modem Info Message Received'
        

        if isinstance(address, Address):
            self.address = address
        else:
            #self.address = Address(rawmessage[2:5])
            self.address = Address(address)
        self.category = cat
        self.subcategory = subcat
        self.firmware = firmware



