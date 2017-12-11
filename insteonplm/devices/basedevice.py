from insteonplm.address import Address
#from .ipdb import IPDB
from insteonplm.messages.messageBase import MessageBase

class BaseDevice(object):
    """INSTEON Device"""

    def __init__(self, plm, address, cat, subcat, firmware, description, model):
        self.plm = plm
        self.address = Address(address)
        self.cat = cat
        self.subcat = subcat
        self.firmware = firmware
        self.description = description
        self.model = model  

    def processMessage(self, message):
        return NotImplemented

    def AssignToALLLinkGroup(self, group):
        return NotImplemented

    def DeleteFromALLLinkGroup(self, group):
        return NotImplemented

    def ProductDataRequest(self):
        return NotImplemented

    def FxUsername(self):
        return NotImplemented

    def DeviceTextStringRequest(self):
        return NotImplemented

    def EnterLinkingMode(self, group):
        return NotImplemented

    def EnterUnlinkingMode(self, group):
        return NotImplemented

    def GetEngineVersion(self):
        return NotImplemented

    def Ping(self):
        return NotImplemented

    def IdRequest(self):
        return NotImplemented

    def ReadALDB(self):
        return NotImplemented

    def WriteALDB(self):
        return NotImplemented

