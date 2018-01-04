from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class SendAllLinkCommand(MessageBase):
    """Insteon Send All Link Command Message 0x6A"""

    code = MESSAGE_SEND_ALL_LINK_COMMAND_0X61
    sendSize = MESSAGE_SEND_ALL_LINK_COMMAND_SIZE
    receivedSize = MESSAGE_SEND_ALL_LINK_COMMAND_RECEIVED_SIZE
    description = 'Insteon Get Next All Link Record Message'

    def __init__(self,group, allLinkCommand, broadcastCommand, acknak=None):

        self.group = group
        self.allLinkCommmand = allLinkCommand
        self.broadcastCommand = broadcastCommand

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return SendAllLinkCommand(rawmessage[2], rawmessage[3], rawmessage[4], rawmessage[5:6])

    @property
    def hex(self):
        return self._messageToHex(self.group,
                                  self.allLinkCommmand,
                                  self.broadcastCommand,
                                  self._acknak)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

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






