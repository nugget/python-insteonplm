"""X10 states."""

from insteonplm.messages.x10send import X10Send
from insteonplm.messages.x10received import X10Received
from insteonplm.states import State
from insteonplm.constants import (X10_COMMAND_ON,
                                  X10_COMMAND_OFF,
                                  X10_COMMAND_DIM,
                                  X10_COMMAND_BRIGHT)


class X10OnOffSwitch(State):
    """On / Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Initialize the X10OnOff state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        on_msg = X10Received.command_msg(address.x10_housecode,
                                         X10_COMMAND_ON)
        off_msg = X10Received.command_msg(address.x10_housecode,
                                          X10_COMMAND_OFF)
        self._message_callbacks.add(on_msg,
                                    self._on_message_received)
        self._message_callbacks.add(off_msg,
                                    self._off_message_received)

    def on(self):
        """Send the On command to an X10 device."""
        msg = X10Send.unit_code_msg(self.address.x10_housecode,
                                    self.address.x10_unitcode)
        self._send_method(msg)

        msg = X10Send.command_msg(self.address.x10_housecode,
                                  X10_COMMAND_ON)
        self._send_method(msg, False)
        self._update_subscribers(0xff)

    def off(self):
        """Send the Off command to an X10 device."""
        msg = X10Send.unit_code_msg(self.address.x10_housecode,
                                    self.address.x10_unitcode)
        self._send_method(msg)

        msg = X10Send.command_msg(self.address.x10_housecode,
                                  X10_COMMAND_OFF)
        self._send_method(msg, False)
        self._update_subscribers(0x00)

    def _on_message_received(self, msg):
        """An ON has been received."""
        self._update_subscribers(0xff)

    def _off_message_received(self, msg):
        """An OFF has been received."""
        self._update_subscribers(0x00)


class X10DimmableSwitch(X10OnOffSwitch):
    """Dimmable X10 Switch."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=0):
        """Initialize the Dimmable state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._steps = 22

        dim_msg = X10Received.command_msg(address.x10_housecode,
                                          X10_COMMAND_DIM)
        bri_msg = X10Received.command_msg(address.x10_housecode,
                                          X10_COMMAND_BRIGHT)
        self._message_callbacks.add(dim_msg,
                                    self._dim_message_received)
        self._message_callbacks.add(bri_msg,
                                    self._bright_message_received)

    @property
    def steps(self):
        """Number of steps from OFF to full ON."""
        return self._div_steps

    @steps.setter
    def steps(self, val: int):
        """Set the number of steps from OFF to full ON."""
        self._dim_steps = val

    def set_level(self, val):
        """Set the device ON LEVEL."""
        if val == 0:
            self.off()
        elif val == 255:
            self.on()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val*255
            elif val <= 0xff:
                setlevel = val
            change = setlevel - self._value
            increment = 255 / self._steps
            steps = round(abs(change) / increment)
            print('Steps: ', steps)
            if change > 0:
                method = self.brighten
                self._value += round(steps * increment)
                self._value = min(255, self._value)
            else:
                method = self.dim
                self._value -= round(steps * increment)
                self._value == max(0, self._value)
            for step in range(0, steps):
                method(True)
            self._update_subscribers(self._value)

    def brighten(self, defer_update=False):
        """Brighten the device one step."""
        msg = X10Send.unit_code_msg(self.address.x10_housecode,
                                    self.address.x10_unitcode)
        self._send_method(msg)

        msg = X10Send.command_msg(self.address.x10_housecode,
                                  X10_COMMAND_BRIGHT)
        self._send_method(msg, False)
        if not defer_update:
            self._update_subscribers(self._value + 255 / self._steps)

    def dim(self, defer_update=False):
        """Dim the device one step."""
        msg = X10Send.unit_code_msg(self.address.x10_housecode,
                                    self.address.x10_unitcode)
        self._send_method(msg)

        msg = X10Send.command_msg(self.address.x10_housecode,
                                  X10_COMMAND_DIM)
        self._send_method(msg, False)
        if not defer_update:
            self._update_subscribers(self._value - 255 / self._steps)

    def _dim_message_received(self, msg):
        val = max(self._value - (255 / self._steps), 0)
        self._update_subscribers(val)

    def _bright_message_received(self, msg):
        val = min(self._value + (255 / self._steps), 255)
        self._update_subscribers(val)
