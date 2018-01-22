from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class AllLinkCleanupStatusReport(MessageBase):
    """INSTEON All-Link Cleanup Status Report Message 0x58"""

    def __init__(self, status):
        super().__init__(MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58,
                         MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE,
                         MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE,
                         'INSTEON All-Link Cleanup Status Report Message Received')
        self._status = status

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkCleanupStatusReport(rawmessage[2])

    @property
    def status(self):
        return self._status

    @property
    def isack(self):
        return (self.status & MESSAGE_ACK) == MESSAGE_ACK

    @property
    def isnak(self):
        return (self.status & MESSAGE_NAK) == MESSAGE_NAK
    
    def to_hex(self):
        return self._messageToHex(self._status)

