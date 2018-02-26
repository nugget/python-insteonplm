"""Module for classes representing a Security Health and Safety INSTEON device."""

from insteonplm.states.sensor import (VariableSensor, OnOffSensor, SmokeCO2Sensor)
from .devicebase import DeviceBase


class SecurityHealthSafety(DeviceBase):
    """Security Health Safety Control Device Class 0x10

    INSTEON Security Health Safety Control Device Class.
    These are typically binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        """Initialize the SecurityHealthSafety device class."""
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = VariableSensor(self._address, "generalSensor",
                                               0x01, self._send_msg,
                                               self._plm.message_callbacks, 0x00)


class SecurityHealthSafety_2421(DeviceBase):
    """Security Health Safety Control Device model 2421

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        """Initialize the SecurityHealthSafety_2421 device class."""
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(
            self._address, "openClosedSensor", 0x01, self._send_msg,
            self._plm.message_callbacks, 0x00)


class SecurityHealthSafety_2842_222(DeviceBase):
    """Security Health Safety Control Device model 2842-222

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        """Initialize the SecurityHealthSafety_2842_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(self._address, "motionSensor",
                                            0x01, self._send_msg,
                                            self._plm.message_callbacks, 0x00)


class SecurityHealthSafety_2845_222(DeviceBase):
    """Security Health Safety Control Device model 2845-222

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        """Initialize the SecurityHealthSafety_2845_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(self._address, "doorSensor", 0x01,
                                            self._send_msg,
                                            self._plm.message_callbacks, 0x00)


class SecurityHealthSafety_2852_222(DeviceBase):
    """Security Health Safety Control Device model 2852-222

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        """Initialize the SecurityHealthSafety_2852_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(
            self._address, "leakSensor", 0x01, self._send_msg,
            self._plm.message_callbacks, 0x00)


class SecurityHealthSafety_2982_222(DeviceBase):
    """Security Health Safety Control Device model 2982-222

    INSTEON Security Health Safety Control Device Class.
    This device is a variable sensors with the following values:
        0: All clear
        1: Smoke detected
        2: CO2 detected
        3: Test detected
        4: Unknown message detected
        5: All Clear detected
        6: Low Battery
        7: Sensor malfunction
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = SmokeCO2Sensor(self._address, "smokeCO2Sensor",
                                               0x01, self._send_msg,
                                               self._plm.message_callbacks, 0x00)
