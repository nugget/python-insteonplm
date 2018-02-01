from .devicebase import DeviceBase
from insteonplm.constants import *
from insteonplm.states.sensor import VariableSensor, MotionSensor, SmokeCO2Sensor

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
        super().__init__(plm, address, cat, subcat, product_key, description, model)
        
        self._stateList[0x01] = VariableSensor(self._address, "onOffSensor", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)

class SecurityHealthSafety_2842_222(DeviceBase):
    
    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._product_data_in_aldb = True
        
        self._stateList[0x01] = MotionSensor(self._address, "motionSensor", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)
            
class SecurityHealthSafety_2982_222(DeviceBase):
    
    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        super().__init__(plm, address, cat, subcat, product_key, description, model)
        
        self._stateList[0x01] = SmokeCO2Sensor(self._address, "smokeCO2Sensor", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)