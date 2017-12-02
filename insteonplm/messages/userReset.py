from .messageBase import MessageBase
from .messageConstants import *

class UserReset(MessageBase):
    """Insteon User Reset Message Received 0x55"""
    def __init__(self):
        self.code = MESSAGE_USER_RESET_DETECTED
        self.sendSize = MESSAGE_USER_RESET_DETECTED_SIZE
        self.receivedSize = MESSAGE_USER_RESET_DETECTED_SIZE
        self.name = 'INSTEON User Reset Message Received'

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