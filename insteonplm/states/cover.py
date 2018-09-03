"""Window Coverings states."""
import logging

from insteonplm.constants import (COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
                                  COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
                                  COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
                                  COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_ON_FAST_0X12_NONE,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
                                  MESSAGE_TYPE_ALL_LINK_BROADCAST)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.states import State

_LOGGER = logging.getLogger(__name__)


class Cover(State):
    """Device state representing cover that is controllable.

    Available methods are:
    open()
    close()
    set_position()
    async_refresh_state()
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Cover Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request
        self._register_messages()

    def _register_messages(self):
        _LOGGER.debug('Registering callbacks for Cover device %s',
                      self._address.human)
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
                                    self._open_message_received)
        self._message_callbacks.add(template_on_fast_broadcast,
                                    self._open_message_received)
        self._message_callbacks.add(template_off_broadcast,
                                    self._closed_message_received)
        self._message_callbacks.add(template_off_fast_broadcast,
                                    self._closed_message_received)
        self._message_callbacks.add(template_manual_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_instant_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_off_broadcast,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_on_broadcast,
                                    self._manual_change_received)

    def open(self):
        """Turn the device ON."""
        open_command = StandardSend(self._address,
                                    COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
        self._send_method(open_command, self._open_message_received)

    def open_fast(self):
        """Turn the device ON Fast."""
        open_command = StandardSend(self._address,
                                    COMMAND_LIGHT_ON_FAST_0X12_NONE, cmd2=0xff)
        self._send_method(open_command, self._open_message_received)

    def close(self):
        """Turn the device off."""
        close_command = StandardSend(self._address,
                                     COMMAND_LIGHT_OFF_0X13_0X00)
        self._send_method(close_command, self._closed_message_received)

    def close_fast(self):
        """Turn the device off."""
        close_command = StandardSend(self._address,
                                     COMMAND_LIGHT_OFF_FAST_0X14_0X00)
        self._send_method(close_command, self._closed_message_received)

    def set_position(self, val):
        """Set the devive OPEN LEVEL."""
        if val == 0:
            self.close()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val * 100
            elif val <= 0xff:
                setlevel = val
            set_command = StandardSend(
                self._address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=setlevel)
            self._send_method(set_command, self._open_message_received)

    def set_position_fast(self, val):
        """Set the devive OPEN LEVEL."""
        if val == 0:
            self.close_fast()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val * 100
            elif val <= 0xff:
                setlevel = val
            set_command = StandardSend(
                self._address, COMMAND_LIGHT_ON_FAST_0X12_NONE, cmd2=setlevel)
            self._send_method(set_command, self._open_message_received)

    def _open_message_received(self, msg):
        cmd2 = msg.cmd2 if msg.cmd2 else 255
        self._update_subscribers(cmd2)

    # pylint: disable=unused-argument
    def _closed_message_received(self, msg):
        self._update_subscribers(0x00)

    # pylint: disable=unused-argument
    def _manual_change_received(self, msg):
        self._send_status_request()

    def _send_status_request(self):
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        self._send_method(status_command, self._status_message_received)

    def _status_message_received(self, msg):
        _LOGGER.debug("Cover status message received called")
        self._update_subscribers(msg.cmd2)
