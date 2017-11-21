from .messageBase import MessageBase
from .messageConstants import *

class GetImConfiguration(MessageBase):
    """Insteon Get IM Configuration Message Send and Receive 0x62"""
    def __init__(self, flags, acknak = None):
        self.code = MESSAGE_GET_IM_CONFIGURATION
        self.sendSize = MESSAGE_GET_IM_CONFIGURATION_SIZE
        self.returnSize = MESSAGE_GET_IM_CONFIGURATION_RECEIVED_SIZE
        self.name = 'Insteon Get IM Configuration Message Send and Receive'
        
        self.__messageFlags = flags
        self.spare1 = None
        self.spare2 = None
        self.acknak = acknak
