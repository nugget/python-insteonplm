from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class SendAllLinkCommand(MessageBase):
    """Insteon Send All Link Command Message 0x6A"""

    def __init__(self,group, allLinkCommand, broadcastCommand, acknak=None):
        super().__jnit__(MESSAGE_SEND_ALL_LINK_COMMAND_0X61, 
                         MESSAGE_SEND_ALL_LINK_COMMAND_SIZE,
                         MESSAGE_SEND_ALL_LINK_COMMAND_RECEIVED_SIZE,
                         'Insteon Get Next All Link Record Message')

        self._group = group
        self._allLinkCommmand = allLinkCommand
        self._broadcastCommand = broadcastCommand

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return SendAllLinkCommand(rawmessage[2], rawmessage[3], rawmessage[4], rawmessage[5:6])

    @property
    def group(self):
        return self._group 

    @property
    def allLinkCommmand(self):
        return self._allLinkCommmand

    @property
    def broadcastCommand(self):
        return self._broadcastCommand

    @property
    def isack(self):
        if (self._acknak is not None and self._acknak == MESSAGE_ACK):
            return True
        else:
            return False

    @property
    def isnak(self):
        if (self._acknak is not None and self._acknak == MESSAGE_NAK):
            return True
        else:
            return False

    def to_hex(self):
        return self._messageToHex(self._group,
                                  self._allLinkCommmand,
                                  self._broadcastCommand,
                                  self._acknak)






