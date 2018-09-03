"""Dimmable light states."""
import logging

from insteonplm.constants import (COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00,
                                  COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00,
                                  COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
                                  COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
                                  COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
                                  COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_ON_FAST_0X12_NONE,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE,
                                  COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
                                  FAN_SPEED_HIGH,
                                  FAN_SPEED_LOW,
                                  FAN_SPEED_MEDIUM,
                                  FAN_SPEED_OFF,
                                  MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.states import State

_LOGGER = logging.getLogger(__name__)
DIMMABLE_KEYPAD_SCENE_ON_LEVEL = "sceneOnLevel"


class DimmableSwitch(State):
    """Device state representing an On/Off switch that is controllable.

    Available methods are:
    on()
    off()
    set_level()
    brightent()
    dim()
    connect()
    update(self, val)
    async_refresh_state()
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the DimmableSwitch Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request
        self._register_messages()

    # pylint: disable=too-many-locals
    def _register_messages(self):
        _LOGGER.debug('Registering callbacks for DimmableSwitch device %s',
                      self._address.human)
        template_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_on_fast_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_off_fast_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_instant_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)

        template_on_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_on_fast_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_off_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_off_fast_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_instant_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_off_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_on_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)

        self._message_callbacks.add(template_on_cleanup,
                                    self._on_message_received)
        self._message_callbacks.add(template_on_fast_cleanup,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_cleanup,
                                    self._off_message_received)
        self._message_callbacks.add(template_off_fast_cleanup,
                                    self._off_message_received)
        self._message_callbacks.add(template_manual_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_instant_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_on_cleanup,
                                    self._manual_change_received)

        self._message_callbacks.add(template_on_broadcast,
                                    self._on_message_received)
        self._message_callbacks.add(template_on_fast_broadcast,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_broadcast,
                                    self._off_message_received)
        self._message_callbacks.add(template_off_fast_broadcast,
                                    self._off_message_received)
        self._message_callbacks.add(template_manual_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_instant_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_on_broadcast,
                                    self._manual_change_received)

    def on(self):
        """Turn the device ON."""
        on_command = StandardSend(self._address,
                                  COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
        self._send_method(on_command, self._on_message_received)

    def off(self):
        """Turn the device off."""
        off_command = StandardSend(self._address,
                                   COMMAND_LIGHT_OFF_0X13_0X00)
        self._send_method(off_command, self._off_message_received)

    def set_level(self, val):
        """Set the devive ON LEVEL."""
        if val == 0:
            self.off()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val * 100
            elif val <= 0xff:
                setlevel = val
            set_command = StandardSend(
                self._address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=setlevel)
            self._send_method(set_command, self._on_message_received)

    def brighten(self):
        """Brighten the device one step."""
        brighten_command = StandardSend(
            self._address, COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00)
        self._send_method(brighten_command)

    def dim(self):
        """Dim the device one step."""
        dim_command = StandardSend(
            self._address, COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00)
        self._send_method(dim_command)

    def _on_message_received(self, msg):
        cmd2 = msg.cmd2 if msg.cmd2 else 255
        self._update_subscribers(cmd2)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        self._update_subscribers(0x00)

    # pylint: disable=unused-argument
    def _manual_change_received(self, msg):
        self._send_status_request()

    def _send_status_request(self):
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        self._send_method(status_command, self._status_message_received)

    def _status_message_received(self, msg):
        _LOGGER.debug("DimmableSwitch status message received called")
        self._update_subscribers(msg.cmd2)


class DimmableSwitch_Fan(DimmableSwitch):
    """Device state representing a controlable bottom outlet On/Off switch.

    Available methods are:
    on(self)
    off(self)
    async_refresh_state(self)
    connect(self, call_back)
    update(self, val)
    async_refresh_state(self)
    """

    def __init__(self, address, statename, group, send_message_method,
                 set_message_callback_method, defaultvalue=None):
        """Init the DimmableSwitch_Fan Class."""
        super().__init__(address, statename, group, send_message_method,
                         set_message_callback_method, defaultvalue)

        self._updatemethod = self._status_request
        self._udata = {'d1': self._group}

    def on(self):
        """Turn on the fan."""
        on_command = ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE,
                                  self._udata, cmd2=FAN_SPEED_MEDIUM)
        on_command.set_checksum()
        self._send_method(on_command, self._on_message_received)

    def set_level(self, val):
        """Set the fan speed."""
        speed = self._value_to_fan_speed(val)
        if val == 0:
            self.off()
        else:
            set_command = ExtendedSend(self._address,
                                       COMMAND_LIGHT_ON_0X11_NONE,
                                       self._udata, cmd2=speed)
            set_command.set_checksum()
            self._send_method(set_command, self._on_message_received)

    def off(self):
        """Turn off the fan."""
        off_command = ExtendedSend(self._address,
                                   COMMAND_LIGHT_OFF_0X13_0X00, self._udata)
        off_command.set_checksum()
        self._send_method(off_command, self._off_message_received)
        _LOGGER.debug('Ending DimmableSwitch_Fan.off')

    def _status_request(self):
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE,
                                      cmd2=0x03)
        self._send_method(status_command, self._status_message_received)

    def _status_message_received(self, msg):
        self._update_subscribers(msg.cmd2)

    # pylint: disable=no-self-use
    def _value_to_fan_speed(self, speed):
        if speed > 0xfe:
            return FAN_SPEED_HIGH
        if speed > 0x7f:
            return FAN_SPEED_MEDIUM
        if speed > 0:
            return FAN_SPEED_LOW
        return FAN_SPEED_OFF


class DimmableRemote(State):
    """Device state representing dimmable keypad switch that is not controllable.

    Available methods are:
    connect()
    update(self, val)
    async_refresh_state()
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the DimmableSwitch Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        _LOGGER.debug('Registering callbacks for DimmableSwitch device %s',
                      self._address.human)

        self._is_responder = False

        self._register_messages()

    def _on_message_received(self, msg):
        _LOGGER.debug('Calling DimmableRemote _on_message_received '
                      'for group %d with level %d',
                      self._group, msg.cmd2)
        self._update_subscribers(0xff)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        _LOGGER.debug('Calling DimmableRemote _off_message_received '
                      'for group %d', self._group)
        self._update_subscribers(0x00)

    # pylint: disable=no-self-use
    # pylint: disable=unused-argument
    def _manual_change_received(self, msg):
        _LOGGER.debug('Message type 0x17 or 0x18 received but no way '
                      'to properly handle them, sorry.')

    def _register_messages(self):
        template_on_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_on_fast_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_off_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_off_fast_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_instant_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_off_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_on_broadcast = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)

        self._message_callbacks.add(template_on_broadcast,
                                    self._on_message_received)
        self._message_callbacks.add(template_on_fast_broadcast,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_broadcast,
                                    self._off_message_received)
        self._message_callbacks.add(template_off_fast_broadcast,
                                    self._off_message_received)
        self._message_callbacks.add(template_manual_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_instant_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_on_broadcast,
                                    self._manual_change_received)


class DimmableKeypadA(DimmableSwitch):
    """Device state for a controllable keypad button A On/Off switch."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue, leds):
        """Init the DimmableKeypadA class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request
        self._leds = leds

    def led_on(self):
        """Turn the LED on."""
        self._leds.on(self._group)

    def led_off(self):
        """Turn the LED off."""
        self._leds.off(self._group)

    def led_is_on(self):
        """Return if the LED is on."""
        return self._leds.is_on(self._group)

    def _on_message_received(self, msg):
        super()._on_message_received(msg)
        self._leds.async_refresh_state()

    def _off_message_received(self, msg):
        super()._off_message_received(msg)
        self._leds.async_refresh_state()

    def _send_status_request(self):
        switch_status_msg = StandardSend(
            self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        self._send_method(switch_status_msg, self._status_message_received)
