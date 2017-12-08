from insteonplm.address import Address
from .ipdb import IPDB
from insteonplm.messages.messagebase import MessageBase

class insteonDevice(object):
    """INSTEON Device"""
    ipdb = IPDB()

    def __init__(self, address, cat, subcat, firmware):
        self.address = Address(address)
        self.product = self.ipdb[cat, subcat]

    def processMessage(self, message):
        return NotImplemented