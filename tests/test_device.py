from insteonplm.devices.device import Device
from insteonplm.devices.generalController import GeneralController
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl

def test_create_device():
    device = Device.create(None, '112233', 0x01, 0x0d, None)
    print(device.id)
    assert device.id == '112233'
    assert isinstance(device, DimmableLightingControl)