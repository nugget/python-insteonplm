from .devicebase import DeviceBase
from insteonplm.constants import *
from insteonplm.states.onOff import OnOffSwitch, OnOffSwitch_OutletTop, OnOffSwitch_OutletBottom

class SwitchedLightingControl(DeviceBase):
    def __init__(self, plm, address, cat, subcat, product_key=0x00, description='', model=''):
        super().__init__(plm, address, cat, subcat, product_key, description, model)

        self._stateList[0x01] = OnOffSwitch(self._address, "lightOnOff", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)


class SwitchedLightingControl_2663_222(DeviceBase):
    """On/Off outlet model 2663-222 Switched Lighting Control Device Class 0x02 subcat 0x39
    
    Two separate INSTEON On/Off switch devices are created with ID
        - 'address': Top Outlet
        - 'address_2': Bottom Outlet

    Available device control options are:
        - light_on()
        - light_on_fast()
        - light_off()
        - light_off_fast()
    To monitor the state of the device subscribe to the state monitor:
         - lightOnLevel.connect(callback)
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None):
        super().__init__(plm, address, cat, subcat, product_key, description, model)
        
        self._stateList[0x01] = OnOffSwitch_OutletTop(self._address, "outletTopOnOff", 0x01, self._send_msg, self._plm.message_callbacks, 0x00)
        self._stateList[0x02] = OnOffSwitch_OutletBottom(self._address, "outletBottomOnOff", 0x02, self._send_msg, self._plm.message_callbacks, 0x00)