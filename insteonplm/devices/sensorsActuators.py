"""INSTEON Sensors Actuators Device Class Module."""
from insteonplm.devices import Device
from insteonplm.states.onOff import OpenClosedRelay
from insteonplm.states.sensor import IoLincSensor


class SensorsActuators(Device):
    """Sensors And Actuator Device Class.

    Device cat: 0x07 subcat: Any

    There are 3 known device types in this category:
        1) I/O Linc [2450] & [2450-50-60]
        2) Smartenit IO devices (various input and output channels,
        see http://sandbox.smartenit.com/downloads/IoTxx_Command_Set.pdf)
        Including
            a) EZSns1W Sensor Interface Module
            b) EZIO8T I/O Module
            c) EZIO2X4
            d) EZIO8SA / IOT8
            e) EZSnsRF
            f) EZISnsRf
            g) EZIO6I
            h) EZIO4O
        3) SynchroLinc [2423A5]
        (http://cache.insteon.com/developer/2423A5dev-112010-en.pdf)

    Each device type is sufficiently different as to require their own device
    class. However, they all seem to have a common element of a relay and a
    sensor.
    """

    def __init__(self, plm, address, cat, subcat, product_key=0,
                 description='', model=''):
        """Init the SensorsActuators Class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = OpenClosedRelay(
            self._address, "openClosedRelay", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class SensorsActuators_2450(SensorsActuators):
    """I/O Linc [2450] & [2450-50-60] Device Class.

    I/O Linc model 2450 and 2450-50-60.
    Device cat: 0x07 subcat: 0x00

    Two separate INSTEON devices are created
        1) Relay
            - ID: xxxxxx (where xxxxxx is the Insteon address of the device)
            - Controls:
                - relay_close()
                - relay_open()
            - Monitor: relay.connect(callback)
                - Closed: 0x00
                - Open:   0xff
        2) Sensor
            - ID: xxxxxx_2  (where xxxxxx is the Insteon address of the device)
            - Controls: None
            - Monitor: sensor.connect(callback)
               - Closed: 0x00
               - Open:   0x01

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SensorsActuators_2450 Class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = OpenClosedRelay(
            self._address, "openClosedRelay", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

        # Both the Relay and the Sensor are linked via group 1.
        # The sensor status updates are sent as group 1 updates.
        # The relay status is not relevent.
        self._stateList[0x02] = IoLincSensor(
            self._address, "ioLincSensor", 0x02, self._send_msg,
            self._message_callbacks, 0x00)
