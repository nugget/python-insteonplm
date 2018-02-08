import unittest
from insteonplm.address import Address

def test_textstring():
    addr = Address('1a2b3c')
    chk = Address('000000')
    chk.addr = b'\x1a\x2b\x3c'
    print(addr.addr)
    print(chk.addr)
    assert addr == chk
    assert addr.human == '1A.2B.3C'
    assert addr.hex == '1a2b3c'
    assert addr.bytes == b'\x1a\x2b\x3c'

def test_bytearray():
    addr_ba = bytearray([0x1a, 0x2b, 0x3c])
    addr = Address(addr_ba)
    chk = Address('000000')
    chk.addr = b'\x1a\x2b\x3c'
    #assert addr == chk
    assert addr.human == '1A.2B.3C'
    assert addr.hex == '1a2b3c'
    assert addr.bytes == b'\x1a\x2b\x3c'

def test_bytes():
    addr_b = b'\x1a\x2b\x3c'
    addr = Address(addr_b)
    chk = Address('000000')
    chk.addr = b'\x1a\x2b\x3c'
    #assert addr == chk
    assert addr.human == '1A.2B.3C'
    assert addr.hex == '1a2b3c'
    assert addr.bytes == b'\x1a\x2b\x3c'

def test_none():
    addr = Address(None)
    chk = Address('1a2b3c')
    #assert addr == chk
    assert addr.human == '00.00.00'
    assert addr.hex == '000000'
    assert addr.bytes == b'\x00\x00\x00'

def test_eq():
    addr1 = Address(None)
    addr2 = Address('1a2b3c')
    addr3 = Address('4d5e6f')

    assert addr1.matches_pattern(addr2)
    assert addr3.matches_pattern(addr1)
    assert not (addr2.matches_pattern(addr3))
    assert addr2.matches_pattern(addr2)