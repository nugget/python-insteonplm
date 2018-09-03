"""X10 states."""
import logging

from insteonplm.messages.x10send import X10Send
from insteonplm.messages.x10received import X10Received
from insteonplm.states import State
from insteonplm.constants import (X10_COMMAND_ALL_UNITS_OFF,
                                  X10_COMMAND_ALL_LIGHTS_ON,
                                  X10_COMMAND_ALL_LIGHTS_OFF,
                                  X10_COMMAND_ON,
                                  X10_COMMAND_OFF,
                                  X10_COMMAND_DIM,
                                  X10_COMMAND_BRIGHT)


_LOGGER = logging.getLogger(__name__)


class X10OnOffSwitch(State):
    """On / Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the X10OnOff state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._register_messages()

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

    # pylint: disable=unused-argument
    def _on_message_received(self, msg):
        """Receive an ON message."""
        self._update_subscribers(0xff)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        """Receive an OFF message."""
        self._update_subscribers(0x00)

    def _register_messages(self):
        on_msg = X10Received.command_msg(self.address.x10_housecode,
                                         X10_COMMAND_ON)
        off_msg = X10Received.command_msg(self.address.x10_housecode,
                                          X10_COMMAND_OFF)
        all_on_msg = X10Received.command_msg(self.address.x10_housecode,
                                             X10_COMMAND_ALL_LIGHTS_ON)
        all_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                              X10_COMMAND_ALL_LIGHTS_OFF)
        all_units_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                                    X10_COMMAND_ALL_UNITS_OFF)

        self._message_callbacks.add(on_msg,
                                    self._on_message_received)
        self._message_callbacks.add(off_msg,
                                    self._off_message_received)
        self._message_callbacks.add(all_on_msg,
                                    self._on_message_received)
        self._message_callbacks.add(all_off_msg,
                                    self._off_message_received)
        self._message_callbacks.add(all_units_off_msg,
                                    self._off_message_received)


class X10DimmableSwitch(X10OnOffSwitch):
    """Dimmable X10 Switch."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=0, dim_steps=22):
        """Init the Dimmable state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._steps = dim_steps

    @property
    def steps(self):
        """Return the number of steps from OFF to full ON."""
        return self._steps

    @steps.setter
    def steps(self, val: int):
        """Set the number of steps from OFF to full ON."""
        self._steps = val

    def set_level(self, val):
        """Set the device ON LEVEL."""
        if val == 0:
            self.off()
        elif val == 255:
            self.on()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val * 255
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
                self._value = max(0, self._value)
            # pylint: disable=unused-variable
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

    # pylint: disable=unused-argument
    def _dim_message_received(self, msg):
        val = max(self._value - (255 / self._steps), 0)
        self._update_subscribers(val)

    # pylint: disable=unused-argument
    def _bright_message_received(self, msg):
        val = min(self._value + (255 / self._steps), 255)
        self._update_subscribers(val)

    def _register_messages(self):
        super()._register_messages()
        dim_msg = X10Received.command_msg(self.address.x10_housecode,
                                          X10_COMMAND_DIM)
        bri_msg = X10Received.command_msg(self.address.x10_housecode,
                                          X10_COMMAND_BRIGHT)
        self._message_callbacks.add(dim_msg,
                                    self._dim_message_received)
        self._message_callbacks.add(bri_msg,
                                    self._bright_message_received)


class X10OnOffSensor(State):
    """On / Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the X10OnOff state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._register_messages()

    # pylint: disable=unused-argument
    def _on_message_received(self, msg):
        """Receive an ON message."""
        self._update_subscribers(0xff)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        """Receive an OFF message."""
        self._update_subscribers(0x00)

    def _register_messages(self):
        on_msg = X10Received.command_msg(self.address.x10_housecode,
                                         X10_COMMAND_ON)
        off_msg = X10Received.command_msg(self.address.x10_housecode,
                                          X10_COMMAND_OFF)
        all_units_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                                    X10_COMMAND_ALL_UNITS_OFF)

        self._message_callbacks.add(on_msg,
                                    self._on_message_received)
        self._message_callbacks.add(off_msg,
                                    self._off_message_received)
        self._message_callbacks.add(all_units_off_msg,
                                    self._off_message_received)


class X10AllUnitsOffSensor(State):
    """All Units Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=0xff):
        """Init the X10AllUnitsOff state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._register_messages()

    def reset(self):
        """Reset the state to ON."""
        self._update_subscribers(0xff)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        """Receive an OFF message."""
        self._update_subscribers(0x00)

    def _register_messages(self):
        all_units_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                                    X10_COMMAND_ALL_UNITS_OFF)
        self._message_callbacks.add(all_units_off_msg,
                                    self._off_message_received)


class X10AllLightsOnSensor(State):
    """All Units Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=0x00):
        """Init the X10AllLightsOn state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._register_messages()

    def reset(self):
        """Reset the state to OFF."""
        self._update_subscribers(0x00)

    # pylint: disable=unused-argument
    def _on_message_received(self, msg):
        """Receive an ON message."""
        self._update_subscribers(0xff)

    def _register_messages(self):
        all_on_msg = X10Received.command_msg(self.address.x10_housecode,
                                             X10_COMMAND_ALL_LIGHTS_ON)
        self._message_callbacks.add(all_on_msg,
                                    self._on_message_received)


class X10AllLightsOffSensor(State):
    """All Lights Off state for an X10 device."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=0xff):
        """Init the X10AllLightsOff state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._register_messages()

    def reset(self):
        """Reset the state to ON."""
        self._update_subscribers(0xff)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        """Receive an OFF message."""
        self._update_subscribers(0x00)

    def _register_messages(self):
        all_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                              X10_COMMAND_ALL_LIGHTS_OFF)
        self._message_callbacks.add(all_off_msg,
                                    self._off_message_received)
