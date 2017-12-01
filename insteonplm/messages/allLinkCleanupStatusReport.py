from .messageBase import MessageBase
from .messageConstants import *
import binascii

class AllLinkCleanupStatusReport(MessageBase):
    """INSTEON All-Link Cleanup Status Report Message 0x58"""

    def __init__(self, status):
        self.code = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT
        self.sendSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
        self.returnSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
        self.name = 'INSTEON All-Link Cleanup Status Report Message Received'

        self.status = status

    @property
    def hex(self):
        return self._messageToHex(self.status)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

    @property
    def isack(self):
        return (self.status & MESSAGE_ACK) == MESSAGE_ACK

    @property
    def isnak(self):
        return (self.status & MESSAGE_NAK) == MESSAGE_NAK
