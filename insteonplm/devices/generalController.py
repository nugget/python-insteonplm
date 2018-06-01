"""INSTEON General Controller Device Class."""
from insteonplm.devices import Device, ALDB, ALDBVersion


class GeneralController(Device):
    """General Controller Device Class.

    Device cat: 0x00

    Example: ControLinc, RemoteLinc, SignaLinc, etc.
    """

    def __init__(self, plm, address, cat, subcat, product_key=0,
                 description='', model=''):
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)
        self._aldb = ALDB(None, None, self._address, version=ALDBVersion.Null)
