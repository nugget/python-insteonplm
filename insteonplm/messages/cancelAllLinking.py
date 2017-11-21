from .messageBase import MessageBase
from .messageConstants import *
from .. import Address

class CancelAllLinking(Message):
    """INSTEON Cancel All-Linking"""

    def __init__(self), acknak = None):
        self.code = MESSAGE_CANCEL_ALL_LINKING
        self.sendSize = MESSAGE_CANCEL_ALL_LINKING_SIZE
        self.returnSize = MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE
        self.name = 'INSTEON Cancel All-Linking'

        self.acknak = acknak

    @property
    def message(self):
        return bytearray(0x02,
                         self.code)

    @property
    def isack(self):
        if self.acknak is not None && self.acknack == MESSAGE_ACK:
            return True
        else:
            return False

    @property
    def isnak(self):
        if self.acknak is not None && self.acknack == MESSAGE_NAK:
            return True
        else:
            return False


