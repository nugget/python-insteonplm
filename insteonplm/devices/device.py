import logging

from .ipdb import IPDB
from insteonplm.address import Address
from .dimmableLightingControl import DimmableLightingControl
from .generalController import GeneralController
from .switchedLightingControl import SwitchedLightingControl

class Device(object):
    """Receive device infomration and return a device class to control the device."""
    

    @classmethod
    def create(cls, plm, address, cat, subcat, firmware=None):
        log = logging.getLogger(__name__)

        ipdb = IPDB()
        product = ipdb[[cat, subcat]]
        deviceclass = product[5]
        log.debug('Device cat: %x  subcat: %x returns deviceclass: %s', cat, subcat, deviceclass)
        if deviceclass is not None:
            return deviceclass.create(plm, address, cat, subcat, product[2], product[3], product[4])
        else:
            return None

