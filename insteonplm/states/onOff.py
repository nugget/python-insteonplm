"""On/Off states."""

from insteonplm.constants import (COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
                                  COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
                                  COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_ON_FAST_0X12_NONE,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                                  MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.states import State


class OnOffStateBase(State):
    """Base state representing an On/Off switch that is controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      register_updates()
      async_refresh_state()
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Initialize the OnOffStateBase."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def _on_message_received(self, msg):
        """An ON has been received."""
        self._update_subscribers(0xff)

    def _off_message_received(self, msg):
        """An OFF has been received."""
        self._update_subscribers(0x00)

    def _manual_change_received(self, msg):
        """A manual change message has been received."""
        self._send_status_request()

    def _send_status_request(self):
        """Send a status request message to the device."""
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        self._send_method(status_command,
                          self._status_message_received)

    def _status_message_received(self, msg):
        """A status message has been received."""
        if msg.cmd2 == 0x00:
            self._update_subscribers(0x00)
        else:
            self._update_subscribers(0xff)

    def _register_messages(self):
        """Register messages to listen for."""
        template_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_fast_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_fast_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)

        template_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_fast_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_fast_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)

        self._message_callbacks.add(template_on_group,
                                    self._on_message_received)
        self._message_callbacks.add(template_fast_on_group,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_group,
                                    self._off_message_received)
        self._message_callbacks.add(template_fast_off_group,
                                    self._off_message_received)
        self._message_callbacks.add(template_manual_on_group,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_group,
                                    self._manual_change_received)

        self._message_callbacks.add(template_on_cleanup,
                                    self._on_message_received)
        self._message_callbacks.add(template_fast_on_cleanup,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_cleanup,
                                    self._off_message_received)
        self._message_callbacks.add(template_fast_off_cleanup,
                                    self._off_message_received)
        self._message_callbacks.add(template_manual_on_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_cleanup,
                                    self._manual_change_received)


class OnOffSwitch(OnOffStateBase):
    """On/Off state representing an On/Off switch that is controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      on()
      off()
      register_updates()
      async_refresh_state()
    """

    def on(self):
        """Send ON command to device."""
        on_command = StandardSend(self._address,
                                  COMMAND_LIGHT_ON_0X11_NONE, 0xff)
        self._send_method(on_command,
                          self._on_message_received)

    def off(self):
        """Send OFF command to device."""
        off_command = StandardSend(self._address,
                                   COMMAND_LIGHT_OFF_0X13_0X00)
        self._send_method(off_command,
                          self._off_message_received)


class OnOffSwitch_OutletTop(OnOffStateBase):
    """Device state representing a controllable top outlet On/Off switch.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      on()
      off()
      register_updates()
      async_refresh_state()
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Initalize the OnOffSwitch_OutletTop Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_0x01_request

    def on(self):
        """Send ON command to device."""
        on_command = StandardSend(self._address,
                                  COMMAND_LIGHT_ON_0X11_NONE, 0xff)
        self._send_method(on_command, self._on_message_received)

    def off(self):
        """Send OFF command to device."""
        self._send_method(StandardSend(self._address,
                                       COMMAND_LIGHT_OFF_0X13_0X00),
                          self._off_message_received)

    def _send_status_0x01_request(self):
        """Sent status request to device."""
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01)
        self._send_method(status_command, self._status_message_0x01_received)

    def _status_message_0x01_received(self, msg):
        """Handle status received messages.

        The following status values can be recieve:
            0x00 = Both Outlets Off
            0x01 = Only Top Outlet On
            0x02 = Only Bottom Outlet On
            0x03 = Both Outlets On
        """
        if msg.cmd2 == 0x00 or msg.cmd2 == 0x02:
            self._update_subscribers(0x00)
        elif msg.cmd2 == 0x01 or msg.cmd2 == 0x03:
            self._update_subscribers(0xff)
        else:
            raise ValueError


class OnOffSwitch_OutletBottom(OnOffStateBase):
    """Device state representing a controllable bottom outlet On/Off switch.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      on()
      off()
      register_updates()
      async_refresh_state()
    """

    def __init__(self, address, statename, group, send_message_method,
                 set_message_callback_method, defaultvalue=None):
        """Initialize the OnOffSwitch_OutletBottom."""
        super().__init__(address, statename, group, send_message_method,
                         set_message_callback_method, defaultvalue)

        self._updatemethod = self._send_status_0x01_request
        self._udata = {'d1': self._group}

    def on(self):
        """Send an ON message to device group."""
        on_command = ExtendedSend(self._address,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  self._udata,
                                  cmd2=0xff)
        self._send_method(on_command, self._on_message_received)

    def off(self):
        """Send an OFF message to device group."""
        off_command = ExtendedSend(self._address,
                                   COMMAND_LIGHT_OFF_0X13_0X00,
                                   self._udata)
        self._send_method(off_command, self._off_message_received)

    def _send_status_0x01_request(self):
        """Send a status request."""
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01)
        self._send_method(status_command, self._status_message_received)

    def _status_message_received(self, msg):
        """A status message has been received.

        The following status values can be recieve:
            0x00 = Both Outlets Off
            0x01 = Only Top Outlet On
            0x02 = Only Bottom Outlet On
            0x03 = Both Outlets On
        """
        if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
            self._update_subscribers(0x00)
        elif msg.cmd2 == 0x02 or msg.cmd2 == 0x03:
            self._update_subscribers(0xff)
        else:
            raise ValueError


class OpenClosedRelay(OnOffStateBase):
    """Device state representing an Open/Close switch that is controllable.

    Available properties are:
      value
      name
      address
      group

    Available methods are:
      open()
      close()
      register_updates()
      async_refresh_state()
    """

    def open(self):
        """Send OPEN command to device."""
        open_command = StandardSend(self._address,
                                    COMMAND_LIGHT_ON_0X11_NONE, 0xff)
        self._send_method(open_command, self._open_message_received)

    def close(self):
        """Send CLOSE command to device."""
        close_command = StandardSend(self._address,
                                     COMMAND_LIGHT_OFF_0X13_0X00)
        self._send_method(close_command, self._close_message_received)

    def _open_message_received(self, msg):
        """An OPEN message has been received."""
        self._update_subscribers(0xff)

    def _close_message_received(self, msg):
        """A CLOSE message has been received."""
        self._update_subscribers(0x00)


class OnOffKeypadA(OnOffStateBase):
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


class OnOffKeypad(State):
    """Device state representing a controllable keypad button On/Off switch."""

    def __init__(self, address, statename, group, send_message_method,
                 set_message_callback_method, defaultvalue=None):
        """Initialize the OnOffKeypad Class."""
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
        return self._led

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
        set_cmd = self._create_set_property_msg('_off_mask', 0x03, mask)
        self._send_method(set_cmd, self._property_set)

    def set_x10_address(self, x10address):
        """Set the X10 address for the current group/button."""
        set_cmd = self._create_set_property_msg('_x10_house_code', 0x04,
                                                x10address)
        self._send_method(set_cmd, self._property_set)

    def set_ramp_rate(self, ramp_rate):
        """Set the X10 address for the current group/button."""
        set_cmd = self._create_ext_msg('_ramp_rate', 0x05, ramp_rate)
        self._send_method(set_cmd, self._property_set)

    def scene_on(self):
        """Trigger group/scene to ON level."""
        user_data = Userdata({'d1': self._group,
                              'd2': 0x00,
                              'd3': 0x00,
                              'd4': 0x11,
                              'd5': 0xff,
                              'd6': 0x00})
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00,
                           user_data)
        self._send_method(cmd, self._triggered_group)

    def scene_off(self):
        """Trigger group/scene to OFF level."""
        user_data = Userdata({'d1': self._group,
                              'd2': 0x00,
                              'd3': 0x00,
                              'd4': 0x13,
                              'd5': 0x00,
                              'd6': 0x00})
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00,
                           user_data)
        self._send_method(cmd, self._triggered_group)

    def _on_message_received(self, msg):
        self._update_subscribers(msg.cmd2)

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
        self._set_status_data(msg.userdata)
        self._update_subscribers(msg.userdata.get('d8'))

    def _property_set(self, msg):
        """Set command received and acknowledged."""
        prop = self._sent_property.get('val')
        if prop and hasattr(self, prop):
            setattr(self, prop, self._sent_property.get('val'))
        self._sent_property = {}

    def _triggered_group(self, msg):
        """Received acknowlegement the group/scene has been triggered."""
        pass

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
        self._on_mask = userdata.get('d3')
        self._off_mask = userdata.get('d4')
        self._x10_house_code = userdata.get('d5')
        self._x10_unit = userdata.get('d6')
        self._ramp_rate = userdata.get('d7')
        self._led_brightness = userdata.get('d9')
        self._non_toggle_mask = userdata.get('d10')
        self.led.set_value(userdata.get('d11'))
        self._x10_all_bit_mask = userdata.get('d12')
        self._on_off_bit_mask = userdata.get('d13')

    def _register_messages(self):
        """Register messages to listen for."""
        template_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_fast_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None))
        template_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_fast_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_on_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)
        template_manual_off_group = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
            address=self._address,
            target=bytearray([0x00, 0x00, self._group]),
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
            cmd2=None)

        self._message_callbacks.add(template_on_group,
                                    self._on_message_received)
        self._message_callbacks.add(template_fast_on_group,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_group,
                                    self._off_message_received)
        self._message_callbacks.add(template_fast_off_group,
                                    self._off_message_received)
        self._message_callbacks.add(template_manual_on_group,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_group,
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
                                    self._status_message_received)

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
        self._sent_property = {'prop': prop,
                               'val': val}
        return cmd


class OnOffKeypadLed(State):
    """Device state for KeyPadLinc LED."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self.on_method = None
        self.off_method = None

    def on(self):
        """Turn the LED on."""
        if self.on_method:
            self.on_method(self.group)

    def off(self):
        """Turn the LED off."""
        if self.off_method:
            self.off_method(self.group)

    def set_value(self, bitmask):
        """Set the LED on/off value from the LED bitmap."""
        is_on = bool(bitmask & 1 << self._group - 1)
        self._update_subscribers(1 if is_on else 0)
