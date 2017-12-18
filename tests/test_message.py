import unittest
from insteonplm.messages.message import Message
from insteonplm.messages.standardReceive import StandardReceive #50
from insteonplm.messages.extendedReceive import ExtendedReceive #51
from insteonplm.messages.allLinkComplete import AllLinkComplete #53
from insteonplm.messages.buttonEventReport import ButtonEventReport #54
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse #57
from insteonplm.messages.getIMInfo import GetImInfo #60
from insteonplm.messages.standardSend import StandardSend #62
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.address import Address

def test_create_standardReceive_message():
    address1 = 0x11
    address2 = 0x22
    address3 = 0x33
    target1 = 0x44
    target2 = 0x55
    target3 = 0x66
    flags = 0x77
    cmd1 = 0x88
    cmd2 = 0x99
    rawmessage = bytearray([0x02, 0x50, address1, address2, address3, target1, target2, target3, flags, cmd1, cmd2])
    msg  = Message.create(rawmessage)

    assert isinstance(msg, StandardReceive)
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.target == Address(bytearray([target1, target2, target3]))
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2

def test_create_extendedReceive_message():
    address1 = 0x11
    address2 = 0x22
    address3 = 0x33
    target1 = 0x44
    target2 = 0x55
    target3 = 0x66
    flags = 0x77
    cmd1 = 0x88
    cmd2 = 0x99
    rawmessage = bytearray([0x02, 0x51, address1, address2, address3, target1, target2, target3, flags, cmd1, cmd2,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msg  = Message.create(rawmessage)

    assert isinstance(msg , ExtendedReceive)
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.target == Address(bytearray([target1, target2, target3]))
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2

def test_create_allLinkComplete_message():
    linkcode = 0x11
    group = 0x22
    address1 = 0x33
    address2 = 0x44
    address3 = 0x55
    cat = 0x66
    subcat = 0x77
    firmware = 0x88

    rawmessage = bytearray([0x02, 0x53, linkcode, group, address1, address2, address3, cat, subcat, firmware])
    msg  = Message.create(rawmessage)

    assert isinstance(msg , AllLinkComplete)

    assert msg.linkcode == linkcode
    assert msg.group == group
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.category == cat
    assert msg.subcategory == subcat
    assert msg.firmware == firmware

def test_button_event_report():
    event = 0x02
    rawmessage = bytearray([0x02, 0x54, event])
    msg  = Message.create(rawmessage)

    assert isinstance(msg, ButtonEventReport)
    assert msg.event == event
    assert msg.description == 'SET button tapped'

def test_AllLinkRecordResponse_message():
    flags = 0x11
    group = 0x22
    address1 = 0x33
    address2 = 0x44
    address3 = 0x55
    linkdata1 = 0x66
    linkdata2 = 0x77
    linkdata3 = 0x88
    rawmessage = bytearray([0x02, 0x57, flags, group, address1, address2, address3, linkdata1, linkdata2, linkdata3])
    msg  = Message.create(rawmessage)

    assert isinstance(msg, AllLinkRecordResponse)
    assert msg.group == group
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.linkdata1 == linkdata1
    assert msg.linkdata2 == linkdata2
    assert msg.linkdata3 == linkdata3

def test_GetImInfo_message():
    address1 = 0x11
    address2 = 0x22
    address3 = 0x33
    cat = 0x44
    subcat = 0x55
    firmware = 0x66
    acknak = 0x77
    rawmessage = bytearray([0x02, 0x60, address1, address2, address3, cat, subcat, firmware, acknak])
    msg  = Message.create(rawmessage)

    assert isinstance(msg, GetImInfo)
    assert msg.address == Address(bytearray([address1, address2, address3]))
    assert msg.category == cat
    assert msg.subcategory == subcat
    assert msg.firmware == firmware

# This is not a valid test because you cannot receive a StandardSend or a ExtendedSend without an acknak via raw data
#def test_StandardSend_noAcknak_message():
#    target1 = 0x11
#    target2 = 0x22
#    target3 = 0x33
#    flags = 0xEF 
#    cmd1 = 0x55
#    cmd2 = 0x66
#    rawmessage = bytearray([0x02, 0x62, target1, target2, target3, flags, cmd1, cmd2])
#    msg  = Message.create(rawmessage)
#
#
#    assert isinstance(msg, StandardSend)
#    assert msg.cmd1 == cmd1
#    assert msg.cmd2 == cmd2
#    assert msg.isack == False
#    assert msg.isnak == False

def test_StandardSend_withAcknak_message():
    target1 = 0x11
    target2 = 0x22
    target3 = 0x33
    flags = 0xEF # 11101111
    cmd1 = 0x55
    cmd2 = 0x66
    acknak = 0x06
    rawmessage = bytearray([0x02, 0x62, target1, target2, target3, flags, cmd1, cmd2, acknak])
    msg  = Message.create(rawmessage)

    assert isinstance(msg, StandardSend)
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2
    assert msg.isack == True
    assert msg.isnak == False

def test_ExtendedSend_withAcknak_message():
    target1 = 0x11
    target2 = 0x22
    target3 = 0x33
    flags = 0x10 # 00010000
    cmd1 = 0x55
    cmd2 = 0x66
    acknak = 0x06
    rawmessage = bytearray([0x02, 0x62, target1, target2, target3, flags, cmd1, cmd2,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, acknak])
    msg  = Message.create(rawmessage)

    assert isinstance(msg, ExtendedSend)
    assert msg.cmd1 == cmd1
    assert msg.cmd2 == cmd2
    assert msg.isack == True
    assert msg.isnak == False

def test_iscomplete_with_complete_message():
    rawmessage = bytearray([0x02, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    assert Message.iscomplete(rawmessage)
    
def test_iscomplete_with_incomplete_message():
    shortmessage = bytearray([0x02, 0x50, 0x00])
    assert not Message.iscomplete(shortmessage)

def test_incomplete_standard_message():
    rawmessage = bytearray([0x02, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msg = Message.create(rawmessage)
    assert msg is None

def test_incomplete_extended_messge():
    msgext = ExtendedSend(bytearray({0x1a,0x2b,0x3c}), 0x7d, 0x8e, **{'d1':0x9f})
    print(msgext.hex)

    rawmessage = bytearray([0x02, 0x62, 0x1a, 0x2b, 0x3c, 0x10, 0x7d, 0x8e, 0x9f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msg = Message.create(rawmessage)
    assert msg is None
    

    rawmessage.append(0x06)
    msg = Message.create(rawmessage)
    assert isinstance(msg, ExtendedSend)
