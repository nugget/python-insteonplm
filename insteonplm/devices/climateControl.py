"""INSTEON Climate Control Device Class."""
from insteonplm.devices import Device
from insteonplm.constants import ThermostatMode
from insteonplm.states.thermostat import (Temperature,
                                          Humidity,
                                          Mode,
                                          CoolSetPoint,
                                          HeatSetPoint)


class ClimateControl_2441th(Device):
    """Thermostat model 2441TH."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the DimmableLightingControl Class."""
        Device.__init__(self, plm, address, cat, subcat, product_key,
                        description, model)

        self._stateList[0x01] = CoolSetPoint(
            self._address, "coolSetPoint", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

        self._stateList[0x02] = HeatSetPoint(
            self._address, "heatSetPoint", 0x02, self._send_msg,
            self._message_callbacks, 0x00)

        self._mode = Mode(
            self._address, "mode", 0x10, self._send_msg,
            self._message_callbacks, 0x00)

        self._temp = Temperature(
            self._address, "temperature", 0x11, self._send_msg,
            self._message_callbacks, 0x00)

        self._humidity = Humidity(
            self._address, "humidity", 0x12, self._send_msg,
            self._message_callbacks, 0x00)

    def async_refresh_state(self):
        """Request each state to provide status update."""
        # Get mode  0x6b 0x02 mode.async_refresh_state()
        # Get set point 0x6a 0x20
        # Get temp 0x6a 0x00
        # Get humidity 0x6a 0x60
        # Get Ambient temp 0x6b 0x03 (not implemented)
        # When the mode changes do it again
        # Mode must be received before other can continue
        self._mode.async_refresh_state()
        if self._mode.value == ThermostatMode.COOL:
            self._states[0x01].async_refresh_state()
        elif self._mode.vale in [ThermostatMode.HEAT,
                                 ThermostatMode.AUTO]:
            self._states[0x02].async_refresh_state()
        self._temp.async_refresh_state()
        self._humidity.async_refresh_state()


    def _mode_changed(self, addr, group, val):
        self.async_refresh_state()
