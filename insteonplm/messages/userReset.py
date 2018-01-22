from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class UserReset(MessageBase):
    """Insteon User Reset Message Received 0x55"""

    def __init__(self):
        super().__init__(MESSAGE_USER_RESET_DETECTED_0X55,
                         MESSAGE_USER_RESET_DETECTED_SIZE,
                         MESSAGE_USER_RESET_DETECTED_SIZE,
                         'INSTEON User Reset Message Received')


    @classmethod
    def from_raw_messsage(cls, rawmessage):
        return UserReset()

    def to_hex(self):
        return self._messageToHex()