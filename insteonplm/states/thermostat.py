"""Thermostat states."""
import logging
from insteonplm.constants import (
    COMMAND_EXTENDED_GET_SET_0X2E_0X00,
    # COMMAND_THERMOSTAT_TEMPERATURE_UP_0X68_NONE,
    # COMMAND_THERMOSTAT_TEMPERATURE_DOWN_0X69_NONE,
    COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
    COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04,
    COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05,
    COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06,
    COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07,
    COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08,
    COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09,
    COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02,
    COMMAND_THERMOSTAT_SET_COOL_SETPOINT_0X6C_NONE,
    COMMAND_THERMOSTAT_SET_HEAT_SETPOINT_0X6D_NONE,
    COMMAND_THERMOSTAT_TEMPERATURE_STATUS_0X6E_NONE,
    COMMAND_THERMOSTAT_HUMIDITY_STATUS_0X6F_NONE,
    COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE,
    COMMAND_THERMOSTAT_COOL_SET_POINT_STATUS_0X71_NONE,
    COMMAND_THERMOSTAT_HEAT_SET_POINT_STATUS_0X72_NONE,
    MESSAGE_TYPE_DIRECT_MESSAGE,
    MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
    ThermostatMode)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.userdata import Userdata
from insteonplm.states import State

_LOGGER = logging.getLogger(__name__)


class Temperature(State):
    """A state representing a temperature sensor."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Temperature state."""
        super(Temperature, self).__init__(address, statename, group,
                                          send_message_method,
                                          message_callbacks, defaultvalue)

        self._update_method = self._send_status_request

        self._register_messages()

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x00)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        self._update_subscribers(msg.cmd2 / 2)

    def _temp_received(self, msg):
        self._update_subscribers(msg.cmd2 / 2)

    def _register_messages(self):
        temp_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_TEMPERATURE_STATUS_0X6E_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))

        self._message_callbacks.add(temp_msg, self._temp_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        c_temp = msg.userdata['d10'] | (msg.userdata['d9'] << 8)
        f_temp = c_temp * .1 * 9 / 5 + 32
        self._update_subscribers(f_temp)


class Humidity(State):
    """A state representing a humidity sensor."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(Humidity, self).__init__(
            address, statename, group, send_message_method,
            message_callbacks, defaultvalue)

        self._update_method = self._send_status_request

        self._register_messages()

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x20)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        self._update_subscribers(msg.cmd2)

    def _humidity_received(self, msg):
        self._update_subscribers(msg.cmd2)

    def _register_messages(self):
        humidity_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_HUMIDITY_STATUS_0X6F_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))

        self._message_callbacks.add(humidity_msg, self._humidity_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        humid = msg.userdata['d8']
        self._update_subscribers(humid)


class SystemMode(State):
    """A state representing the thermostat mode."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(SystemMode, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._update_method = self._send_status_request

        self._register_messages()

    def set(self, mode):
        """Set the thermostat mode.

        Mode optons:
            OFF = 0x00,
            HEAT = 0x01,
            COOL = 0x02,
            AUTO = 0x03,
            FAN_AUTO = 0x04,
            FAN_ALWAYS_ON = 0x8
        """
        new_mode = None
        if mode == ThermostatMode.OFF:
            new_mode = COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09
        elif mode == ThermostatMode.HEAT:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04
        elif mode == ThermostatMode.COOL:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05
        elif mode == ThermostatMode.AUTO:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06
        if new_mode:
            msg = ExtendedSend(address=self._address,
                               commandtuple=new_mode,
                               userdata=Userdata())
            msg.set_checksum()
            self._send_method(msg, self._mode_change_ack)

    def _mode_change_ack(self, msg):
        set_mode = msg.cmd2
        mode = None
        if set_mode == 0x04:
            mode = ThermostatMode.HEAT
        elif set_mode == 0x05:
            mode = ThermostatMode.COOL
        elif set_mode in [0x06, 0x0a]:
            mode = ThermostatMode.AUTO
        elif set_mode == 0x09:
            mode = ThermostatMode.OFF
        if mode:
            self._update_subscribers(mode)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        self._update_subscribers(ThermostatMode(msg.cmd2))

    def _ext_status_received(self, msg):
        sysmode = msg.userdata['d6']
        ext_mode = sysmode >> 4
        if ext_mode == 0:
            mode = ThermostatMode.OFF
        elif ext_mode == 1:
            mode = ThermostatMode.AUTO
        elif ext_mode == 2:
            mode = ThermostatMode.HEAT
        elif ext_mode == 3:
            mode = ThermostatMode.COOL
        self._update_subscribers(mode)

    def _register_messages(self):
        mode_status_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))
        mode_change_heat_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_cool_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_auto_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_off_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))

        self._message_callbacks.add(mode_status_msg,
                                    self._status_received)
        self._message_callbacks.add(mode_change_heat_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_cool_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_auto_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_off_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)


class FanMode(State):
    """A state representing the thermostat fan mode."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(FanMode, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._update_method = self._send_status_request

        self._register_messages()

    def set(self, mode):
        """Set the thermostat mode.

        Mode optons:
            OFF = 0x00,
            HEAT = 0x01,
            COOL = 0x02,
            AUTO = 0x03,
            FAN_AUTO = 0x04,
            FAN_ALWAYS_ON = 0x8
        """
        if mode == ThermostatMode.FAN_AUTO:
            new_mode = COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08
        elif mode == ThermostatMode.FAN_ALWAYS_ON:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07
        if new_mode:
            msg = ExtendedSend(address=self._address,
                               commandtuple=new_mode,
                               userdata=Userdata())
            msg.set_checksum()
            self._send_method(msg, self._mode_change_ack)

    def _mode_change_ack(self, msg):
        set_mode = msg.cmd2
        mode = None
        if set_mode == 0x07:
            mode = ThermostatMode.FAN_ALWAYS_ON
        elif set_mode == 0x08:
            mode = ThermostatMode.FAN_AUTO
        elif set_mode == 0x09:
            mode = ThermostatMode.OFF
        elif self.value == ThermostatMode.OFF:
            mode = ThermostatMode.FAN_AUTO
        if mode:
            self._update_subscribers(mode)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        self._update_subscribers(ThermostatMode(msg.cmd2))

    def _ext_status_received(self, msg):
        sysmode = msg.userdata['d6']
        ext_mode = sysmode & 0x0f
        if ext_mode == 0:
            mode = ThermostatMode.FAN_AUTO
        elif ext_mode == 1:
            mode = ThermostatMode.FAN_ALWAYS_ON
        if mode:
            self._update_subscribers(mode)

    def _register_messages(self):
        mode_status_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))
        mode_change_fan_on_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_fan_auto_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_off_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))

        self._message_callbacks.add(mode_status_msg,
                                    self._status_received)
        self._message_callbacks.add(mode_change_fan_on_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_fan_auto_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_off_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)


class CoolSetPoint(State):
    """A state to manage the cool set point."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(CoolSetPoint, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._update_method = self._send_status_request

        self._register_messages()

    def set(self, val):
        """Set the cool set point."""
        msg = ExtendedSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_SET_COOL_SETPOINT_0X6C_NONE,
            cmd2=int(val * 2),
            userdata=Userdata())
        msg.set_checksum()
        self._send_method(msg, self._set_cool_point_ack)

    def _set_cool_point_ack(self, msg):
        self._update_subscribers(msg.cmd2 / 2)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x20)
        self._send_method(msg, self._status_message_received)

    def _status_message_received(self, msg):
        self._update_subscribers(msg.cmd2 / 2)

    def _register_messages(self):
        cool_set_point_status = StandardReceive.template(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_COOL_SET_POINT_STATUS_0X71_NONE,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, False))
        self._message_callbacks.add(cool_set_point_status,
                                    self._status_message_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        cool_sp = msg.userdata['d7'] / 2
        self._update_subscribers(cool_sp)


class HeatSetPoint(State):
    """A state to manage the cool set point."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the HeatSetPoint state."""
        super(HeatSetPoint, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._update_method = self._send_status_request

        self._register_messages()

    def set(self, val):
        """Set the heat set point."""
        msg = ExtendedSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_SET_HEAT_SETPOINT_0X6D_NONE,
            cmd2=int(val * 2),
            userdata=Userdata())
        msg.set_checksum()
        self._send_method(msg, self._set_heat_point_ack)

    def _set_heat_point_ack(self, msg):
        self._update_subscribers(msg.cmd2)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x20)
        self._send_method(msg, self._status_message_received)

    def _status_message_received(self, msg):
        self._update_subscribers(msg.cmd2 / 2)

    def _register_messages(self):
        _LOGGER.debug('Starting HeatSetPoint register_messages')
        heat_set_point_status = StandardReceive.template(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_HEAT_SET_POINT_STATUS_0X72_NONE,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, False))
        self._message_callbacks.add(heat_set_point_status,
                                    self._status_message_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, True),
            userdata=Userdata.template({"d1": 0x01}))
        _LOGGER.debug('Reg Ext Status: %s', ext_status_recd)
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        heat_sp = msg.userdata['d12'] / 2
        self._update_subscribers(heat_sp)
