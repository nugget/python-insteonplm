"""Test insteonplm ALDB Class."""
from insteonplm.address import Address
from insteonplm.aldb import ALDB
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl
from .mockPLM import MockPLM


def test_create_device_from_category():
    """Test device created from cateogory."""
    plm = MockPLM()
    addr = Address('1a2b3c')
    cat = 0x02
    subcat = 0x13

    description = 'Icon SwitchLinc Relay (Lixar)'
    model = '2676R-B'

    aldb = ALDB()
    dev = aldb.create_device_from_category(plm, addr, cat, subcat)

    assert isinstance(dev, SwitchedLightingControl)
    assert dev.cat == cat
    assert dev.subcat == subcat
    assert dev.description == description
    assert dev.model == model


def test_create_device_from_category_generic_device():
    """Test create device from category generic device."""
    plm = MockPLM()
    addr = Address('1a2b3c')
    cat = 0x02
    subcat = 0xff  # needs to be a subcat that is not in the IPDB

    description = 'Generic Switched Lighting Control'
    model = ''

    aldb = ALDB()
    dev = aldb.create_device_from_category(plm, addr, cat, subcat)

    assert isinstance(dev, SwitchedLightingControl)
    assert dev.cat == cat
    assert dev.subcat == subcat
    assert dev.description == description
    assert dev.model == model
