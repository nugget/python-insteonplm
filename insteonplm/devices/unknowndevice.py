"""INSTEON Device Unknown Device Type."""
from insteonplm.devices import Device, ALDB, ALDBVersion


class UnknownDevice(Device):
    """Unknown Device Class.

    Unknown Device used when only the device address is known but no other
    information. Available methods:
        id_request()
        product_data_request()
        assign_to_all_link_group()
        delete_from_all_link_group()
        device_text_string_request()
        enter_linking_mode()
        enter_unlinking_mode()
        get_engine_version()
        ping()
        read_aldb()
        write_aldb()
    """

    def __init__(self, plm, address, cat=None, subcat=None, product_key=0x00,
                 description='', model=''):
        """Init the UnknownDevice Class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)
        self._aldb = ALDB(None, None, self._address, version=ALDBVersion.Null)
