"""INSTEON Standard Receive Message Type 0x50."""

from insteonplm.constants import (MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50,
                                  MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE)
from insteonplm.address import Address
from insteonplm.messages.message import Message
from insteonplm.messages.messageFlags import MessageFlags


class StandardReceive(Message):
    """Insteon Standard Length Message Received.

    Message type 0x50
    """

    _code = MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50
    _sendSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
    _receivedSize = MESSAGE_STANDARD_MESSAGE_RECIEVED_SIZE
    _description = 'INSTEON Standard Message Received'

    def __init__(self, address, target, commandtuple, cmd2=None, flags=0x00):
        """Init the StandardReceive message class."""
        if commandtuple.get('cmd1') is not None:
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
        # self._messageFlags.extended = 0
        self._cmd1 = cmd1
        self._cmd2 = cmd2out

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create message from a raw byte stream."""
        return StandardReceive(rawmessage[2:5],
                               rawmessage[5:8],
                               {'cmd1': rawmessage[9],
                                'cmd2': rawmessage[10]},
                               flags=rawmessage[8])

    # pylint: disable=protected-access
    @classmethod
    def template(cls, address=None, target=None, commandtuple=None,
                 cmd2=-1, flags=None):
        """Create a message template used for callbacks."""
        msgraw = bytearray([0x02, cls._code])
        msgraw.extend(bytes(cls._receivedSize))
        msg = StandardReceive.from_raw_message(msgraw)

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
        return msg

    @property
    def address(self):
        """Return the address of the device."""
        return self._address

    @property
    def target(self):
        """Return the address of the target device."""
        return self._target

    @property
    def cmd1(self):
        """Return the cmd1 property of the message."""
        return self._cmd1

    @property
    def cmd2(self):
        """Return the cmd2 property of the message."""
        return self._cmd2

    @property
    def flags(self):
        """Return the message flags."""
        return self._messageFlags

    @property
    def targetLow(self):
        """Return the low byte of the target message property.

        Used in All-Link Cleanup message types.
        """
        low_byte = None
        if self.target.addr is not None and self._messageFlags.isBroadcast:
            low_byte = self.target.bytes[0]
        return low_byte

    @property
    def targetMed(self):
        """Return the middle byte of the target message property.

        Used in All-Link Cleanup message types.
        """
        med_byte = None
        if self.target.addr is not None and self._messageFlags.isBroadcast:
            med_byte = self.target.bytes[1]
        return med_byte

    @property
    def targetHi(self):
        """Return the high byte of the target message property.

        Used in All-Link Cleanup message types.
        """
        hi_byte = None
        if self.target.addr is not None and self._messageFlags.isBroadcast:
            hi_byte = self.target.bytes[2]
        return hi_byte

    def _message_properties(self):
        return [{'address': self._address},
                {'target': self._target},
                {'flags': self._messageFlags},
                {'cmd1': self._cmd1},
                {'cmd2': self._cmd2}]
