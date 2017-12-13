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

    @classmethod
    def prod_data_in_aldb(self):
        """True if Product data (cat, subcat, product_key) is stored in the PLM ALDB.
           False if product data must be aquired via a Device ID message or from a Product Data Request command.
           
           Very few devices store their product data in the ALDB, therefore False is the default.
           The common reason to store product data in the ALDB is for one way devices or battery opperated devices where 
           the ability to send a command request is limited.
           
           To override this setting create a device specific class and override this class method."""
        return False

