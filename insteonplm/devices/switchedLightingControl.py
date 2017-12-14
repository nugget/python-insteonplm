from .basedevice import BaseDevice
from insteonplm.constants import *

class SwitchedLightingControl(BaseDevice):
    """Switched Lighting Control Device Class 0x02"""

    def Light_On(self, onlevel=0xff):
        if onlevel <= 0:
            return ValueError
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_ON, onlevel)

    def Light_On_Fast (self, onlevel=0xff):
        if onlevel <= 0:
            return ValueError
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_FAST, onlevel)

    def Light_Off(self):
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF)

    def Light_Off_Fast(self):
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_FAST)

    def Light_Status_Request (self):
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST)

    def Get_Operating_Flags(self):
        return NotImplemented

    def Set_Operating_Flags(self):
        return NotImplemented

    def Light_Manually_Turned_Off(self):
        return NotImplemented

    def Light_Manually_Turned_On(self):
        return NotImplemented

