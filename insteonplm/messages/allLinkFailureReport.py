from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class AllLinkCleanupFailureReport(MessageBase):
    """INSTEON All-Link Failure Report Message 0x56"""
    _code = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_0X56
    _sendSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    _receivedSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    _description = 'INSTEON All-Link Failure Report Message'


    def __init__(self, group, address):
        self._group = group
        self._address = Address(address)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkCleanupFailureReport(rawmessage[3], rawmessage[4:7])
    
    @property
    def group(self):
        return self._group
    
    @property
    def address(self):
        return self._address

    def to_hex(self):
        return self._messageToHex(0x01,
                                  self._group,
                                  self._address)