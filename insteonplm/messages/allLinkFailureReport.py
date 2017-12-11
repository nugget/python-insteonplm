from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class AllLinkFailureReport(MessageBase):
    """INSTEON All-Link Failure Report Message 0x56"""

    code = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT
    sendSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    receivedSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
    description = 'INSTEON All-Link Failure Report Message'

    def __init__(self, group, address):

        self.group = group
        self.address = Address(address)

    @property
    def hex(self):
        return self._messageToHex(0x01,
                                  self.group,
                                  self.address)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)