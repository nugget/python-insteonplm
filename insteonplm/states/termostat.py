"""Thermostat states."""

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

class Termostat(State):
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
        """Initialize the State state."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

    def _sensor_on_command_received(self, msg):
        """Message handler for Standard or Extended sensor on messages.

        Message handler for Standard (0x50) or Extended (0x51) message commands
        0x11 Sensor On.  When a message is received any state listeners are
        updated with 0x11 for on.
        """
        self._update_subscribers(msg.cmd2)

    def _sensor_off_command_received(self, msg):
        """Message handler for Standard or Extended sensor off messages.

        Message handler for Standard (0x50) or Extended (0x51) message commands
        0x11 Sensor On.  When a message is received any state listeners are
        updated with 0x13 for off.
        """
        self._update_subscribers(0x00)

    def _register_messages(self):
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
