from .devicebase import DeviceBase
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *

class SensorsActuators(DeviceBase):
    """Sensors And Actuator Device Class 0x07

     There are 3 known device types in this category:
     1) I/O Linc [2450] & [2450-50-60]
     2) Smartenit IO devices (various input and output channels, see http://sandbox.smartenit.com/downloads/IoTxx_Command_Set.pdf) Including
        a) EZSns1W Sensor Interface Module
        b) EZIO8T I/O Module
        c) EZIO2X4
        d) EZIO8SA / IOT8
        e) EZSnsRF
        f) EZISnsRf
        g) EZIO6I
        h) EZIO4O
    3) SynchroLinc [2423A5] (http://cache.insteon.com/developer/2423A5dev-112010-en.pdf) 

    Each device type is sufficiently different as to require their own device class.
    However, they all seem to have a common element of a relay and a sensor. 
    """
    def __init__(self, plm, address, cat, subcat, product_key = 0, description = '', model = '', groupbutton = 1):
        return super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)

class SensorsActuators_2450(SensorsActuators):
    """I/O Linc [2450] & [2450-50-60] Device Class 0x07 subcat 0x00
        
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

    _status_callback = None

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)

        self.sensor = StateChangeSignal('Sensor', self.sensor_status_request, 0x00)
        self.relay = StateChangeSignal('Relay', self.relay_status_request, 0x00)

        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, self._closed_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_ON_0X11_NONE, self._closed_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_OFF_0X13_0X00, self._open_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_OFF_0X13_0X00, self._open_command_received)
       
    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton = 0x01):
        devices = []
        devices.append(SensorsActuators_2450(plm, address, cat, subcat, product_key, description + ' Relay', model, 0x01))
        devices.append(SensorsActuators_2450(plm, address, cat, subcat, product_key, description + ' Sensor', model, 0x02))
        return devices
    
    def relay_close():
        """Change the relay state to closed."""
        onlevel = 0xff
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_0X11_NONE, onlevel)

    def relay_open():
        """Change the relay state to open."""
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_0X13_0X00)

    def relay_status_request(self):
        """Request status of the device relay."""
        relay_device = self._plm.devices[self._get_device_id(0x01)]
        if self._status_callback is not None:
            # We are waiting for another status request to complete
            self._plm.async_sleep(2)
        self._set_status_callback(relay_device._relay_status_received)
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)

    def sensor_status_request(self):
        """Request status of the device sensor"""
        sensor_device = self._plm.devices[self._get_device_id(0x02)]
        if self._status_callback is not None:
            # We are waiting for another status request to complete
            self._plm.async_sleep(2)
        self._set_status_callback(sensor_device._sensor_status_received)
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01)

    def _closed_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor or Relay closed
        When a message is received any state listeners are updated with the Sensor or Relay state.
        """
        self.log.debug('Starting SensorsActuators_2450._closed_command_received')
        if msg.isbroadcastflag:
            sensor_device = self._plm.devices[self._get_device_id(0x02)]
            sensor_device.sensor.update(self._get_device_id(0x02), 0x00)
        else:
            relay_device = self._plm.devices[self._get_device_id(0x01)]
            relay_device.relay.update(self._get_device_id(0x01), 0x00)
        self.log.debug('Starting SensorsActuators_2450._closed_command_received')

    def _open_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor or Relay open
        When a message is received any state listeners are updated with the Sensor or Relay state.
        """
        self.log.debug('Starting SensorsActuators_2450._open_command_received')
        if msg.isbroadcastflag:
            self.sensor.update(self._get_device_id(0x02), 0x01)
        else:
            self.relay.update(self._get_device_id(0x01), 0xff)
        self.log.debug('Starting SensorsActuators_2450._open_command_received')

    def _sensor_status_received(self, msg):
        sensor_device = self._plm.devices[self._get_device_id(0x02)]
        sensor_device.sensor.update(self._get_device_id(0x02), msg.cmd2)
        self._set_status_callback(None)

    def _relay_status_received(self, msg):
        relay_device = self._plm.devices[self._get_device_id(0x01)]
        relay_device.relay.update(self._get_device_id(0x01), msg.cmd2)
        self._set_status_callback(None)

    def _set_status_callback(self, callback):
        self.log.debug("Setting status callback %s", callback)
        relay_device = self._plm.devices[self._get_device_id(0x01)]
        relay_device._status_callback = callback
        relay_device._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE, relay_device._status_callback, MESSAGE_ACK)

        sensor_device = self._plm.devices[self._get_device_id(0x02)]
        sensor_device._status_callback = callback
        sensor_device._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE, sensor_device._status_callback, MESSAGE_ACK)