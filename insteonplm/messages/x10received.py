"""INSTEON Message X10 Received."""
from insteonplm.messages.message import Message
from insteonplm.constants import (MESSAGE_X10_MESSAGE_RECEIVED_0X52,
                                  MESSAGE_X10_MESSAGE_RECEIVED_SIZE)
import insteonplm.utils


class X10Received(Message):
    """Insteon X10 Received Message.

    Message type 0x52
    """

    _code = MESSAGE_X10_MESSAGE_RECEIVED_0X52
    _sendSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    _receivedSize = MESSAGE_X10_MESSAGE_RECEIVED_SIZE
    _description = 'Insteon Get Next All Link Record Message'

    def __init__(self, rawX10, flag):
        """Init X10Received Class."""
        self._rawX10 = rawX10
        self._flag = flag

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create from raw byte stream."""
        return X10Received(rawmessage[2], rawmessage[3])

    @property
    def rawX10(self):
        """Return raw X10 message."""
        return self._rawX10

    @property
    def flag(self):
        """Return X10 flag."""
        return self._flag

    @staticmethod
    def unit_code_msg(housecode, unitcode):
        """Create an X10 message to send the house code and unit code."""
        house_byte = 0
        unit_byte = 0
        if isinstance(housecode, str):
            house_byte = insteonplm.utils.housecode_to_byte(housecode) << 4
            unit_byte = insteonplm.utils.unitcode_to_byte(unitcode)
        elif isinstance(housecode, int) and housecode < 16:
            house_byte = housecode << 4
            unit_byte = unitcode
        else:
            house_byte = housecode
            unit_byte = unitcode
        return X10Received(house_byte + unit_byte, 0x00)

    @staticmethod
    def command_msg(housecode, command):
        """Create an X10 message to send the house code and a command code."""
        house_byte = 0
        if isinstance(housecode, str):
            house_byte = insteonplm.utils.housecode_to_byte(housecode) << 4
        elif isinstance(housecode, int) and housecode < 16:
            house_byte = housecode << 4
        else:
            house_byte = housecode
        return X10Received(house_byte + command, 0x80)

    def _message_properties(self):
        return [{'rawX10': self._rawX10},
                {'flag': self._flag}]
