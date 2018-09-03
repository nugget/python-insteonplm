"""INSTEON Message Reset IM."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_RESET_IM_0X67,
                                  MESSAGE_RESET_IM_SIZE,
                                  MESSAGE_RESET_IM_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)


class ResetIM(Message):
    """Insteon Reset IM Message.

    Message type 0x67
    """

    _code = MESSAGE_RESET_IM_0X67
    _sendSize = MESSAGE_RESET_IM_SIZE
    _receivedSize = MESSAGE_RESET_IM_RECEIVED_SIZE
    _description = 'Insteon Reset IM Message'

    def __init__(self, acknak=None):
        """Init the ResetIM Class."""
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return ResetIM(rawmessage[2:3])

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
