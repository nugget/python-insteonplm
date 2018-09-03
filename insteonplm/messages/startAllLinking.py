"""INSTEON Message Start All-Linking."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_START_ALL_LINKING_0X64,
                                  MESSAGE_START_ALL_LINKING_SIZE,
                                  MESSAGE_START_ALL_LINKING_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)


class StartAllLinking(Message):
    """Insteon Start All Linking Message.

    Message type 0x64
    """

    _code = MESSAGE_START_ALL_LINKING_0X64
    _sendSize = MESSAGE_START_ALL_LINKING_SIZE
    _receivedSize = MESSAGE_START_ALL_LINKING_RECEIVED_SIZE
    _description = 'Insteon Start All Linking Message'

    def __init__(self, linkCode, group, acknak=None):
        """Init the StartAllLinking Class."""
        self._linkCode = linkCode
        self._group = group

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return StartAllLinking(rawmessage[2], rawmessage[3], rawmessage[4:5])

    @property
    def linkCode(self):
        """Return the link code."""
        return self._linkCode

    @property
    def group(self):
        """Return the All-Link group."""
        return self._group

    @property
    def acknak(self):
        """Return the ACK/NAK byte."""
        return self._acknak

    @property
    def isack(self):
        """Test if this is an ACK message."""
        return self._acknak is not None and self._acknak == MESSAGE_ACK

    @property
    def isnak(self):
        """Test if this is a NAK message."""
        return self._acknak is not None and self._acknak == MESSAGE_NAK

    def _message_properties(self):
        return [{'linkCode': self._linkCode},
                {'group': self._group},
                {'acknak': self._acknak}]
