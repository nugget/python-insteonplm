from .basedevice import BaseDevice
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *

class SwitchedLightingControl(BaseDevice):
    """Switched Lighting Control Device Class 0x02"""

    def __init__(selfplm, address, cat, subcat, firmware=None, description=None, model=None):
        BaseDevice.__init__(self, plm, address, cat, subcat, firmware, description, model)
        self.lightOnLevel = StateChangeSignal()
        self.register_command_handler(COMMAND_LIGHT_ON, self._light_on_command_received)

    def light_on(self, onlevel=0xff):
        if onlevel <= 0:
            return ValueError
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_ON, onlevel)

    def light_on_fast (self, onlevel=0xff):
        if onlevel <= 0:
            return ValueError
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_FAST, onlevel)

    def light_off(self):
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF)

    def light_off_Fast(self):
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_FAST)

    def light_status_request (self):
        self.plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST)

    def get_operating_flags(self):
        return NotImplemented

    def set_operating_flags(self):
        return NotImplemented

    def light_manually_turned_off(self):
        return NotImplemented

    def light_manually_turned_On(self):
        return NotImplemented

    def _light_on_command_recieved(msg):
        self.lightOnLevel.update(msg.address.hex, msg.cmd2)
