
"""Sensor states."""

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

class SensorBase(State):
    """Base state representing a variable value sensor that is not controllable.

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
        """Initialize the State state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        template_on_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None))
        template_off_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None),
            cmd2=None)

        template_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))
        template_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)

        template_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=self._group)
        template_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=self._group)

        self._message_callbacks.add(template_on_broadcast,
                                    self._sensor_on_command_received)
        self._message_callbacks.add(template_off_broadcast,
                                    self._sensor_off_command_received)

        self._message_callbacks.add(template_on_cleanup,
                                    self._sensor_on_command_received)
        self._message_callbacks.add(template_off_cleanup,
                                    self._sensor_off_command_received)

        self._message_callbacks.add(template_on_group,
                                    self._sensor_on_command_received)
        self._message_callbacks.add(template_off_group,
                                    self._sensor_off_command_received)

    def _sensor_on_command_received(self, msg):
        """Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor On.

        When a message is received any state listeners are updated with the
        value in cmd2.
        """
        self._update_subscribers(msg.cmd2)

    def _sensor_off_command_received(self, msg):
        """Message handler for Standard (0x50) or Extended (0x51) message commands 0x13 Sensor Off.

        When a message is received any state listeners are updated with 0x00 for off.
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

    def _sensor_on_command_received(self, msg):
        """Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor On.

        When a message is received any state listeners are updated with 0x01 for on.
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
        """Initialize the State state."""
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
            target=bytearray([0x00, 0x00, self._group]),
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
        """Initialize the IoLinkSensor."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        template_open_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None))
        template_close_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None),
            cmd2=None)

        template_open_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))
        template_close_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)

        template_open_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=self._group)
        template_close_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=self._group)

        self._message_callbacks.add(template_open_broadcast,
                                    self._open_message_received)
        self._message_callbacks.add(template_close_broadcast,
                                    self._close_message_received)

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

    def _open_message_received(self, msg):
        self._update_subscribers(0x01)

    def _close_message_received(self, msg):
        self._update_subscribers(0x00)

    def _status_message_received(self, msg):
        if msg.cmd2 == 0x00:
            self._update_subscribers(0x00)
        else:
            self._update_subscribers(0x01)
