from .messageBase import MessageBase
from .messageConstants import *
import binascii

class UserReset(MessageBase):
    """Insteon User Reset Message Received 0x55"""

    code = MESSAGE_USER_RESET_DETECTED
    sendSize = MESSAGE_USER_RESET_DETECTED_SIZE
    receivedSize = MESSAGE_USER_RESET_DETECTED_SIZE
    name = 'INSTEON User Reset Message Received'


    @classmethod
    def from_raw_messsage(cls, rawmessage):
        return UserReset()

    @property
    def message(self):
        return bytearray([MESSAGE_START_CODE,
                          self.code])

    @property
    def hex(self):
        return self._messageToHex()

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)