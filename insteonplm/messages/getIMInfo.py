from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class GetImInfo(MessageBase):
    """INSTEON Get Insteon Modem Info Message 0x60"""

    code = MESSAGE_GET_IM_INFO_0X60
    sendSize = MESSAGE_GET_IM_INFO_SIZE
    receivedSize = MESSAGE_GET_IM_INFO_RECEIVED_SIZE
    description = 'INSTEON Get Insteon Modem Info Message Received'

    def __init__(self, address=None, cat=None, subcat=None, firmware=None, acknak = None):
        
        if address is None:
            self.address = None
        else:
            self.address = Address(address)
        self.category = cat
        self.subcategory = subcat
        self.firmware = firmware
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return GetImInfo(rawmessage[2:5],
                         rawmessage[5],
                         rawmessage[6],
                         rawmessage[7],
                         rawmessage[8])

    @property
    def hex(self):
        return self._messageToHex(self.address,
                                    self.category,
                                    self.subcategory,
                                    self.firmware,
                                    self._acknak)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

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


