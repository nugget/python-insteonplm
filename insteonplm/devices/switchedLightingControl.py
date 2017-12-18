from .devicebase import DeviceBase
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *
from .dimmableLightingControl import DimmableLightingControl 

class SwitchedLightingControl(DimmableLightingControl):
    """Switched Lighting Control Device Class 0x02
    
    INSTEON On/Off switch device class. Available device control options are:
        - light_on()
        - light_on_fast()
        - light_off()
        - light_off_fast()
    To monitor the state of the device subscribe to the state monitor:
         - lightOnLevel.connect(callback)
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def light_on(self):
        DimmableLightingControl.light_on(self)

    def light_on_fast (self):
        DimmableLightingControl.light_on_fast (self)

    def light_off(self):
        DimmableLightingControl.light_off(self)

    def light_off_fast(self):
        DimmableLightingControl.light_off_fast(self)

    def light_status_request(self):
        DimmableLightingControl.light_status_request(self)

    def get_operating_flags(self):
        DimmableLightingControl.get_operating_flags(self)

    def set_operating_flags(self):
        DimmableLightingControl.set_operating_flags(self)

    def light_manually_turned_off(self):
        DimmableLightingControl.light_manually_turned_off(self)

    def light_manually_turned_On(self):
        DimmableLightingControl.light_manually_turned_On(self)

class SwitchedLightingControl_2663_222(SwitchedLightingControl):
    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton = 0x01):
        devices = []
        devices.append(SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description, model, 0x01))
        devices.append(SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description, model, 0x02))
        return devices