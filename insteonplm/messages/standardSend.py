"""INSTEON Message type 0x62 Standard Send."""

from insteonplm.constants import (MESSAGE_ACK,
                                  MESSAGE_FLAG_EXTENDED_0X10,
                                  MESSAGE_NAK,
                                  MESSAGE_SEND_STANDARD_MESSAGE_0X62,
                                  MESSAGE_SEND_STANDARD_MESSAGE_RECEIVED_SIZE,
                                  MESSAGE_SEND_STANDARD_MESSAGE_SIZE)
from insteonplm.address import Address
from insteonplm.messages.message import Message
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.messageFlags import MessageFlags


class StandardSend(Message):
    """Insteon Standard Length Message Send 0x62."""

    _code = MESSAGE_SEND_STANDARD_MESSAGE_0X62
    _sendSize = MESSAGE_SEND_STANDARD_MESSAGE_SIZE
    _receivedSize = MESSAGE_SEND_STANDARD_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Standard Message Send'

    def __init__(self, address, commandtuple, cmd2=None,
                 flags=0x00, acknak=None):
        """Init the StandardSend message class."""
        if commandtuple.get('cmd1', None) is not None:
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError

        if cmd2 is not None:
            cmd2out = cmd2

        if cmd2out is None:
            raise ValueError

        self._address = Address(address)
        self._messageFlags = MessageFlags(flags)
        self._messageFlags.extended = 0
        self._cmd1 = cmd1
        self._cmd2 = cmd2out

        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create a message from a raw byte stream."""
        if (rawmessage[5] &
                MESSAGE_FLAG_EXTENDED_0X10) == MESSAGE_FLAG_EXTENDED_0X10:
            if len(rawmessage) >= ExtendedSend.receivedSize:
                msg = ExtendedSend.from_raw_message(rawmessage)
            else:
                msg = None
        else:
            msg = StandardSend(rawmessage[2:5],
                               {'cmd1': rawmessage[6],
                                'cmd2': rawmessage[7]},
                               flags=rawmessage[5],
                               acknak=rawmessage[8:9])
        return msg

    # pylint: disable=protected-access
    @classmethod
    def template(cls, address=None, commandtuple=None,
                 cmd2=-1, flags=None, acknak=None):
        """Create a message template for use in callbacks."""
        msgraw = bytearray([0x02, cls._code])
        msgraw.extend(bytes(cls._receivedSize))
        msg = StandardSend.from_raw_message(msgraw)

        if commandtuple:
            cmd1 = commandtuple.get('cmd1')
            cmd2out = commandtuple.get('cmd2')
        else:
            cmd1 = None
            cmd2out = None

        if cmd2 is not -1:
            cmd2out = cmd2

        msg._address = Address(address)
        msg._messageFlags = MessageFlags(flags)
        msg._cmd1 = cmd1
        msg._cmd2 = cmd2out
        msg._acknak = acknak
        return msg

    @property
    def address(self):
        """Return the address of the device."""
        return self._address

    @property
    def cmd1(self):
        """Return cmd1 property of the message."""
        return self._cmd1

    @property
    def cmd2(self):
        """Return cmd2 property of the message."""
        return self._cmd2

    @property
    def flags(self):
        """Return the message flags."""
        return self._messageFlags

    @property
    def acknak(self):
        """Return the ACK/NAK message flag."""
        return self._acknak

    @acknak.setter
    def acknak(self, val):
        """Set the ACK/NAK byte."""
        if val in [None, 0x06, 0x15]:
            self._acknak = val
        else:
            raise ValueError

    @property
    def isack(self):
        """Test if the message is a message ACK."""
        return self._acknak is not None and self._acknak == MESSAGE_ACK

    @property
    def isnak(self):
        """Test if the message is a message NAK."""
        return self._acknak is not None and self._acknak == MESSAGE_NAK

    def _message_properties(self):
        return [{'address': self._address},
                {'flags': self._messageFlags},
                {'cmd1': self._cmd1},
                {'cmd2': self._cmd2},
                {'acknak': self._acknak}]
