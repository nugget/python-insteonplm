"""INSTEON Message Get Next All-Link Record."""
from insteonplm.messages.message import Message
from insteonplm.constants import (
    MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A,
    MESSAGE_GET_NEXT_ALL_LINK_RECORD_SIZE,
    MESSAGE_GET_NEXT_ALL_LINK_RECORD_RECEIVED_SIZE,
    MESSAGE_ACK,
    MESSAGE_NAK)


class GetNextAllLinkRecord(Message):
    """Insteon Get Next All Link Record Message.

    Message type 0x6A
    """

    _code = MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A
    _sendSize = MESSAGE_GET_NEXT_ALL_LINK_RECORD_SIZE
    _receivedSize = MESSAGE_GET_NEXT_ALL_LINK_RECORD_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'

    def __init__(self, acknak=None):
        """Init the GetNextAllLinkRecord Class."""
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return GetNextAllLinkRecord(rawmessage[2:3])

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
        return [{'acknak': self._acknak}]
