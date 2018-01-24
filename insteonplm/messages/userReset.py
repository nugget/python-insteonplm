from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class UserReset(MessageBase):
    """Insteon User Reset Message Received 0x55"""
    
    _code = MESSAGE_USER_RESET_DETECTED_0X55
    _sendSize = MESSAGE_USER_RESET_DETECTED_SIZE
    _receivedSize = MESSAGE_USER_RESET_DETECTED_SIZE
    _description = 'INSTEON User Reset Message Received'

    @classmethod
    def from_raw_messsage(cls, rawmessage):
        return UserReset()

    def _message_properties(self):
        return []