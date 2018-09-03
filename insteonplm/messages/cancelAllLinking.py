"""INSTEON Message Cancel All-Linking."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_CANCEL_ALL_LINKING_0X65,
                                  MESSAGE_CANCEL_ALL_LINKING_SIZE,
                                  MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)


class CancelAllLinking(Message):
    """INSTEON Cancel All-Linking.

    Message type 0x65
    """

    _code = MESSAGE_CANCEL_ALL_LINKING_0X65
    _sendSize = MESSAGE_CANCEL_ALL_LINKING_SIZE
    _receivedSize = MESSAGE_CANCEL_ALL_LINKING_RECEIVED_SIZE
    _description = 'INSTEON Cancel All-Linking'

    def __init__(self, acknak=None):
        """Init the CancelAllLinking Class."""
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return CancelAllLinking(rawmessage[2:3])

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
