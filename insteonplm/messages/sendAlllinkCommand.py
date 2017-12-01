from .messageBase import MessageBase
from .messageConstants import *

class SendAllLinkCommand(MessageBase):
    """Insteon Send All Link Command Message 0x6A"""

    def __init__(self,group, allLinkCommand, broadcastCommand, acknak=None):
        self.code = MESSAGE_SEND_ALL_LINK_COMMAND
        self.sendSize = MESSAGE_GET_NEXT_ALL_LINK_RECORD_SIZE
        self.returnSize = MESSAGE_GET_NEXT_ALL_LINK_RECORD_RECEIVED_SIZE
        self.name = 'Insteon Get Next All Link Record Message'

        self.group = group
        self.allLinkCommmand = allLinkCommand
        self.broadcastCommand = broadcastCommand

        self._acknak = self._setacknak(acknak)

    @property
    def hex(self):
        return self._messageToHex(self.group,
                                  self.allLinkCommand,
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






