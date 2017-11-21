from .messageBase import MessageBase
from .messageConstants import *

class AllLinkCleanupStatusReport(MessageBase):
    """INSTEON All-Link Cleanup Status Report Message 0x58"""

    def __init__(self, status):
        self.code = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT
        self.sendSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
        self.returnSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
        self.name = 'INSTEON All-Link Cleanup Status Report Message Received'

        self.status = status

    @property
    def message(self):
        msg = bytearray([0x02,
                         self.code,
                         self.status])
        return msg

    @property
    def isack(self):
        return (self.status & MESSAGE_ACK) == MESSAGE_ACK

    @property
    def isnak(self):
        return (self.status & MESSAGE_NAK) == MESSAGE_NAK
