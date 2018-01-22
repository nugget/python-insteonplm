from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class GetImInfo(MessageBase):
    """INSTEON Get Insteon Modem Info Message 0x60"""

    def __init__(self, address=None, cat=None, subcat=None, firmware=None, acknak = None):
        super().__init__(MESSAGE_GET_IM_INFO_0X60,
                         MESSAGE_GET_IM_INFO_SIZE,
                         MESSAGE_GET_IM_INFO_RECEIVED_SIZE,
                         'INSTEON Get Insteon Modem Info Message Received')
        
        self._address = Address(address)
        self._category = cat
        self._subcategory = subcat
        self._firmware = firmware
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return GetImInfo(rawmessage[2:5],
                         rawmessage[5],
                         rawmessage[6],
                         rawmessage[7],
                         rawmessage[8])

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
    def isack(self):
        if (self._acknak is not None and self._acknak == MESSAGE_ACK):
            return True
        else:
            return False

    @property
    def isnak(self):
        if (self._acknak is not None and self._acknak == MESSAGE_NAK):
            return True
        else:
            return False

    def to_hex(self):
        return self._messageToHex(self.address,
                                    self.category,
                                    self.subcategory,
                                    self.firmware,
                                    self._acknak)


