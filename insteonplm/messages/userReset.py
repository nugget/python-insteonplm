from .messageBase import MessageBase
from .messageConstants import *

class UserReset(MessageBase):
    """Insteon User Reset Message Received 0x55"""
    def __init__(self, rawmessage):
        self.code = 0x55
        self.sendSize = 2
        self.returnSize = 2
        self.name = 'INSTEON User Reset Message Received'