"""INSTEON Message Send All-Link Command."""
from insteonplm.constants import (MESSAGE_SEND_ALL_LINK_COMMAND_0X61,
                                  MESSAGE_SEND_ALL_LINK_COMMAND_SIZE,
                                  MESSAGE_SEND_ALL_LINK_COMMAND_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)
from insteonplm.messages.message import Message


class SendAllLinkCommand(Message):
    """Insteon Send All Link Command Message.

    Message type 0x6A
    """

    _code = MESSAGE_SEND_ALL_LINK_COMMAND_0X61
    _sendSize = MESSAGE_SEND_ALL_LINK_COMMAND_SIZE
    _receivedSize = MESSAGE_SEND_ALL_LINK_COMMAND_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'

    def __init__(self, group, allLinkCommand, broadcastCommand, acknak=None):
        """Init the SendAllLinkCommand Class."""
        self._group = group
        self._allLinkCommmand = allLinkCommand
        self._broadcastCommand = broadcastCommand

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return SendAllLinkCommand(rawmessage[2],
                                  rawmessage[3],
                                  rawmessage[4],
                                  rawmessage[5:6])

    @property
    def group(self):
        """Return the All-Link group."""
        return self._group

    @property
    def allLinkCommmand(self):
        """Return the All-Link command."""
        return self._allLinkCommmand

    @property
    def broadcastCommand(self):
        """Return the broadcase command."""
        return self._broadcastCommand

    @property
    def isack(self):
        """Test if this is an ACK message."""
        return self._acknak is not None and self._acknak == MESSAGE_ACK

    @property
    def isnak(self):
        """Test if this is a NAK message."""
        return self._acknak is not None and self._acknak == MESSAGE_NAK

    def _message_properties(self):
        return [{'group': self._group},
                {'allLinkCommand': self._allLinkCommmand},
                {'broadcastCommand': self._broadcastCommand},
                {'acknak': self._acknak}]
