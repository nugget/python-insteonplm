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
from insteonplm.messages import MessageFlags
from insteonplm.states import StateBase


class OnOffStateBase(StateBase):
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
    """Device state representing a the top outlet On/Off switch that is controllable.

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
        """
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
    """Device state representing a the bottom outlet On/Off switch that is controllable.

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
        """Initialize the OnOffSwitch_OutletBottom"""
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
