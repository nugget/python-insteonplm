from .devicebase import DeviceBase
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *

class SecurityHealthSafety(DeviceBase):
    """Security Health Safety Control Device Class 0x10
    
    INSTEON Security Health Safety Control Device Class. 
    These are typically binary sensors with On/Off status.
    There are no state change commands that can be sent to the device.
    
    To monitor the state of the device subscribe to the state monitor:
         - sensor.connect(callback)  (state='Sensor')
         kk
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """
    

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)

        # Binary sensors are assumed to be readonly therefore no update method is necessary
        # Assuming the default for the sensor is 0
        self.sensor = StateChangeSignal('Sensor', None, 0x00)

        # Tell PLM not to just use the ALDB record for device info
        # This is likely the case for all devices in this category 
        self._product_data_in_aldb = True

        self._message_callbacks.add(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, self._sensor_on_command_received)
        self._message_callbacks.add(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_ON_0X11_NONE, self._sensor_on_command_received)
        self._message_callbacks.add(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_OFF_0X13_0X00, self._sensor_off_command_received)
        self._message_callbacks.add(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_OFF_0X13_0X00, self._sensor_off_command_received)
        # Motion Sensor 2842-222 sends cmd1:0x13 cmd2: 0x01 for an off command. Not sure about other devices in this devcat.
        self._message_callbacks.add(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, {'cmd1':0x13, 'cmd2':0x01}, self._sensor_off_command_received)
        self._message_callbacks.add(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, {'cmd1':0x13, 'cmd2':0x01}, self._sensor_off_command_received)


    def _sensor_on_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor On
        When a message is received any state listeners are updated with the 
        return 0x01 for on
        """
        self.log.debug('Starting SecurityHealthSafety._sensor_on_command_received')
        self.sensor.update(self.id, msg.cmd2)
        self.log.debug('Starting SecurityHealthSafety._sensor_on_command_received')

    def _sensor_off_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x13 Sensor Off
        When a message is received any state listeners are updated with the 
        return 0x00 for off
        """
        self.sensor.update(self.id, 0x00)
            
class SecurityHealthSafety_2982_222(SecurityHealthSafety):
    
    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)
        
        self._message_callbacks.add(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, self._sensor_state_received)
        self._message_callbacks.add(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_ON_0X11_NONE, self._sensor_state_received)

    def _sensor_state_received(self, msg):
        self.log.debug('Starting SecurityHealthSafety_2982_222._sensor_on_command_received')
        if msg.isbroadcastflag:
            self.sensor.update(self.id, msg.targetHi)
        self.log.debug('Ending SecurityHealthSafety_2982_222._sensor_on_command_received')