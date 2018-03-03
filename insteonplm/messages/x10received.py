"""INSTEON Message X10 Received."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_X10_MESSAGE_RECEIVED_0X52,
                                  MESSAGE_X10_MESSAGE_RECEIVED_SIZE)


class X10Received(Message):
    """Insteon X10 Received Message.

    Message type 0x52
    """

    _code = MESSAGE_X10_MESSAGE_RECEIVED_0X52
    _sendSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    _receivedSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'

    def __init__(self, rawX10, flag):
        """Initialize X10Received Class."""
        self._rawX10 = rawX10
        self._flag = flag

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create from raw byte stream."""
        return X10Received(rawmessage[2], rawmessage[3])

    @property
    def rawX10(self):
        """Return raw X10 message."""
        return self._rawX10

    @property
    def flag(self):
        """Return X10 flag."""
        return self._flag

    def _message_properties(self):
        return [{'rawX10': self._rawX10},
                {'flag': self._flag}]
