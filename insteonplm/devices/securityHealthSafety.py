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

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """
    

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        DeviceBase.__init__(self, plm, address, cat, subcat, product_key, description, model, groupbutton)

        self.sensor = StateChangeSignal()
        self.sensor._stateName = 'Sensor'

        # Tell PLM not to just use the ALDB record for device info
        # This is likely the case for all devices in this category 
        if self._subcat == 0x01:  
            self._product_data_in_aldb = True

        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, self._sensor_on_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_ON_0X11_NONE, self._sensor_on_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_OFF_0X13_0X00, self._sensor_off_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51, COMMAND_LIGHT_OFF_0X13_0X00, self._sensor_off_command_received)


    def _sensor_on_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor On
        When a message is received any state listeners are updated with the 
        return 0x01 for on
        """
        self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, 0x01)

    def _sensor_offcommand_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x13 Sensor Off
        When a message is received any state listeners are updated with the 
        return 0x00 for off
        """
        self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, 0x00)
            
