"""INSTEON General Controller Device Class."""
from insteonplm.devices import X10Device
from insteonplm.states.x10 import (X10OnOffSwitch, X10DimmableSwitch,
                                   X10OnOffSensor)


class X10OnOff(X10Device):
    """General X10 On / Off Switch Device Class."""

    def __init__(self, plm, housecode, unitcode):
        super().__init__(plm, housecode, unitcode)
        self._description = 'X10 On / Off Device'

        self._stateList[0x01] = X10OnOffSwitch(
            self._address, "x10OnOffSwitch", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class X10Dimmable(X10Device):
    """General X10 Dimmable Switch Device Class."""

    def __init__(self, plm, housecode, unitcode, dim_steps=22):
        super().__init__(plm, housecode, unitcode)
        self._description = 'X10 Dimmable Device'

        self._stateList[0x01] = X10DimmableSwitch(
            self._address, "x10DimmableSwitch", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class X10Sensor(X10Device):
    """General X10 On / Off Sensor Device Class."""

    def __init__(self, plm, housecode, unitcode, dim_steps=22):
        super().__init__(plm, housecode, unitcode)
        self._description = 'X10 On / Off Sensor Device'

        self._stateList[0x01] = X10OnOffSensor(
            self._address, "x10OnOffSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)
