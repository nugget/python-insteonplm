"""INSTEON Message User Reset."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_USER_RESET_DETECTED_0X55,
                                  MESSAGE_USER_RESET_DETECTED_SIZE)


class UserReset(Message):
    """Insteon User Reset Message Received.

    Message type 0x55
    """

    _code = MESSAGE_USER_RESET_DETECTED_0X55
    _sendSize = MESSAGE_USER_RESET_DETECTED_SIZE
    _receivedSize = MESSAGE_USER_RESET_DETECTED_SIZE
    _description = 'INSTEON User Reset Message Received'

    # pylint: disable=unused-argument
    @classmethod
    def from_raw_messsage(cls, rawmessage):
        """Create message from raw byte stream."""
        return UserReset()

    def _message_properties(self):
        return []
