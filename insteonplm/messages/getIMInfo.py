"""INSTEON Message Get IM Info."""

from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_GET_IM_INFO_0X60,
                                  MESSAGE_GET_IM_INFO_SIZE,
                                  MESSAGE_GET_IM_INFO_RECEIVED_SIZE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)
from insteonplm.address import Address


class GetImInfo(Message):
    """INSTEON Get Insteon Modem Info Message.

    Message type 0x60
    """

    _code = MESSAGE_GET_IM_INFO_0X60
    _sendSize = MESSAGE_GET_IM_INFO_SIZE
    _receivedSize = MESSAGE_GET_IM_INFO_RECEIVED_SIZE
    _description = 'INSTEON Get Insteon Modem Info Message Received'

    def __init__(self, address=None, cat=None, subcat=None, firmware=None,
                 acknak=None):
        """Init the GetImInfo Class."""
        self._address = Address(address)
        self._category = cat
        self._subcategory = subcat
        self._firmware = firmware
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        return GetImInfo(rawmessage[2:5],
                         rawmessage[5],
                         rawmessage[6],
                         rawmessage[7],
                         rawmessage[8])

    @property
    def address(self):
        """Return the device address."""
        return self._address

    @property
    def category(self):
        """Return the IM device category."""
        return self._category

    @property
    def subcategory(self):
        """Return the IM device subcategory."""
        return self._subcategory

    @property
    def firmware(self):
        """Return the IM device firmware version."""
        return self._firmware

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
        return [{'address': self._address},
                {'category': self._category},
                {'subcategory': self._subcategory},
                {'firmware': self._firmware},
                {'acknak': self._acknak}]
