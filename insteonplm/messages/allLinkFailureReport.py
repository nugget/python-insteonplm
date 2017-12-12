from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address
import binascii

class AllLinkCleanupFailureReport(MessageBase):
    """INSTEON All-Link Failure Report Message 0x56"""

    code = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT
    sendSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    receivedSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    description = 'INSTEON All-Link Failure Report Message'

    def __init__(self, group, address):

        self.group = group
        if isinstance(address, Address):
            self.address = address
        else:
            self.address = Address(address)

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkCleanupFailureReport(rawmessage[3], rawmessage[4:7])

    @property
    def hex(self):
        return self._messageToHex(0x01,
                                  self.group,
                                  self.address)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)