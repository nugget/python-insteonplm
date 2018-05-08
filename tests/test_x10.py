"""Test insteonplm X10 devices."""

from insteonplm.devices.x10 import X10OnOff
from .mockPLM import MockPLM

def test_x10OnOff():
    housecode = 'C'
    unitcode = 9
    plm = MockPLM()
    device = X10OnOff(plm, housecode, unitcode)
    assert device.address.human == 'X10.{}.{:02d}'.format(housecode, unitcode)

    device.states[0x01].on()
    print(plm.sentmessage)