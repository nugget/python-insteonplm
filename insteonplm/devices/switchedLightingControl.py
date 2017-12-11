from .basedevice import BaseDevice

class SwitchedLightingControl(BaseDevice):
    """Switched Lighting Control 0x02"""
    def LightOn(self):
        return NotImplemented

    def LightOnFast (self):
        return NotImplemented

    def LightOff(self):
        return NotImplemented

    def LightOffFast(self):
        return NotImplemented

    def LightStatusRequest (self):
        return NotImplemented

    def GetOperatingFlags(self):
        return NotImplemented

    def SetOperatingFlags(self):
        return NotImplemented

    def LightManuallyTurnedOff(self):
        return NotImplemented

    def LightManuallyTurnedOn(self):
        return NotImplemented

