"""INSTEON Message All-LinkCleanup Failup Report."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_0X56,
                                  MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE)
from insteonplm.address import Address


class AllLinkCleanupFailureReport(Message):
    """INSTEON All-Link Failure Report Message.

    Message type 0x56
    """

    _code = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_0X56
    _sendSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    _receivedSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    _description = 'INSTEON All-Link Failure Report Message'

    def __init__(self, group, address):
        """Init the AllLinkCleanupFailureReport Class."""
        self._group = group
        self._address = Address(address)
        self._failedFlag = 0x01

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from a raw byte stream."""
        return AllLinkCleanupFailureReport(rawmessage[3], rawmessage[4:7])

    @property
    def group(self):
        """Return the All-Link Group."""
        return self._group

    @property
    def address(self):
        """Return the device address."""
        return self._address

    def _message_properties(self):
        return [{'failedFlag': self._failedFlag},
                {'group': self._group},
                {'address': self._address}]
