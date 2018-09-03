"""INSTEON Message Get First All-Link Record."""
from insteonplm.messages.message import Message
from insteonplm.constants import (
    MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69,
    MESSAGE_GET_FIRST_ALL_LINK_RECORD_SIZE,
    MESSAGE_GET_FIRST_ALL_LINK_RECORD_RECEIVED_SIZE,
    MESSAGE_ACK,
    MESSAGE_NAK)


class GetFirstAllLinkRecord(Message):
    """Insteon Get First All Link Record Message.

    Message type 0x69
    """

    _code = MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69
    _sendSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_SIZE
    _receivedSize = MESSAGE_GET_FIRST_ALL_LINK_RECORD_RECEIVED_SIZE
    _description = 'Insteon Get First All Link Record Message'

    def __init__(self, acknak=None):
        """Init the GetFirstAllLinkRecord Class."""
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return GetFirstAllLinkRecord(rawmessage[2:3])

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
