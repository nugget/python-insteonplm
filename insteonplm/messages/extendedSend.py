"""INSTEON Extended Send Message Type 0x62."""

from insteonplm.constants import (MESSAGE_ACK,
                                  MESSAGE_NAK,
                                  MESSAGE_SEND_EXTENDED_MESSAGE_0X62,
                                  MESSAGE_SEND_EXTENDED_MESSAGE_RECEIVED_SIZE,
                                  MESSAGE_SEND_EXTENDED_MESSAGE_SIZE)
from insteonplm.address import Address
from insteonplm.messages.message import Message
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.userdata import Userdata


class ExtendedSend(Message):
    """Send an INSTEON Extended message.

    address: A device hex address in any form.
    cmd1: Requred command in the cmd1 field
    cmd2: Requred command in the cmd2 field
    **kwarg: otional userdata dictionary with the following keys:
        'd1' - User data byte 0 as byte or int
        'd2' - user data byte 1 as byte or int
        ...
        'd14' - user data byte 14 as byte or int
        'd1' to 'd14' are assumed to equal 0x00 unless explicitly set
    """

    _code = MESSAGE_SEND_EXTENDED_MESSAGE_0X62
    _sendSize = MESSAGE_SEND_EXTENDED_MESSAGE_SIZE
    _receivedSize = MESSAGE_SEND_EXTENDED_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Standard Message Send'

    def __init__(self, address, commandtuple, userdata, cmd2=None,
                 flags=0x10, acknak=None):
        """Initialize the ExtendedSend message class."""
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
        self._messageFlags.extended = 1
        self._cmd1 = cmd1
        self._cmd2 = cmd2out
        self._userdata = Userdata(userdata)
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create a message from a raw byte stream."""
        userdata_dict = Userdata(rawmessage[8:22])
        return ExtendedSend(rawmessage[2:5],
                            {'cmd1': rawmessage[6],
                             'cmd2': rawmessage[7]},
                            userdata_dict,
                            flags=rawmessage[5],
                            acknak=rawmessage[22:23])

    # pylint: disable=protected-access
    @classmethod
    def template(cls, address=None, commandtuple={}, userdata=None,
                 cmd2=-1, flags=None, acknak=None):
        """Create a message template used for callbacks."""
        msgraw = bytearray([0x02, cls._code])
        msgraw.extend(bytes(cls._receivedSize))
        msg = ExtendedSend.from_raw_message(msgraw)

        cmd1 = commandtuple.get('cmd1', None)
        cmd2out = commandtuple.get('cmd2', None)

        if cmd2 is not -1:
            cmd2out = cmd2

        msg._address = Address(address)
        msg._messageFlags = MessageFlags(flags)
        msg._messageFlags.extended = 1
        msg._cmd1 = cmd1
        msg._cmd2 = cmd2out
        msg._userdata = Userdata.template(userdata)
        msg._acknak = acknak
        return msg

    @property
    def address(self):
        """Return the address of the device."""
        return self._address

    @property
    def cmd1(self):
        """Return the cmd1 property of the message."""
        return self._cmd1

    @property
    def cmd2(self):
        """Return the cmd2 property of the message."""
        return self._cmd2

    @property
    def userdata(self):
        """Return the extended message user data."""
        return self._userdata

    @property
    def flags(self):
        """Return the message flags."""
        return self._messageFlags

    @property
    def acknak(self):
        """Return the ACK/NAK byte."""
        return self._acknak

    @property
    def isack(self):
        """Test if message is an ACK."""
        return self._acknak is not None and self._acknak == MESSAGE_ACK

    @property
    def isnak(self):
        """Test if message is a NAK."""
        return self._acknak is not None and self._acknak == MESSAGE_NAK

    def _message_properties(self):
        return [{'address': self._address},
                {'flags': self._messageFlags},
                {'cmd1': self._cmd1},
                {'cmd2': self._cmd2},
                {'userdata': self._userdata},
                {'acknak': self._acknak}]
