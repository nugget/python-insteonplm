"""Test all message classes."""
import binascii

from insteonplm.address import Address
from insteonplm.messages.allLinkCleanupFailureReport import (
    AllLinkCleanupFailureReport)
from insteonplm.messages.allLinkCleanupStatusReport import (
    AllLinkCleanupStatusReport)
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.buttonEventReport import ButtonEventReport
from insteonplm.messages.cancelAllLinking import CancelAllLinking
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from insteonplm.messages.getImConfiguration import GetImConfiguration
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.resetIM import ResetIM
from insteonplm.messages.sendAlllinkCommand import SendAllLinkCommand
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.startAllLinking import StartAllLinking
from insteonplm.messages.userReset import UserReset
from insteonplm.messages.x10received import X10Received
from insteonplm.messages.x10send import X10Send


def test_allLinkCleanupStatusReport():
    """Test AllLinkCleanupStatusReport."""
    msg = AllLinkCleanupStatusReport(0x11)
    assert msg.acknak == 0x11
    assert msg.hex == hexmsg(0x02, 0x58, 0x11)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_allLinkComplete():
    """Test AllLinkComplete."""
    linkcode = 0x11
    group = 0x22
    address = bytearray([0x33, 0x44, 0x55])
    cat = 0x66
    subcat = 0x77
    firmware = 0x88
    msg = AllLinkComplete(linkcode, group, address, cat, subcat, firmware)
    assert msg.address == Address(address)
    assert msg.linkcode == linkcode
    assert msg.group == group
    assert msg.category == cat
    assert msg.subcategory == subcat
    assert msg.hex == hexmsg(0x02, 0x53, 0x11, 0x22, 0x33,
                             0x44, 0x55, 0x66, 0x77, 0x88)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_allLinkFailureReport():
    """Test AllLinkFailureReport."""
    group = 0x11
    addr = bytearray([0x22, 0x33, 0x44])
    msg = AllLinkCleanupFailureReport(group, addr)

    assert msg.address == Address(addr)
    assert msg.group == group
    assert msg.hex == hexmsg(0x02, 0x56, 0x01, 0x11, 0x22, 0x33, 0x44)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_allLinkRecordResponse():
    """Test AllLinkRecordResponse."""
    flag = 0x11
    group = 0x22
    addr = bytearray([0x33, 0x44, 0x55])
    link1 = 0x66
    link2 = 0x77
    link3 = 0x88
    msg = AllLinkRecordResponse(flag, group, addr, link1, link2, link3)
    assert msg.address == Address(addr)
    assert msg.group == group
    assert msg.linkdata1 == link1
    assert msg.linkdata2 == link2
    assert msg.linkdata3 == link3
    assert msg.hex == hexmsg(0x02, 0x57, flag, group, 0x33, 0x44, 0x55,
                             link1, link2, link3)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_buttonEventReport():
    """Test ButtonEventReport."""
    event = 0x03
    msg = ButtonEventReport(event)
    assert msg.event == event
    assert msg.hex == hexmsg(0x02, 0x54, event)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_cancelAllLinking():
    """Test CancelAllLinking."""
    msg = CancelAllLinking()
    assert msg.hex == hexmsg(0x02, 0x65)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = CancelAllLinking(0x06)
    assert msg.hex == hexmsg(0x02, 0x65, 0x06)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = CancelAllLinking(0x15)
    assert msg.hex == hexmsg(0x02, 0x65, 0x15)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_extendedReceive():
    """Test ExtendedReceive."""
    address = bytearray([0x11, 0x22, 0x33])
    target = bytearray([0x44, 0x55, 0x66])
    flags = 0x77
    cmd1 = 0x88
    cmd2 = 0x99
    userdata = {}
    userdatatest = bytearray()

    for i in range(1, 15):
        key = 'd' + str(i)
        userdata.update({key: 0xe0})
        userdatatest.append(0xe0)

    msg = ExtendedReceive(address, target, {'cmd1': cmd1, 'cmd2': cmd2},
                          userdata, flags=flags)
    assert msg.hex == hexmsg(0x02, 0x51, Address(address), Address(target),
                             flags, cmd1, cmd2, userdatatest)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_extendedSend():
    """Test ExtendedSend."""
    address = bytearray([0x11, 0x22, 0x33])
    flags = 0x44 | 0x10
    cmd1 = 0x55
    cmd2 = 0x66
    userdata = {}
    ack = 0x06
    nak = 0x15

    for i in range(1, 15):
        key = 'd' + str(i)
        val = 0xe0 + i
        userdata.update({key: val})

    msg = ExtendedSend(address, {'cmd1': cmd1, 'cmd2': cmd2},
                       userdata, flags=flags)
    assert msg.hex == hexmsg(0x02, 0x62, Address(address),
                             flags | 0x10, cmd1, cmd2, userdata)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = ExtendedSend(address, {'cmd1': cmd1, 'cmd2': cmd2},
                       userdata, flags=flags, acknak=ack)
    assert msg.hex == hexmsg(0x02, 0x62, Address(address),
                             flags | 0x10, cmd1, cmd2, userdata, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = ExtendedSend(address, {'cmd1': cmd1, 'cmd2': cmd2},
                       userdata, flags=flags, acknak=nak)
    assert msg.hex == hexmsg(0x02, 0x62, Address(address),
                             flags | 0x10, cmd1, cmd2, userdata, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_getFirstAllLinkRecord():
    """Test GetFirstAllLinkRecord."""
    ack = 0x06
    nak = 0x15
    msg = GetFirstAllLinkRecord()
    assert msg.hex == hexmsg(0x02, 0x69)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = GetFirstAllLinkRecord(ack)
    assert msg.hex == hexmsg(0x02, 0x69, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = GetFirstAllLinkRecord(nak)
    assert msg.hex == hexmsg(0x02, 0x69, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_getImConfiguration():
    """Test GetImConfiguration."""
    ack = 0x06
    nak = 0x15
    flags = 0x11
    msg = GetImConfiguration()
    assert msg.hex == hexmsg(0x02, 0x73)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = GetImConfiguration(flags, ack)
    assert msg.hex == hexmsg(0x02, 0x73, flags, 0x00, 0x00, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = GetImConfiguration(flags, nak)
    assert msg.hex == hexmsg(0x02, 0x73, flags, 0x00, 0x00, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_getIMInfo():
    """Test GetIMInfo."""
    addr = bytearray([0x11, 0x22, 0x33])
    cat = 0x44
    subcat = 0x55
    firmware = 0x66
    ack = 0x06
    nak = 0x15

    msg = GetImInfo()
    assert msg.hex == hexmsg(0x02, 0x60)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = GetImInfo(addr, cat, subcat, firmware, ack)
    assert msg.hex == hexmsg(0x02, 0x60, addr, cat, subcat, firmware, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = GetImInfo(addr, cat, subcat, firmware, nak)
    assert msg.hex == hexmsg(0x02, 0x60, addr, cat, subcat, firmware, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_getNextAllLinkRecord():
    """Test GetNextAllLinkRecord."""
    ack = 0x06
    nak = 0x15

    msg = GetNextAllLinkRecord()
    assert msg.hex == hexmsg(0x02, 0x6a)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = GetNextAllLinkRecord(ack)
    assert msg.hex == hexmsg(0x02, 0x6a, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = GetNextAllLinkRecord(nak)
    assert msg.hex == hexmsg(0x02, 0x6a, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_resetIM():
    """Test ResetIM."""
    ack = 0x06
    nak = 0x15

    msg = ResetIM()
    assert msg.hex == hexmsg(0x02, 0x67)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = ResetIM(ack)
    assert msg.hex == hexmsg(0x02, 0x67, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = ResetIM(nak)
    assert msg.hex == hexmsg(0x02, 0x67, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_sendAlllinkCommand():
    """Test SendAlllinkCommand."""
    group = 0x11
    cmd1 = 0x22
    cmd2 = 0x33
    ack = 0x06
    nak = 0x15

    msg = SendAllLinkCommand(group, cmd1, cmd2)
    assert msg.hex == hexmsg(0x02, 0x61, group, cmd1, cmd2)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = SendAllLinkCommand(group, cmd1, cmd2, ack)
    assert msg.hex == hexmsg(0x02, 0x61, group, cmd1, cmd2, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = SendAllLinkCommand(group, cmd1, cmd2, nak)
    assert msg.hex == hexmsg(0x02, 0x61, group, cmd1, cmd2, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_standardReceive():
    """Test StandardReceive."""
    address = bytearray([0x11, 0x22, 0x33])
    target = bytearray([0x44, 0x55, 0x66])
    flags = 0x77
    cmd1 = 0x88
    cmd2 = 0x99

    msg = StandardReceive(address, target, {'cmd1': cmd1, 'cmd2': cmd2},
                          flags=flags)
    assert msg.hex == hexmsg(0x02, 0x50, Address(address), Address(target),
                             flags, cmd1, cmd2)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_standardSend():
    """Test StandardSend."""
    address = bytearray([0x11, 0x22, 0x33])
    flags = 0x44
    cmd1 = 0x55
    cmd2 = 0x66
    ack = 0x06
    nak = 0x15

    msg = StandardSend(address, {'cmd1': cmd1, 'cmd2': cmd2}, flags=flags)
    assert msg.hex == hexmsg(0x02, 0x62, Address(address), flags, cmd1, cmd2)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = StandardSend(address, {'cmd1': cmd1, 'cmd2': cmd2},
                       flags=flags, acknak=ack)
    assert msg.hex == hexmsg(0x02, 0x62, Address(address),
                             flags, cmd1, cmd2, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = StandardSend(address, {'cmd1': cmd1, 'cmd2': cmd2},
                       flags=flags, acknak=nak)
    assert msg.hex == hexmsg(0x02, 0x62, Address(address),
                             flags, cmd1, cmd2, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_startAllLinking():
    """Test StartAllLinking."""
    group = 0x11
    code = 0x03
    ack = 0x06
    nak = 0x15

    msg = StartAllLinking(code, group)
    assert msg.hex == hexmsg(0x02, 0x64, code, group)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = StartAllLinking(code, group, ack)
    assert msg.hex == hexmsg(0x02, 0x64, code, group, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = StartAllLinking(code, group, nak)
    assert msg.hex == hexmsg(0x02, 0x64, code, group, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def test_userReset():
    """Test UserReset."""
    msg = UserReset()
    assert msg.hex == hexmsg(0x02, 0x55)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_x10received():
    """Test X10Received."""
    rawX10 = 0x11
    flag = 0x22
    msg = X10Received(rawX10, flag)
    assert msg.hex == hexmsg(0x02, 0x52, rawX10, flag)
    assert len(msg.hex) / 2 == msg.sendSize
    assert len(msg.hex) / 2 == msg.receivedSize


def test_x10send():
    """Test X10Send."""
    rawX10 = 0x11
    flag = 0x22
    ack = 0x06
    nak = 0x15

    msg = X10Send(rawX10, flag)
    assert msg.hex == hexmsg(0x02, 0x63, rawX10, flag)
    assert not msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.sendSize

    msg = X10Send(rawX10, flag, ack)
    assert msg.hex == hexmsg(0x02, 0x63, rawX10, flag, ack)
    assert msg.isack
    assert not msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize

    msg = X10Send(rawX10, flag, nak)
    assert msg.hex == hexmsg(0x02, 0x63, rawX10, flag, nak)
    assert not msg.isack
    assert msg.isnak
    assert len(msg.hex) / 2 == msg.receivedSize


def hexmsg(*arg):
    """Utility method to convert a message to hex."""
    msg = bytearray([])
    for b in arg:
        if b is None:
            pass
        elif isinstance(b, int):
            msg.append(b)
        elif isinstance(b, Address):
            msg.extend(b.bytes)
        elif isinstance(b, bytearray):
            msg.extend(b)
        elif isinstance(b, bytes):
            msg.extend(b)
        elif isinstance(b, dict):
            for i in range(1, 15):
                key = 'd' + str(i)
                val = b[key]
                msg.append(val)

    return binascii.hexlify(msg).decode()
