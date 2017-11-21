from .address import Address
from .ipdb import IPDB

class insteonDevice(object):
    """INSTEON Device"""
    ipdb = IPDB()

    def __init__(self, address, cat, subcat, firmware)
        self.address = Address(address)
        self.product = self.ipdb[cat, subcat]

