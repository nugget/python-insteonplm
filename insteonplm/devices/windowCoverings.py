"""INSTEON Device Type Window Coverings Control Module."""
from insteonplm.devices import Device
from insteonplm.states.cover import Cover


class WindowCovering(Device):
    """Window Covering Controller.

    INSTEON Window Covering device class. Available device control options are:
        - open()
        - open_fast()
        - set_position(openlevel=0xff)
        - close()
        - close_fast()

    To monitor changes to the state of the device subscribe to the state
    monitor:
         - _states[0x01].connect(callback)  (state='LightOnLevel')

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the WindowCovering Class."""
        Device.__init__(self, plm, address, cat, subcat, product_key,
                        description, model)

        self._stateList[0x01] = Cover(
            self._address, "coverOpenLevel", 0x01, self._send_msg,
            self._message_callbacks, 0x00)
