"""INSTEON Message All-Link Record Response."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57,
                                  MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE)
from insteonplm.address import Address

CONTROL_FLAG_RECORD_IN_USE = 0x80
CONTROL_FLAG_CONTROLLER = 0x40


class AllLinkRecordResponse(Message):
    """INSTEON ALL-Link Record Response.

    Message type 0x57
    """

    _code = MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57
    _sendSize = MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE
    _receivedSize = MESSAGE_ALL_LINK_RECORD_RESPONSE_SIZE
    _description = 'INSTEON ALL-Link Record Response'

    def __init__(self, flags, group, address, linkdata1, linkdata2, linkdata3):
        """Init the AllLinkRecordResponse Class."""
        self._controlFlags = flags
        self._group = group
        self._address = Address(address)
        self._linkdata1 = linkdata1
        self._linkdata2 = linkdata2
        self._linkdata3 = linkdata3

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return AllLinkRecordResponse(rawmessage[2],
                                     rawmessage[3],
                                     rawmessage[4:7],
                                     rawmessage[7],
                                     rawmessage[8],
                                     rawmessage[9])

    @property
    def controlFlags(self):
        """Return the link record control flags."""
        return self._controlFlags

    @property
    def group(self):
        """Return the link record group."""
        return self._group

    @property
    def address(self):
        """Return the device address."""
        return self._address

    @property
    def linkdata1(self):
        """Return the first link data field."""
        return self._linkdata1

    @property
    def linkdata2(self):
        """Return the second link data field."""
        return self._linkdata2

    @property
    def linkdata3(self):
        """Return the third link data field."""
        return self._linkdata3

    @property
    def isRecordinuse(self):
        """Test if the link record is in use."""
        return ((self._controlFlags & CONTROL_FLAG_RECORD_IN_USE) ==
                CONTROL_FLAG_RECORD_IN_USE)

    @property
    def isController(self):
        """Test if the link group is a controller."""
        return ((self._controlFlags & CONTROL_FLAG_CONTROLLER) ==
                CONTROL_FLAG_CONTROLLER)

    @property
    def isSlave(self):
        """Test if the link group is a slave or responder."""
        return not self.isController

    def _message_properties(self):
        return [{'controlFlags': self._controlFlags},
                {'group': self._group},
                {'address': self._address},
                {'linkdata1': self._linkdata1},
                {'linkdata2': self._linkdata2},
                {'linkdata3': self._linkdata3}]
