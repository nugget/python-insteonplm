"""INSTEON Message All-Link Complete."""

from insteonplm.address import Address
from insteonplm.constants import (MESSAGE_ALL_LINKING_COMPLETED_0X53,
                                  MESSAGE_ALL_LINKING_COMPLETED_SIZE)
from insteonplm.messages.message import Message


class AllLinkComplete(Message):
    """INSTEON ALL-Linking Completed Message.

    Message type 0x53
    """

    _code = MESSAGE_ALL_LINKING_COMPLETED_0X53
    _sendSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
    _receivedSize = MESSAGE_ALL_LINKING_COMPLETED_SIZE
    _description = 'INSTEON ALL-Linking Completed Message Received'

    def __init__(self, linkcode, group, address, cat, subcat, firmware):
        """Init the AllLinkComplete Class."""
        self._linkcode = linkcode
        self._group = group
        self._address = Address(address)
        self._category = cat
        self._subcategory = subcat
        self._firmware = firmware

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create a message from a raw byte stream."""
        return AllLinkComplete(rawmessage[2],
                               rawmessage[3],
                               rawmessage[4:7],
                               rawmessage[7],
                               rawmessage[8],
                               rawmessage[9])

    @property
    def linkcode(self):
        """Return link record link code."""
        return self._linkcode

    @property
    def group(self):
        """Return link record group."""
        return self._group

    @property
    def address(self):
        """Return the device address."""
        return self._address

    @property
    def category(self):
        """Return the device category."""
        return self._category

    @property
    def subcategory(self):
        """Return the device subcategory."""
        return self._subcategory

    @property
    def firmware(self):
        """Return the device firmware version."""
        return self._firmware

    @property
    def isresponder(self):
        """Return if the link record is a responder."""
        return bool(self.linkcode == 0)

    @property
    def iscontroller(self):
        """Return if the link record is a controller."""
        return bool(self.linkcode == 1)

    @property
    def isdeleted(self):
        """Return if the link record is deleted."""
        return bool(self.linkcode == 0xFF)

    def _message_properties(self):
        return [{'linkcode': self._linkcode},
                {'group': self._group},
                {'address': self._address},
                {'category': self._category},
                {'subcategory': self._subcategory},
                {'firmware': self._firmware}]
