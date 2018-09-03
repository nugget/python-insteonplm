"""Test insteonplm.devices.ALDB class."""
from insteonplm.devices import ControlFlags


def test_control_flags():
    """Test ControlFlags class for input and output."""
    in_use = True
    not_in_use = False
    responder = 0
    controller = 1
    used_before = True
    not_used_before = False

    cf = ControlFlags(in_use, controller, used_before, bit5=0, bit4=0)
    assert cf.is_in_use
    assert not cf.is_available
    assert cf.is_controller
    assert not cf.is_responder
    assert cf.is_used_before
    assert not cf.is_high_water_mark
    assert cf.byte == 0xc2

    cf = ControlFlags(not_in_use, responder, not_used_before, bit5=0, bit4=0)
    assert not cf.is_in_use
    assert cf.is_available
    assert not cf.is_controller
    assert cf.is_responder
    assert not cf.is_used_before
    assert cf.is_high_water_mark
    assert cf.byte == 0x00
