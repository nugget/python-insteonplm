"""Dimmable light states."""

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

from insteonplm.states.onOff import OnOffKeypadLed
from insteonplm.const import (COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                              COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00,
                              COMMAND_EXTENDED_GET_SET_0X2E_0X00,
                              MESSAGE_TYPE_DIRECT_MESSAGE)
from insteonplm.messsages.userdata import Userdata
from insteonplm.messages.extendedSend import ExtendedSend
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
        """Initalize the DimmableSwitch Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self.log.debug('Registering callbacks for DimmableSwitch device %s',
                       self._address.human)
        template_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))
        template_on_fast_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None))
        template_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)
        template_off_fast_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)
        template_manual_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)
        template_instant_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)
        template_manual_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)
        template_manual_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=None)

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
                setlevel = val*100
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
        self._update_subscribers(msg.cmd2)

    def _off_message_received(self, msg):
        self._update_subscribers(0x00)

    def _manual_change_received(self, msg):
        self._send_status_request()

    def _send_status_request(self):
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        self._send_method(status_command, self._status_message_received)

    def _status_message_received(self, msg):
        self._update_subscribers(msg.cmd2)


class DimmableSwitch_Fan(State):
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
        """Initalize the DimmableSwitch_Fan Class."""
        super().__init__(address, statename, group, send_message_method,
                         set_message_callback_method, defaultvalue)

        self._updatemethod = self._status_request
        self._udata = {'d1': self._group}

    def on(self):
        """Turn on the fan."""
        on_command = ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE,
                                  self._udata, cmd2=FAN_SPEED_MEDIUM)
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
            self._send_method(set_command, self._on_message_received)

    def off(self):
        """Turn off the fan."""
        off_command = ExtendedSend(self._address,
                                   COMMAND_LIGHT_OFF_0X13_0X00, self._udata)
        self._send_method(off_command, self._off_message_received)
        self.log.debug('Ending DimmableSwitch_Fan.off')

    def _on_message_received(self, msg):
        self._update_subscribers(0xff)

    def _off_message_received(self, msg):
        self._update_subscribers(0x00)

    def _status_request(self):
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE,
                                      cmd2=0x03)
        self._send_method(status_command, self._status_message_received)

    def _status_message_received(self, msg):
        self._update_subscribers(msg.cmd2)

    def _value_to_fan_speed(self, speed):
        if speed > 0xfe:
            return FAN_SPEED_HIGH
        elif speed > 0x7f:
            return FAN_SPEED_MEDIUM
        elif speed > 0:
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
        """Initalize the DimmableSwitch Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self.log.debug('Registering callbacks for DimmableSwitch device %s',
                       self._address.human)

        self._register_messages()

    def _on_message_received(self, msg):
        self.log.debug('Calling DimmableRemote _on_message_received '
                       'for group %d with level %d',
                       self._group, msg.cmd2)
        self._update_subscribers(0xff)

    def _off_message_received(self, msg):
        self.log.debug('Calling DimmableRemote _off_message_received '
                       'for group %d', self._group)
        self._update_subscribers(0x00)

    def _manual_change_received(self, msg):
        self.log.debug('Message type 0x17 or 0x18 received but no way '
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
                 message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request
        self._led = OnOffKeypadLed(address, "{}Led".format(statename), group,
                                   None, None)
        self._led.on_method = self._led_on
        self._led.off_method = self._led_off

    @property
    def led(self):
        """The LED state of the group/button."""
        return self._led

    def _led_on(self, group):
        self.on()

    def _led_off(self, group):
        self.off()

    def _on_message_received(self, msg):
        super()._on_message_received(msg)
        self._led.set_value(0xff)

    def _off_message_received(self, msg):
        super()._off_message_received(msg)
        self._led.set_value(0x00)

    def _send_status_request(self):
        switch_status_msg = StandardSend(
            self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        led_status_msg = StandardSend(
            self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01)
        self._send_method(switch_status_msg, self._status_message_received)
        self._send_method(led_status_msg, self._led_status_received)

    def _led_status_received(self, msg):
        self._led.set_value(msg.cmd2)


class DimmableKeypad(State):
    """Controllable keypad button dimmable switch."""

    def __init__(self, address, statename, group, send_message_method,
                 set_message_callback_method, defaultvalue=None):
        """Initialize the DimmableKeypad Class."""
        super().__init__(address, statename, group, send_message_method,
                         set_message_callback_method, defaultvalue)

        self._led = OnOffKeypadLed(self._address, "{}Led".format(statename),
                                   self._group, None, None)

        self._updatemethod = self._send_status_request

        self._on_mask = 0
        self._off_mask = 0
        self._x10_house_code = 0
        self._x10_unit = 0
        self._ramp_rate = 0
        self._led_brightness = 0
        self._non_toggle_mask = 0
        self._led_bit_mask = 0
        self._x10_all_bit_mask = 0
        self._on_off_bit_mask = 0

        self._sent_property = {}
        self._register_messages()

    @property
    def led(self):
        """The LED state of the group/button."""
        return self._led

    @property
    def scene(self):
        return self._scene_level

    def on(self):
        """Turn on the button/group."""
        on_cmd = self._create_set_property_msg(None, 0x06, 0xff)
        self._send_method(on_cmd, self._on_message_received)

    def off(self):
        """Turn off the button/group."""
        off_cmd = self._create_set_property_msg(None, 0x06, 0x00)
        self._send_method(off_cmd, self._off_message_received)

    def set_on_mask(self, mask):
        """Set the on mask for the current group/button."""
        set_cmd = self._create_set_property_msg('_on_mask', 0x02, mask)
        self._send_method(set_cmd, self._property_set)

    def set_off_mask(self, mask):
        """Set the off mask for the current group/button."""
        set_cmd = self._create_ext_msg('_off_mask', 0x03, mask)
        self._send_method(set_cmd, self._property_set)

    def set_x10_address(self, x10address):
        """Set the X10 address for the current group/button."""
        set_cmd = self._create_set_property_msg('_x10_house_code', 0x04,
                                                x10address)
        self._send_method(set_cmd, self._property_set)

    def set_ramp_rate(self, ramp_rate):
        """Set the X10 address for the current group/button."""
        set_cmd = self._create_set_property_msg('_ramp_rate', 0x05,
                                                ramp_rate)
        self._send_method(set_cmd, self._property_set)

    def scene_on(self):
        """Trigger group/scene to ON level."""
        user_data = Userdata({'d1': self._group,
                              'd2': 0x00,
                              'd3': 0x00,
                              'd4': 0x11,
                              'd5': 0xff,
                              'd6': 0x00})
        self._set_sent_property(DIMMABLE_KEYPAD_SCENE_ON_LEVEL, 0xff)
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00,
                           user_data)
        self.log.debug('Calling scene_on and sending reponse to '
                       '_received_scene_triggered')
        self._send_method(cmd, self._received_scene_triggered)

    def scene_off(self):
        """Trigger group/scene to OFF level."""
        user_data = Userdata({'d1': self._group,
                              'd2': 0x00,
                              'd3': 0x00,
                              'd4': 0x13,
                              'd5': 0x00,
                              'd6': 0x00})
        self._set_sent_property(DIMMABLE_KEYPAD_SCENE_ON_LEVEL, 0x00)
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00,
                           user_data)
        self._send_method(cmd, self._received_scene_triggered)

    def scene_level(self, level):
        """Trigger group/scene to input level."""
        if level == 0:
            self.trigger_off()
        else:
            user_data = Userdata({'d1': self._group,
                                  'd2': 0x00,
                                  'd3': 0x00,
                                  'd4': 0x11,
                                  'd5': level,
                                  'd6': 0x00})
            self._set_sent_property(DIMMABLE_KEYPAD_SCENE_ON_LEVEL, level)
            cmd = ExtendedSend(self._address,
                               COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00,
                               user_data)
            self._send_method(cmd, self._received_scene_triggered)

    def _on_message_received(self, msg):
        self._update_subscribers(0xff)

    def _off_message_received(self, msg):
        self._update_subscribers(0x00)

    def _manual_change_received(self, msg):
        self._send_status_request()

    def _send_status_request(self):
        """Send status request for group/button."""
        user_data = Userdata({'d1': self.group,
                              'd2': 0x00})
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_GET_SET_0X2E_0X00,
                           userdata=user_data)
        self._send_method(cmd, self._status_message_received)

    def _status_message_received(self, msg):
        """Confirmation that the status message is coming.

        The real status message is the extended direct message.
        """
        self.log.debug('Status message was acknowledged')

    def _status_extended_message_received(self, msg):
        """ Status message received.:

            cmd1:  0x2e
            cmd2:  0x00
            flags: Direct Extended
            d1:    group
            d2:    0x01
            d3:    On Mask
            d4:    Off Mask
            d5:    X10 House Code
            d6:    X10 Unit
            d7:    Ramp Rate
            d8:    On-Level
            d9:    LED Brightness
            d10:   Non-Toggle Mask
            d11:   LED Bit Mask
            d12:   X10 ALL Bit Mask
            d13:   On/Off Bit Mask
            d14:   Check sum
        """
        user_data = msg.userdata
        self._update_subscribers(user_data['d8'])
        self._set_status_data(user_data)

    def _property_set(self, msg):
        """Set command received and acknowledged."""
        prop = self._sent_property.get('val')
        if prop and hasattr(self, prop):
            setattr(self, prop, self._sent_property.get('val'))
        self._sent_property = {}

    def _received_scene_triggered(self, msg):
        scene_level = self._sent_property.get('prop')
        val = self._sent_property.get('val')
        self.log.debug('Calling DimmableKeypad _received_scene_triggered '
                       'for group %s with on level %s',
                       self._group, scene_level)
        if scene_level == DIMMABLE_KEYPAD_SCENE_ON_LEVEL:
            self._update_subscribers(val)

    def _set_status_data(self, userdata):
        """Set status properties from userdata response.

        Response values:
            d3:  On Mask
            d4:  Off Mask
            d5:  X10 House Code
            d6:  X10 Unit
            d7:  Ramp Rate
            d8:  On-Level
            d9:  LED Brightness
            d10: Non-Toggle Mask
            d11: LED Bit Mask
            d12: X10 ALL Bit Mask
            d13: On/Off Bit Mask
        """
        self._on_mask = userdata['d3']
        self._off_mask = userdata['d4']
        self._x10_house_code = userdata['d5']
        self._x10_unit = userdata['d6']
        self._ramp_rate = userdata['d7']
        self._led_brightness = userdata['d9']
        self._non_toggle_mask = userdata['d10']
        self._led_bit_mask = userdata['d11']
        self._x10_all_bit_mask = userdata['d12']
        self._on_off_bit_mask = userdata['d13']

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

        # Status message received
        template_status_recd = ExtendedReceive.template(
            address=self._address,
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE,
                                        True),
            userdata={'d1': self._group,
                      'd2': 0x01})
        self._message_callbacks.add(template_status_recd,
                                    self._status_extended_message_received)

    def _create_set_property_msg(self, prop, cmd, val):
        """Create an extended message to set a property.

        Create an extended message with:
            cmd1: 0x2e
            cmd2: 0x00
            flags: Direct Extended
            d1: group
            d2: cmd
            d3: val
            d4 - d14: 0x00
        """
        user_data = Userdata({'d1': self.group,
                              'd2': cmd,
                              'd3': val})
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_GET_SET_0X2E_0X00,
                           user_data)
        self._set_sent_property(prop, val)
        return cmd

    def _set_sent_property(self, prop, val):
        self._sent_property = {'prop': prop,
                               'val': val}
