"""INSTEON Extended Receive Message Type 0x51."""

from insteonplm.constants import (MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51,
                                  MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE)
from insteonplm.address import Address
from insteonplm.messages.message import Message
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.userdata import Userdata


class ExtendedReceive(Message):
    """Insteon Extended Length Message Received.

    Message type 0x51
    """

    _code = MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51
    _sendSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    _receivedSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Extended Message Received'

    def __init__(self, address, target, commandtuple, userdata, cmd2=None,
                 flags=0x10):
        """Init the ExtendedRecieve message class."""
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
        self._target = Address(target)
        self._messageFlags = MessageFlags(flags)
        # self._messageFlags.extended = 1
        self._cmd1 = cmd1
        self._cmd2 = cmd2out
        self._userdata = Userdata(userdata)

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from raw byte stream."""
        userdata = Userdata.from_raw_message(rawmessage[11:25])
        return ExtendedReceive(rawmessage[2:5],
                               rawmessage[5:8],
                               {'cmd1': rawmessage[9],
                                'cmd2': rawmessage[10]},
                               userdata,
                               flags=rawmessage[8])

    # pylint: disable=protected-access
    @classmethod
    def template(cls, address=None, target=None, commandtuple=None,
                 userdata=None, cmd2=-1, flags=None):
        """Create message template for callbacks."""
        msgraw = bytearray([0x02, cls._code])
        msgraw.extend(bytes(cls._receivedSize))
        msg = ExtendedReceive.from_raw_message(msgraw)

        if commandtuple:
            cmd1 = commandtuple.get('cmd1')
            cmd2out = commandtuple.get('cmd2')
        else:
            cmd1 = None
            cmd2out = None

        if cmd2 is not -1:
            cmd2out = cmd2

        msg._address = Address(address)
        msg._target = Address(target)
        msg._messageFlags = MessageFlags(flags)
        msg._cmd1 = cmd1
        msg._cmd2 = cmd2out
        msg._userdata = Userdata.create_pattern(userdata)
        return msg

    @property
    def address(self):
        """Return address of sending device."""
        return self._address

    @property
    def target(self):
        """Return address of target device."""
        return self._target

    @property
    def cmd1(self):
        """Return cmd1 property of message."""
        return self._cmd1

    @property
    def cmd2(self):
        """Return cmd2 property of message."""
        return self._cmd2

    @property
    def userdata(self):
        """Return user data of extended message."""
        return self._userdata

    @property
    def flags(self):
        """Return message flags."""
        return self._messageFlags

    @property
    def targetLow(self):
        """Return the low byte of the target address field.

        Used in All-Link Cleanup messages.
        """
        low_byte = None
        if self.target is not None and self._messageFlags.isBroadcast:
            low_byte = self.target.bytes[0]
        return low_byte

    @property
    def targetMed(self):
        """Return the middle byte of the target address field.

        Used in All-Link Cleanup messages.
        """
        med_byte = None
        if self.target is not None and self._messageFlags.isBroadcast:
            med_byte = self.target.bytes[1]
        return med_byte

    @property
    def targetHi(self):
        """Return the high byte of the target address field.

        Used in All-Link Cleanup messages.
        """
        hi_byte = None
        if self.target is not None and self._messageFlags.isBroadcast:
            hi_byte = self.target.bytes[2]
        return hi_byte

    def _message_properties(self):
        return [{'address': self._address},
                {'target': self._target},
                {'flags': self._messageFlags},
                {'cmd1': self._cmd1},
                {'cmd2': self._cmd2},
                {'userdata': self._userdata}]
