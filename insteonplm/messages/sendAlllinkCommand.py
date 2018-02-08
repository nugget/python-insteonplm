from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class SendAllLinkCommand(MessageBase):
    """Insteon Send All Link Command Message 0x6A"""

    _code = MESSAGE_SEND_ALL_LINK_COMMAND_0X61
    _sendSize = MESSAGE_SEND_ALL_LINK_COMMAND_SIZE
    _receivedSize = MESSAGE_SEND_ALL_LINK_COMMAND_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'


    def __init__(self,group, allLinkCommand, broadcastCommand, acknak=None):
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

    def _message_properties(self):
        return [{'group': self._group},
                {'allLinkCommand': self._allLinkCommmand},
                {'broadcastCommand': self._broadcastCommand},
                {'acknak': self._acknak}]






