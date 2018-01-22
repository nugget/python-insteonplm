from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class AllLinkRecordResponse(MessageBase):
    """INSTEON ALL-Link Record Response 0x57"""

    def __init__(self, flags, group, address, linkdata1, linkdata2, linkdata3):
        super().__init__(MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57,
                         MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE,
                         MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE,
                         'INSTEON ALL-Link Record Response')

        # ALL-Link Record Response
        self._controlFlags = flags
        self._group = group
        self._address = Address(address)
        self._linkdata1 = linkdata1
        self._linkdata2 = linkdata2
        self._linkdata3 = linkdata3

    @classmethod
    def from_raw_message(cls, rawmessage):
        return AllLinkRecordResponse(rawmessage[2],
                                     rawmessage[3],
                                     rawmessage[4:7],
                                     rawmessage[7],
                                     rawmessage[8],
                                     rawmessage[9])

    @property
    def group(self):
        self._group

    @property
    def address(self):
        self._address

    @property
    def linkdata1(self):
        self._linkdata1

    @property
    def linkdata2(self):
        self._linkdata2

    @property
    def linkdata3(self):
        self._linkdata3

    @property
    def isRecordinuse(self):
        return (self._controlFlags & self.CONTROL_FLAG_RECORD_IN_USE) == self.CONTROL_FLAG_RECORD_IN_USE

    @property
    def isController(self):
        return (self._controlFlags & self.CONTROL_FLAG_CONTROLLER) == self.CONTROL_FLAG_CONTROLER

    @property
    def isSlave(self):
        return not self.iscontroller

    def to_hex(self):
        return self._messageToHex(self._controlFlags,
                                  self._group,
                                  self._address,
                                  self._linkdata1,
                                  self._linkdata2,
                                  self._linkdata3)
