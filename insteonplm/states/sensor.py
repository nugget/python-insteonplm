
"""Sensor states."""
from enum import Enum
from insteonplm.constants import (COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                                  MESSAGE_TYPE_BROADCAST_MESSAGE,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP,
                                  MESSAGE_TYPE_ALL_LINK_BROADCAST)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.states import State


class LeakSensorState(Enum):
    """Enum to define dry/wet state of the leak sensor."""

    DRY = 0
    WET = 1


class SensorBase(State):
    """Base state representing a non-controlable variable value sensor.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      register_updates(self, callback)
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the State state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._is_responder = False

        template_on_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None),
            cmd2=None)
        template_off_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None),
            cmd2=None)

        template_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)

        self._message_callbacks.add(template_on_broadcast,
                                    self._sensor_on_command_received)
        self._message_callbacks.add(template_off_broadcast,
                                    self._sensor_off_command_received)

        self._message_callbacks.add(template_on_group,
                                    self._sensor_on_command_received)
        self._message_callbacks.add(template_off_group,
                                    self._sensor_off_command_received)

    # pylint: disable=unused-argument
    def _sensor_on_command_received(self, msg):
        """Message handler for Standard or Extended sensor on messages.

        Message handler for Standard (0x50) or Extended (0x51) message commands
        0x11 Sensor On.  When a message is received any state listeners are
        updated with 0x11 for on.
        """
        self._update_subscribers(msg.cmd2)

    # pylint: disable=unused-argument
    def _sensor_off_command_received(self, msg):
        """Message handler for Standard or Extended sensor off messages.

        Message handler for Standard (0x50) or Extended (0x51) message commands
        0x11 Sensor On.  When a message is received any state listeners are
        updated with 0x13 for off.
        """
        self._update_subscribers(0x00)


class VariableSensor(SensorBase):
    """Device state representing a variable value sensor that is not controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      register_updates(self, callback)
    """


class OnOffSensor(SensorBase):
    """Device state representing an On/Off sensor that is not controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
    - register_updates(self, callback)
    """

    # pylint: disable=unused-argument
    def _sensor_on_command_received(self, msg):
        """Message handler for Standard or Extended sensor on messages.

        Message handler for Standard (0x50) or Extended (0x51) message commands
        0x11 Sensor On.  When a message is received any state listeners are
        updated with 0x11 for on.
        """
        self._update_subscribers(0x01)


class SmokeCO2Sensor(SensorBase):
    """Device state representing a Smoke/CO2 sensor that is not controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
    - register_updates(self, callback)
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the State state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        template_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None))
        template_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))
        template_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))

        self._message_callbacks.add(template_broadcast,
                                    self._sensor_state_received)
        self._message_callbacks.add(template_cleanup,
                                    self._sensor_state_received)
        self._message_callbacks.add(template_group,
                                    self._sensor_state_received)

    def _sensor_state_received(self, msg):
        self._update_subscribers(msg.targetHi)


class IoLincSensor(SensorBase):
    """Device state representing a I/O Linc Sensor that is not controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
    - register_updates(self, callback)
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the IoLinkSensor."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def _register_messages(self):
        # The actual group number is 0x01 for the IOLinc sensor so this
        # is hard coded in these template messages
        template_close_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=0x01)
        template_open_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=0x01)

        template_close_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, 0x01]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_open_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, 0x01]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)

        self._message_callbacks.add(template_open_cleanup,
                                    self._open_message_received)
        self._message_callbacks.add(template_close_cleanup,
                                    self._close_message_received)

        self._message_callbacks.add(template_open_group,
                                    self._open_message_received)
        self._message_callbacks.add(template_close_group,
                                    self._close_message_received)

    def _send_status_request(self):
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01)
        self._send_method(status_command, self._status_message_received)

    # pylint: disable=unused-argument
    def _open_message_received(self, msg):
        self._update_subscribers(0x00)

    # pylint: disable=unused-argument
    def _close_message_received(self, msg):
        self._update_subscribers(0x01)

    def _status_message_received(self, msg):
        if msg.cmd2 == 0x00:
            # 0x00 is open
            self._update_subscribers(0x00)
        else:
            self._update_subscribers(0x01)


class LeakSensorDryWet(State):
    """Water leak sensor for the Dry or Wet states.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
    - register_updates(self, callback)
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None,
                 dry_wet=None):
        """Init the LeakSensorDry state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._dry_wet_type = dry_wet
        self._dry_wet_callbacks = []

        template_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None))

        template_all_link = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))

        template_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))

        self._message_callbacks.add(template_broadcast,
                                    self._dry_wet_message_received)

        self._message_callbacks.add(template_all_link,
                                    self._dry_wet_message_received)

        self._message_callbacks.add(template_cleanup,
                                    self._dry_wet_message_received)

    def register_dry_wet_callback(self, callback):
        """Register the callback for the wet and dry state callbacks."""
        self._dry_wet_callbacks.append(callback)

    def set_value(self, dry_wet: LeakSensorState):
        """Set the value of the state to dry or wet."""
        value = 0
        if dry_wet == self._dry_wet_type:
            value = 1
        self._update_subscribers(value)

    # pylint: disable=unused-argument
    def _dry_wet_message_received(self, msg):
        """Report a dry or a wet state."""
        for callback in self._dry_wet_callbacks:
            callback(self._dry_wet_type)
        self._update_subscribers(0x01)


class LeakSensorHeartbeat(State):
    """Water leak sensor for the Dry state.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
    - register_updates(self, callback)
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the LeakSensorDry state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._dry_wet_callbacks = []

        template_dry_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            cmd2=self._group,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None))

        template_wet_broadcast = StandardReceive.template(
            commandtuple={'cmd1': 0x13, 'cmd2': self._group},
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None))

        template_dry_all_link = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            cmd2=self._group,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))

        template_wet_all_link = StandardReceive.template(
            commandtuple={'cmd1': 0x13, 'cmd2': self._group},
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))

        template_dry_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            cmd2=self._group,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))

        template_wet_cleanup = StandardReceive.template(
            commandtuple={'cmd1': 0x13, 'cmd2': self._group},
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))

        self._message_callbacks.add(template_dry_broadcast,
                                    self._dry_message_received)
        self._message_callbacks.add(template_wet_broadcast,
                                    self._wet_message_received)
        self._message_callbacks.add(template_dry_all_link,
                                    self._dry_message_received)
        self._message_callbacks.add(template_wet_all_link,
                                    self._wet_message_received)
        self._message_callbacks.add(template_dry_cleanup,
                                    self._dry_message_received)
        self._message_callbacks.add(template_wet_cleanup,
                                    self._wet_message_received)

    def register_dry_wet_callback(self, callback):
        """Register the callback for the wet and dry state callbacks."""
        self._dry_wet_callbacks.append(callback)

    def set_value(self, dry_wet: LeakSensorState):
        """Set the state to wet or dry."""
        if dry_wet == LeakSensorState.DRY:
            self._update_subscribers(0x11)
        else:
            self._update_subscribers(0x13)

    # pylint: disable=unused-argument
    def _dry_message_received(self, msg):
        """Report a dry state."""
        for callback in self._dry_wet_callbacks:
            callback(LeakSensorState.DRY)
        self._update_subscribers(0x11)

    # pylint: disable=unused-argument
    def _wet_message_received(self, msg):
        """Report a wet state."""
        for callback in self._dry_wet_callbacks:
            callback(LeakSensorState.WET)
        self._update_subscribers(0x13)
