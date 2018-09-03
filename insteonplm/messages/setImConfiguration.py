"""INSTEON Set IM Configuration Message."""

from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_SET_IM_CONFIGURATION_0X6B,
                                  MESSAGE_SET_IM_CONFIGURATION_SIZE,
                                  MESSAGE_SET_IM_CONFIGURATION_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)


class SetIMConfiguration(Message):
    """INSTEON Get Insteon Modem Info Message.

    Message type 0x60
    """

    _code = MESSAGE_SET_IM_CONFIGURATION_0X6B
    _sendSize = MESSAGE_SET_IM_CONFIGURATION_SIZE
    _receivedSize = MESSAGE_SET_IM_CONFIGURATION_RECEIVED_SIZE
    _description = 'INSTEON Set IM Configuration Message'

    def __init__(self, flags=None, acknak=None):
        """Init the GetImInfo Class."""
        self._imConfigurationFlags = flags
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return SetIMConfiguration(rawmessage[2],
                                  rawmessage[3])

    @property
    def imConfigurationFlags(self):
        """Return the IM configuration flags."""
        return self._imConfigurationFlags

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
        return [{'imConfigurationFlags': self._imConfigurationFlags},
                {'acknak': self.acknak}]
