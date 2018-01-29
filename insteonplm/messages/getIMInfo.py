from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class GetImInfo(MessageBase):
    """INSTEON Get Insteon Modem Info Message 0x60"""
    
    _code = MESSAGE_GET_IM_INFO_0X60
    _sendSize = MESSAGE_GET_IM_INFO_SIZE
    _receivedSize = MESSAGE_GET_IM_INFO_RECEIVED_SIZE
    _description = 'INSTEON Get Insteon Modem Info Message Received'
        

    def __init__(self, address=None, cat=None, subcat=None, firmware=None, acknak = None):
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
    def acknak(self):
        return self._acknak

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

    def _message_properties(self):
        return [{'address': self._address},
                {'category': self._category},
                {'subcategory': self._subcategory},
                {'firmware': self._firmware},
                {'acknak': self._acknak}]


