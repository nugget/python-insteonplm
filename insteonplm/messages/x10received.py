from .messageBase import MessageBase
from .messageConstants import *

class X10Received(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""

    code = MESSAGE_X10_MESSAGE_RECEIVED
    sendSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    receivedSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    description = 'Insteon Get Next All Link Record Message'

    def __init__(self, rawX10, flag):

        self.rawX10 = rawX10
        self.flag = flag

    @property
    def hex(self):
        return self._messageToHex(self.rawX10,
                                  self.flag)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)



