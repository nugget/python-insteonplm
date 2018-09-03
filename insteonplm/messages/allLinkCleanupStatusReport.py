"""INSTEON Message All-Link Cleanup Status Report."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58,
                                  MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)


class AllLinkCleanupStatusReport(Message):
    """INSTEON All-Link Cleanup Status Report Message.

    Message type 0x58
    """

    _code = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58
    _sendSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
    _receivedSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
    _description = 'INSTEON All-Link Cleanup Status Report Message Received'

    def __init__(self, acknak):
        """Init the AllLinkCleanupStatusReport Class."""
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return AllLinkCleanupStatusReport(rawmessage[2])

    @property
    def acknak(self):
        """Return ACK/NAK byte."""
        return self._acknak

    @property
    def isack(self):
        """Test if this is an ACK message."""
        return self._acknak & MESSAGE_ACK == MESSAGE_ACK

    @property
    def isnak(self):
        """Test if this is a NAK message."""
        return self._acknak & MESSAGE_NAK == MESSAGE_NAK

    def _message_properties(self):
        return [{'acknak': self._acknak}]
