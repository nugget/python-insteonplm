import insteonplm
from insteonplm.address import Address
from insteonplm.aldb import ALDB
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl

def test_get_device_from_categories():
    addr = Address('1a2b3c')
    cat = 0x02
    subcat = 0x13

    description = 'Icon SwitchLinc Relay (Lixar)'
    model = '2676R-B'
    deviceclass = SwitchedLightingControl

    aldb = ALDB()
    dev = aldb.get_device_from_categories(None, addr, cat, subcat)

    assert isinstance(dev, SwitchedLightingControl)
    assert dev.cat == cat
    assert dev.subcat == subcat
    assert dev.description == description
    assert dev.model == model

def test_get_device_from_categories_generic_device():
    addr = Address('1a2b3c')
    cat = 0x02
    subcat = 0xff # needs to be a subcat that is not in the IPDB
        
    description = 'Generic Switched Lighting'
    model = ''
    deviceclass = SwitchedLightingControl

    aldb = ALDB()
    dev = aldb.get_device_from_categories(None, addr, cat, subcat)

    assert isinstance(dev, SwitchedLightingControl)
    assert dev.cat == cat
    assert dev.subcat == subcat
    assert dev.description == description
    assert dev.model == model