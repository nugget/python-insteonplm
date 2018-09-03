"""INSTEON General Controller Device Class."""
from insteonplm.devices import Device, ALDB, ALDBVersion
from insteonplm.states.dimmable import DimmableRemote


class GeneralController(Device):
    """General Controller Device Class.

    Device cat: 0x00

    Example: ControLinc, RemoteLinc, SignaLinc, etc.
    """

    def __init__(self, plm, address, cat, subcat, product_key=0,
                 description='', model=''):
        """Init the GeneralController class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)
        self._aldb = ALDB(None, None, self._address, version=ALDBVersion.Null)


class GeneralController_2342(Device):
    """INSTEON Device Mini-Remote - 1 Scene."""

    def __init__(self, plm, address, cat, subcat, product_key=0,
                 description='', model=''):
        """Init the GeneralController_2342 class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = DimmableRemote(
            self._address, "remoteButton", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class GeneralController_2342_4(Device):
    """INSTEON Device Mini-Remote - 4 Scene."""

    def __init__(self, plm, address, cat, subcat, product_key=0,
                 description='', model=''):
        """Init the GeneralController_2342_4 class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
        for group in button_list:
            self._stateList[group] = DimmableRemote(
                self._address, "remoteButton{}".format(button_list[group]),
                group, self._send_msg, self._message_callbacks, 0x00)


class GeneralController_2342_8(Device):
    """INSTEON Device Mini-Remote - 8 Scene."""

    def __init__(self, plm, address, cat, subcat, product_key=0,
                 description='', model=''):
        """Init the GeneralController_2342_8 class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {1: 'B', 2: 'A', 3: 'D', 4: 'C',
                       5: 'F', 6: 'E', 7: 'H', 8: 'G'}
        for group in button_list:
            self._stateList[group] = DimmableRemote(
                self._address, "remoteButton{}".format(button_list[group]),
                group, self._send_msg, self._message_callbacks, 0x00)
