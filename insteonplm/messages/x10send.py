"""INSTEON Message X10 Send."""
from insteonplm.constants import (MESSAGE_X10_MESSAGE_SEND_0X63,
                                  MESSAGE_X10_MESSAGE_SEND_SIZE,
                                  MESSAGE_X10_MESSAGE_SEND_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)
from insteonplm.messages.message import Message


class X10Send(Message):
    """Insteon Get Next All Link Record Message.

    Message type 0x6A
    """

    _code = MESSAGE_X10_MESSAGE_SEND_0X63
    _sendSize = MESSAGE_X10_MESSAGE_SEND_SIZE
    _receivedSize = MESSAGE_X10_MESSAGE_SEND_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'

    def __init__(self, rawX10, flag, acknak=None):
        """Initialize the X10Send Class."""
        self._rawX10 = rawX10
        self._flag = flag
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return X10Send(rawmessage[2], rawmessage[3], rawmessage[4:5])

    @property
    def rawX10(self):
        """Return the raw x10 bytes."""
        return self._rawX10

    @property
    def flag(self):
        """Return the X10 flag."""
        return self._flag

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
        return [{'rawX10': self._rawX10},
                {'flag': self._flag},
                {'acknak': self._acknak}]
