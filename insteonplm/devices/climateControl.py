"""INSTEON Climate Control Device Class."""
import logging

from insteonplm.devices import Device
from insteonplm.constants import COMMAND_EXTENDED_GET_SET_0X2E_0X00
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.userdata import Userdata
from insteonplm.states.thermostat import (Temperature,
                                          Humidity,
                                          SystemMode,
                                          FanMode,
                                          CoolSetPoint,
                                          HeatSetPoint)
from insteonplm.states.statusReport import StatusReport

_LOGGER = logging.getLogger(__name__)


class ClimateControl_2441th(Device):
    """Thermostat model 2441TH."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the DimmableLightingControl Class."""
        Device.__init__(self, plm, address, cat, subcat, product_key,
                        description, model)

        self._stateList[0x01] = CoolSetPoint(
            self._address, "coolSetPoint", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

        self._stateList[0x02] = HeatSetPoint(
            self._address, "heatSetPoint", 0x02, self._send_msg,
            self._message_callbacks, 0x00)

        self._stateList[0xef] = StatusReport(
            self._address, "statusReport", 0xef, self._send_msg,
            self._message_callbacks, 0x00)

        self._system_mode = SystemMode(
            self._address, "systemMode", 0x10, self._send_msg,
            self._message_callbacks, 0x00)

        self._fan_mode = FanMode(
            self._address, "fanMode", 0x11, self._send_msg,
            self._message_callbacks, 0x00)

        self._temp = Temperature(
            self._address, "temperature", 0x12, self._send_msg,
            self._message_callbacks, 0x00)

        self._humidity = Humidity(
            self._address, "humidity", 0x13, self._send_msg,
            self._message_callbacks, 0x00)

    @property
    def cool_set_point(self):
        """Return the cool set point state."""
        return self._stateList[0x01]

    @property
    def heat_set_point(self):
        """Return the heat set point state."""
        return self._stateList[0x02]

    @property
    def system_mode(self):
        """Return the mode state."""
        return self._system_mode

    @property
    def fan_mode(self):
        """Return the mode state."""
        return self._fan_mode

    @property
    def temperature(self):
        """Return the temperature state."""
        return self._temp

    @property
    def humidity(self):
        """Return the humidity state."""
        return self._humidity

    def async_refresh_state(self):
        """Request each state to provide status update."""
        _LOGGER.debug('Setting up extended status')
        ext_status = ExtendedSend(
            address=self._address,
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata())
        ext_status.set_crc()
        _LOGGER.debug('Sending ext status: %s', ext_status)
        self._send_msg(ext_status)
        _LOGGER.debug('Sending temp status request')
        self.temperature.async_refresh_state()

    # pylint: disable=unused-argument
    def _mode_changed(self, addr, group, val):
        self.async_refresh_state()
