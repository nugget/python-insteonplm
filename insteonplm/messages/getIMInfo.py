from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class GetImInfo(MessageBase):
    """INSTEON Get Insteon Modem Info Message 0x60"""

    def __init__(self, address=None, cat=None, subcat=None, firmware=None, acknak = None):
        self.code = MESSAGE_GET_IM_INFO
        self.sendSize = MESSAGE_GET_IM_INFO_SIZE
        self.receivedSize = MESSAGE_GET_IM_INFO_RECEIVED_SIZE
        self.name = 'INSTEON Get Insteon Modem Info Message Received'
        
        if address is None:
            self.address = None
        else:
            self.address = Address(address)
        self.category = cat
        self.subcategory = subcat
        self.firmware = firmware
        self._acknak = self._setacknak(acknak)

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


