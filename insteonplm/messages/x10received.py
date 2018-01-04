from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class X10Received(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""

    code = MESSAGE_X10_MESSAGE_RECEIVED_0X52
    sendSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    receivedSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    description = 'Insteon Get Next All Link Record Message'

    def __init__(self, rawX10, flag):

        self.rawX10 = rawX10
        self.flag = flag

    @classmethod
    def from_raw_message(cls, rawmessage):
        return X10Received(rawmessage[2], rawmessage[3])

    @property
    def hex(self):
        return self._messageToHex(self.rawX10,
                                  self.flag)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)



