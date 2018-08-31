"""Test insteonplm Address type."""
from insteonplm.address import Address


def test_textstring():
    """Test Address created from text string."""
    addr = Address('1a2b3c')
    assert addr.human == '1A.2B.3C'
    assert addr.hex == '1a2b3c'
    assert addr.bytes == b'\x1a\x2b\x3c'


def test_bytearray():
    """Test Address created from bytearray."""
    addr_ba = bytearray([0x1a, 0x2b, 0x3c])
    addr = Address(addr_ba)
    assert addr.human == '1A.2B.3C'
    assert addr.hex == '1a2b3c'
    assert addr.bytes == b'\x1a\x2b\x3c'


def test_bytes():
    """Test Address created from bytes string."""
    addr_b = b'\x1a\x2b\x3c'
    addr = Address(addr_b)
    assert addr.human == '1A.2B.3C'
    assert addr.hex == '1a2b3c'
    assert addr.bytes == b'\x1a\x2b\x3c'


def test_none():
    """Test Address equal to None."""
    addr = Address(None)
    assert addr.human == '00.00.00'
    assert addr.hex == '000000'
    assert addr.bytes == b'\x00\x00\x00'


def test_eq():
    """Test Addresses pattern matching."""
    addr1 = Address(None)
    addr2 = Address('1a2b3c')
    addr3 = Address('4d5e6f')

    assert addr1.matches_pattern(addr2)
    assert addr3.matches_pattern(addr1)
    assert not addr2.matches_pattern(addr3)
    assert addr2.matches_pattern(addr2)


def test_x10():
    """Test X10 device address."""
    addr = Address.x10('A', 5)

    assert addr.hex == '000601'
    assert addr.human == 'X10.A.05'
    assert addr.is_x10
    assert addr.x10_housecode == 'A'
    assert addr.x10_unitcode == 5
    assert addr.x10_housecode_byte == 6
    assert addr.x10_unitcode_byte == 1

    addr2 = Address.x10('A', 20)
    assert addr2.human == 'X10.A.20'
