from .messageBase import MessageBase
from insteonplm.constants import *
import binascii

class AllLinkCleanupStatusReport(MessageBase):
    """INSTEON All-Link Cleanup Status Report Message 0x58"""
    _code = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58
    _sendSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
    _receivedSize = MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_SIZE
    _description = 'INSTEON All-Link Cleanup Status Report Message Received'

    def __init__(self, acknak):
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkCleanupStatusReport(rawmessage[2])

    @property
    def acknak(self):
        return self._acknak

    @property
    def isack(self):
        return (self._acknak & MESSAGE_ACK) == MESSAGE_ACK

    @property
    def isnak(self):
        return (self._acknak & MESSAGE_NAK) == MESSAGE_NAK
    
    def _message_properties(self):
        return [{'acknak': self._acknak}]

