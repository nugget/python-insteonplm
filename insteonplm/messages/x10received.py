from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class X10Received(MessageBase):
    """Insteon Get Next All Link Record Message 0x6A"""
    
    _code = MESSAGE_X10_MESSAGE_RECEIVED_0X52
    _sendSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    _receivedSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'


    def __init__(self, rawX10, flag):
        self._rawX10 = rawX10
        self._flag = flag

    @classmethod
    def from_raw_message(cls, rawmessage):
        return X10Received(rawmessage[2], rawmessage[3])

    @property
    def rawX10(self):
        return self._rawX10
    
    @property
    def flag(self):
        return self._flag

    def _message_properties(self):
        return [{'rawX10': self._rawX10},
                {'flag': self._flag}]



