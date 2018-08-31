"""Test insteonplm User Data type class."""
from insteonplm.messages.userdata import Userdata


def test_userdata_basic():
    """Test insteonplm User Data type class."""
    userdata = {'d1': 0x11, 'd2': 0x22, 'd3': 0x33, 'd4': 0x44, 'd5': 0x55,
                'd6': 0x66, 'd7': 0x77, 'd8': 0x88, 'd9': 0x99, 'd10': 0xaa,
                'd11': 0xbb, 'd12': 0xcc, 'd13': 0xdd, 'd14': 0xee}

    ud = Userdata(userdata)
    chk = Userdata.create_pattern(userdata)
    chk2 = Userdata.create_pattern({'d1': 0x11})
    assert chk == ud
    assert ud.matches_pattern(chk2)
    assert chk2.matches_pattern(ud)
