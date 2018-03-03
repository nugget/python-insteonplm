"""Test insteonplm.evices module."""
import insteonplm.devices
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl
from .mockPLM import MockPLM


def test_create_device():
    """Test create device."""
    plm = MockPLM()
    device = insteonplm.devices.create(plm, '112233', 0x01, 0x0d, None)
    assert device.id == '112233'
    assert isinstance(device, DimmableLightingControl)


def test_create_device_from_bytearray():
    """Test create device from byte array."""
    plm = MockPLM()
    target = bytearray()
    target.append(0x01)
    target.append(0x0d)
    device = insteonplm.devices.create(plm, '112233',
                                       target[0], target[1],
                                       None)
    assert device.id == '112233'
    assert isinstance(device, DimmableLightingControl)
