"""X10 states."""

from insteonplm.messages.x10send import X10Send
from insteonplm.states import State

X10_COMMAND_ALL_UNITS_OFF = 0x00
X10_COMMAND_ALL_LIGHTS_ON = 0x01
X10_COMMAND_ALL_LIGHTS_OFF = 0x06
X10_COMMAND_ON = 0x02
X10_COMMAND_OFF = 0x03
X10_COMMAND_DIM = 0x04
X10_COMMAND_BRIGHT = 0x05
X10_COMMAND_EXTENDED_CODE = 0x07
X10_COMMAND_HAIL_REQUEST = 0x08
X10_COMMAND_HAIL_ACKNOWLEDGE = 0x09
X10_COMMAND_PRE_SET_DIM = 0x0A
X10_COMMAND_STATUS_IS_ON = 0x0B
X10_COMMAND_STATUS_IS_OFF = 0x0C
X10_COMMAND_STATUS_REQUEST = 0x0D


class X10OnOffSwitch(State):
    """On / Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Initialize the X10OnOff state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

    def on(self):
        """Send the On command to an X10 device."""
        print('X10 address:', self._address.human)
        print('Is X10 address:', self._address.is_x10)
        houseunitcode = (self._address.x10_housecode_byte +
                         self._address.x10_unitcode_byte)
        msg = X10Send(houseunitcode, 0x00)
        self._send_method(msg)

        housecmdcode = self._address.x10_housecode_byte + X10_COMMAND_ON
        msg = X10Send(housecmdcode, 0x80)
        self._send_method(msg)
        self._update_subscribers(0xff)

    def off(self):
        """Send the On command to an X10 device."""
        houseunitcode = (self._address.x10_housecode_byte +
                         self._address.x10_unitcode_byte)
        msg = X10Send(houseunitcode, 0x00)
        self._send_method(msg)

        housecmdcode = self._address.x10_housecode_byte + X10_COMMAND_OFF
        msg = X10Send(housecmdcode, 0x80)
        self._send_method(msg)
        self._update_subscribers(0x00)
