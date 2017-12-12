from .messageBase import MessageBase
from .messageConstants import *
import binascii

class GetImConfiguration(MessageBase):
    """Insteon Get IM Configuration Message 0x62"""

    code = MESSAGE_GET_IM_CONFIGURATION
    sendSize = MESSAGE_GET_IM_CONFIGURATION_SIZE
    receivedSize = MESSAGE_GET_IM_CONFIGURATION_RECEIVED_SIZE
    description = 'Insteon Get IM Configuration Message'

    def __init__(self, flags = None, acknak = None):
        
        self._messageFlags = flags
        self._spare1 = None
        self._spare2 = None
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmesssage):
        return GetImConfiguration(rawmessage[2],
                                  rawmessage[5])

    @property
    def hex(self):
        if self._messageFlags is not None:
            self._spare1 = 0x00
            self._spare2 = 0x00
        return self._messageToHex(self._messageFlags,
                                  self._spare1,
                                  self._spare2,
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
