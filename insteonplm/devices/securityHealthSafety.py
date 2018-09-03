"""INSTEON Security Health and Safety Device Class Module."""

from insteonplm.states.sensor import (VariableSensor,
                                      OnOffSensor,
                                      SmokeCO2Sensor,
                                      LeakSensorDryWet,
                                      LeakSensorHeartbeat,
                                      LeakSensorState)
from insteonplm.devices import Device


class SecurityHealthSafety(Device):
    """Security Health Safety Control Device Class.

    Device cat: 0x10 subcat: Any

    INSTEON Security Health Safety Control Device Class.
    These are typically binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SecurityHealthSafety device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = VariableSensor(
            self._address, "generalSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class SecurityHealthSafety_2421(Device):
    """Security Health Safety Control Device Class.

    TriggerLinc model 2421.
    Device cat: 0x10 subcat: 0x02.

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SecurityHealthSafety_2421 device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(
            self._address, "openClosedSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class SecurityHealthSafety_2842_222(Device):
    """Security Health Safety Control Device Class.

    Moton Sensor model 2842-222.
    Device cat: 0x10 subcat: 0x01.

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SecurityHealthSafety_2842_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(
            self._address, "motionSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

        self._stateList[0x02] = OnOffSensor(
            self._address, "lightSensor", 0x02, self._send_msg,
            self._message_callbacks, 0x00)

        self._stateList[0x03] = OnOffSensor(
            self._address, "batterySensor", 0x03, self._send_msg,
            self._message_callbacks, 0x00)


class SecurityHealthSafety_2845_222(Device):
    """Security Health Safety Control Device Class.

    Hidden Door Sensor model 2845-222.
    Device cat: 0x10 subcat: 0x11.

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SecurityHealthSafety_2845_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = OnOffSensor(
            self._address, "doorSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class SecurityHealthSafety_2852_222(Device):
    """Security Health Safety Control Device Class.

    Water Leak Sensor model 2852-222.
    Device cat: 0x10 subcat: 0x08.

    INSTEON Security Health Safety Control Device Class.
    This device is a binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.

    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SecurityHealthSafety_2852_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = LeakSensorDryWet(
            self._address, "dryLeakSensor", 0x01, self._send_msg,
            self._message_callbacks,
            defaultvalue=0x01,
            dry_wet=LeakSensorState.DRY)
        self._stateList[0x02] = LeakSensorDryWet(
            self._address, "wetLeakSensor", 0x02, self._send_msg,
            self._message_callbacks,
            defaultvalue=0x00,
            dry_wet=LeakSensorState.WET)
        self._stateList[0x04] = LeakSensorHeartbeat(
            self._address, "heartbeatLeakSensor", 0x04, self._send_msg,
            self._message_callbacks,
            defaultvalue=0x11)

        self._stateList[0x01].register_dry_wet_callback(
            self._stateList[0x02].set_value)
        self._stateList[0x01].register_dry_wet_callback(
            self._stateList[0x04].set_value)

        self._stateList[0x02].register_dry_wet_callback(
            self._stateList[0x01].set_value)
        self._stateList[0x02].register_dry_wet_callback(
            self._stateList[0x04].set_value)

        self._stateList[0x04].register_dry_wet_callback(
            self._stateList[0x01].set_value)
        self._stateList[0x04].register_dry_wet_callback(
            self._stateList[0x02].set_value)


class SecurityHealthSafety_2982_222(Device):
    """Security Health Safety Control Device Class.

    Smoke Bridge model 2982-222
    Device cat: 0x10 subcat: 0x0a

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

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SecurityHealthSafety_2982_222 Class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._product_data_in_aldb = True

        self._stateList[0x01] = SmokeCO2Sensor(
            self._address, "smokeCO2Sensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)
