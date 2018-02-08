from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

class AllLinkRecordResponse(MessageBase):
    """INSTEON ALL-Link Record Response 0x57"""

    _code = MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57
    _sendSize = MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE
    _receivedSize = MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE
    _description = 'INSTEON ALL-Link Record Response'


    def __init__(self, flags, group, address, linkdata1, linkdata2, linkdata3):
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
    def controlFlags(self):
        return self._controlFlags

    @property
    def group(self):
        return self._group

    @property
    def address(self):
        return self._address

    @property
    def linkdata1(self):
        return self._linkdata1

    @property
    def linkdata2(self):
        return self._linkdata2

    @property
    def linkdata3(self):
        return self._linkdata3

    @property
    def isRecordinuse(self):
        return (self._controlFlags & self.CONTROL_FLAG_RECORD_IN_USE) == self.CONTROL_FLAG_RECORD_IN_USE

    @property
    def isController(self):
        return (self._controlFlags & self.CONTROL_FLAG_CONTROLLER) == self.CONTROL_FLAG_CONTROLER

    @property
    def isSlave(self):
        return not self.iscontroller

    def _message_properties(self):
        return [{'controlFlags': self._controlFlags},
                {'group': self._group},
                {'address': self._address},
                {'linkdata1': self._linkdata1},
                {'linkdata2': self._linkdata2},
                {'linkdata3': self._linkdata3}]
