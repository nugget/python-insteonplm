from .ipdb import IPDB
from insteonplm.address import Address
from .dimmableLightingControl import DimmableLightingControl
from .generalController import GeneralController
from .switchedLightingControl import SwitchedLightingControl

class Device(object):
    """Receive device infomration and return a device class to control the device."""
    

    @classmethod
    def create(cls, plm, address, cat, subcat, firmware=None):
        ipdb = IPDB()
        product = ipdb[[cat, subcat]]
        print(product)
        deviceclass = product[5]
        print(deviceclass)
        return deviceclass(plm, address, cat, subcat, product[2], product[3], product[4])

