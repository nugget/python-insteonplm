from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

class AllLinkFailureReport(MessageBase):
    """INSTEON All-Link Failure Report Message 0x56"""

    def __init__(self, group, address):
        self.code = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT
        self.sendSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
        self.returnSize = MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_SIZE
        self.name = 'INSTEON All-Link Failure Report Message'

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