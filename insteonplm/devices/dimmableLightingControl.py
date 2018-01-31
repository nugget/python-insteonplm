from .devicebase import DeviceBase
from insteonplm.constants import *
from insteonplm.states.dimmable import DimmableSwitch, DimmableSwitch_Fan

class DimmableLightingControl(DeviceBase):
    """Dimmable Lighting Controller 0x01
    
    INSTEON On/Off switch device class. Available device control options are:
        - light_on(onlevel=0xff)
        - light_on_fast(onlevel=0xff)
        - light_off()
        - light_off_fast()

    To monitor changes to the state of the device subscribe to the state monitor:
         - lightOnLevel.connect(callback)  (state='LightOnLevel')

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        DeviceBase.__init__(self, plm, address, cat, subcat, product_key, description, model)

        self._stateList[0x01] = DimmableSwitch(self._address, "lightOnLevel", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)

class DimmableLightingControl_2475F(DimmableLightingControl):
    
    """FanLinc model 2475F Dimmable Lighting Control Device Class 0x01 subcat 0x2e
    
    Two separate INSTEON On/Off switch devices are created with ID
        1) Ligth
            - ID: xxxxxx (where xxxxxx is the Insteon address of the device)
            - Controls: 
                - light_on(onlevel=0xff)
                - light_on_fast(onlevel=0xff)
                - light_off()
                - light_off_fast()
            - Monitor: lightOnLevel.connect(callback)
        2) Fan
            - ID: xxxxxx_2  (where xxxxxx is the Insteon address of the device)
            - Controls: 
                - fan_on(onlevel=0xff)
                - fan_off()
                - light_on(onlevel=0xff)  - Same as fan_on(onlevel=0xff)
                - light_off()  - Same as fan_off()
            - Monitor: fanSpeed.connect(callback)

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._stateList[0x01] = DimmableSwitch(self._address, "lightOnLevel", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)
        self._stateList[0x02] = DimmableSwitch_Fan(self._address, "fanOnLevel", 0x02, self._send_msg, self._plm.message_callbacks, 0x00)