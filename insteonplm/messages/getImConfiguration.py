"""INSTEON Message Get IM Configuration."""
from insteonplm.constants import (MESSAGE_GET_IM_CONFIGURATION_0X73,
                                  MESSAGE_GET_IM_CONFIGURATION_SIZE,
                                  MESSAGE_GET_IM_CONFIGURATION_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)
from insteonplm.messages.message import Message


class GetImConfiguration(Message):
    """Insteon Get IM Configuration Message.

    Message type 0x62
    """

    _code = MESSAGE_GET_IM_CONFIGURATION_0X73
    _sendSize = MESSAGE_GET_IM_CONFIGURATION_SIZE
    _receivedSize = MESSAGE_GET_IM_CONFIGURATION_RECEIVED_SIZE
    _description = 'Insteon Get IM Configuration Message'

    def __init__(self, flags=None, acknak=None):
        """Init the GetImConfiguration Class."""
        self._imConfigurationFlags = flags
        self._spare1 = None
        self._spare2 = None
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmesssage):
        """Create message from a raw byte stream."""
        return GetImConfiguration(rawmesssage[2],
                                  rawmesssage[5])

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
        if self._imConfigurationFlags is not None:
            self._spare1 = 0x00
            self._spare2 = 0x00
        else:
            self._spare1 = None
            self._spare2 = None
        return [{'imConfigurationFlags': self._imConfigurationFlags},
                {'spare1': self._spare1},
                {'spare2': self._spare2},
                {'acknak': self.acknak}]
