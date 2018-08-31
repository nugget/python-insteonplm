"""Test message creation."""
# pylint: disable=unused-variable
import insteonplm.messages
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.allLinkRecordResponse import (
    AllLinkRecordResponse)
from insteonplm.messages.buttonEventReport import (
    ButtonEventReport)
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.address import Address


def test_create_standardReceive_message():
    """Test create standardReceive message."""
    address1 = 0x11
    address2 = 0x22
    address3 = 0x33
    target1 = 0x44
    target2 = 0x55
    target3 = 0x66
    flags = 0x77
    cmd1 = 0x88
    cmd2 = 0x99
    rawmessage = bytearray([0x02, 0x50, address1, address2, address3, target1,
                            target2, target3, flags, cmd1, cmd2])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, StandardReceive)
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.target == Address(bytearray([target1, target2, target3]))
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2


def test_create_extendedReceive_message():
    """Test create extendedReceive message."""
    address1 = 0x01
    address2 = 0x02
    address3 = 0x03
    target1 = 0x04
    target2 = 0x05
    target3 = 0x06
    flags = 0x07
    cmd1 = 0x08
    cmd2 = 0x09
    rawmessage = bytearray([0x02, 0x51, address1, address2, address3, target1,
                            target2, target3, flags, cmd1, cmd2,
                            0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
                            0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, ExtendedReceive)
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.target == Address(bytearray([target1, target2, target3]))
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2


def test_create_allLinkComplete_message():
    """Test create allLinkComplete message."""
    linkcode = 0x11
    group = 0x22
    address1 = 0x33
    address2 = 0x44
    address3 = 0x55
    cat = 0x66
    subcat = 0x77
    firmware = 0x88

    rawmessage = bytearray([0x02, 0x53, linkcode, group, address1, address2,
                            address3, cat, subcat, firmware])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, AllLinkComplete)

    assert msg.linkcode == linkcode
    assert msg.group == group
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.category == cat
    assert msg.subcategory == subcat
    assert msg.firmware == firmware


def test_button_event_report():
    """Test button event report."""
    event = 0x02
    rawmessage = bytearray([0x02, 0x54, event])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, ButtonEventReport)
    assert msg.event == event
    assert msg.eventText == 'SET button tapped'


def test_AllLinkRecordResponse_message():
    """Test AllLinkRecordResponse message."""
    flags = 0x11
    group = 0x22
    address1 = 0x33
    address2 = 0x44
    address3 = 0x55
    linkdata1 = 0x66
    linkdata2 = 0x77
    linkdata3 = 0x88
    rawmessage = bytearray([0x02, 0x57, flags, group, address1, address2,
                            address3, linkdata1, linkdata2, linkdata3])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, AllLinkRecordResponse)
    assert msg.group == group
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.linkdata1 == linkdata1
    assert msg.linkdata2 == linkdata2
    assert msg.linkdata3 == linkdata3


def test_GetImInfo_message():
    """Test GetImInfo message."""
    address1 = 0x11
    address2 = 0x22
    address3 = 0x33
    cat = 0x44
    subcat = 0x55
    firmware = 0x66
    acknak = 0x77
    rawmessage = bytearray([0x02, 0x60, address1, address2, address3, cat,
                            subcat, firmware, acknak])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, GetImInfo)
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.category == cat
    assert msg.subcategory == subcat
    assert msg.firmware == firmware


def test_StandardSend_withAcknak_message():
    """Test StandardSend withAcknak message."""
    target1 = 0x11
    target2 = 0x22
    target3 = 0x33
    flags = 0xEF  # 11101111
    cmd1 = 0x55
    cmd2 = 0x66
    acknak = 0x06
    rawmessage = bytearray([0x02, 0x62, target1, target2, target3, flags,
                            cmd1, cmd2, acknak])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, StandardSend)
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2
    assert msg.isack
    assert not msg.isnak


def test_ExtendedSend_withAcknak_message():
    """Test ExtendedSend withAcknak message."""
    target1 = 0x11
    target2 = 0x22
    target3 = 0x33
    flags = 0x10  # 00010000
    cmd1 = 0x55
    cmd2 = 0x66
    acknak = 0x06
    rawmessage = bytearray(
        [0x02, 0x62, target1, target2, target3, flags, cmd1, cmd2,
         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, acknak])
    msg, buffer = insteonplm.messages.create(rawmessage)

    assert isinstance(msg, ExtendedSend)
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2
    assert msg.isack
    assert not msg.isnak


def test_iscomplete_with_complete_message():
    """Test iscomplete with complete message."""
    rawmessage = bytearray([0x02, 0x50, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00])
    assert insteonplm.messages.iscomplete(rawmessage)


def test_iscomplete_with_incomplete_message():
    """Test iscomplete with incomplete message."""
    shortmessage = bytearray([0x02, 0x50, 0x00])
    assert not insteonplm.messages.iscomplete(shortmessage)


def test_incomplete_standard_message():
    """Test incomplete standard message."""
    rawmessage = bytearray([0x02, 0x50, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00])
    msg, buffer = insteonplm.messages.create(rawmessage)
    assert msg is None


def test_incomplete_extended_message():
    """Test incomplete extended message."""
    rawmessage = bytearray([0x02, 0x62, 0x1a, 0x2b, 0x3c, 0x10, 0x7d, 0x8e,
                            0x9f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msg, buffer = insteonplm.messages.create(rawmessage)
    assert msg is None

    rawmessage.append(0x06)
    msg, buffer = insteonplm.messages.create(rawmessage)
    assert isinstance(msg, ExtendedSend)


def test_leading_unknown_messge():
    """Test leading unknown messge."""
    rawmessage = bytearray([0x02, 0x00, 0x15, 0x02, 0x50, 0x46, 0xd0, 0xe6,
                            0x43, 0x6c, 0x15, 0x40, 0x11, 0x01])
    msg, buffer = insteonplm.messages.create(rawmessage)
    assert isinstance(msg, StandardReceive)
    assert msg.cmd1 == 0x11
    assert msg.cmd2 == 0x01
