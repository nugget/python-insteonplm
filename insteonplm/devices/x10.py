"""INSTEON General Controller Device Class."""
from insteonplm.devices import X10Device
from insteonplm.states.x10 import X10OnOffSwitch

class X10OnOff(X10Device):
    """General Controller Device Class.

    Device cat: 0x00

    Example: ControLinc, RemoteLinc, SignaLinc, etc.
    """
 
    def __init__(self, plm, housecode, unitcode):
        super().__init__(plm, housecode, unitcode)
        print('1. Is X10 address:', self._address.is_x10)

        self._description = 'X10 On / Off Device'

        self._stateList[0x01] = X10OnOffSwitch(
            self._address, "OnOffSwitch", 0x01, self._send_msg,
            self._message_callbacks, 0x00)