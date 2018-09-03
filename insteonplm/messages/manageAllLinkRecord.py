"""INSTEON Message Manage All-Link Record."""
from insteonplm.messages.message import Message
from insteonplm.constants import (
    MESSAGE_MANAGE_ALL_LINK_RECORD_0X6F,
    MESSAGE_MANAGE_ALL_LINK_RECORD_SIZE,
    MESSAGE_MANAGE_ALL_LINK_RECORD_RECEIVED_SIZE,
    MESSAGE_ACK,
    MESSAGE_NAK)
from insteonplm.address import Address


# pylint: disable=too-many-instance-attributes
class ManageAllLinkRecord(Message):
    """Insteon Get First All Link Record Message.

    Message type 0x69
    """

    _code = MESSAGE_MANAGE_ALL_LINK_RECORD_0X6F
    _sendSize = MESSAGE_MANAGE_ALL_LINK_RECORD_SIZE
    _receivedSize = MESSAGE_MANAGE_ALL_LINK_RECORD_RECEIVED_SIZE
    _description = 'Insteon Manage All Link Record Message'

    def __init__(self, control_code, flags, group, address,
                 linkdata1, linkdata2, linkdata3, acknak=None):
        """Init the ManageAllLinkRecord Class."""
        self._controlCode = control_code
        self._controlFlags = flags
        self._group = group
        self._address = Address(address)
        self._linkdata1 = linkdata1
        self._linkdata2 = linkdata2
        self._linkdata3 = linkdata3
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return ManageAllLinkRecord(rawmessage[2:3],
                                   rawmessage[3:4],
                                   rawmessage[4:7],
                                   rawmessage[7:8],
                                   rawmessage[8:9],
                                   rawmessage[9:10],
                                   rawmessage[10:11])

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
    def acknak(self):
        """Return the ACK/NAK byte."""
        return self._acknak

    @property
    def isack(self):
        """Test if this is an ACK message."""
        return self._acknak is not None and self._acknak == MESSAGE_ACK

    @property
    def isnak(self):
        """Test if this is a NAK message."""
        return self._acknak is not None and self._acknak == MESSAGE_NAK

    def _message_properties(self):
        return [{'controlCode': self._controlCode},
                {'controlFlags': self._controlFlags},
                {'group': self._group},
                {'address': self._address},
                {'linkdata1': self._linkdata1},
                {'linkdata2': self._linkdata2},
                {'linkdata3': self._linkdata3},
                {'acknak': self._acknak}]
