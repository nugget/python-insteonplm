from insteonplm.address import Address

from insteonplm.messages.allLinkCleanupStatusReport import AllLinkCleanupStatusReport
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.allLinkFailureReport import AllLinkFailureReport
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
import binascii

def test_allLinkCleanupStatusReport():
    msg = AllLinkCleanupStatusReport(0x11)
    assert msg.status == 0x11
    assert msg.hex == hexmsg(0x02, 0x58, 0x11)

def test_allLinkComplete():
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
    assert msg.hex == hexmsg(0x02, 0x53, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88)

def test_allLinkFailureReport():
    group = 0x11
    addr = bytearray([0x22,0x33,0x44])
    msg = AllLinkFailureReport(group, addr)

    assert msg.address == Address(addr)
    assert msg.group == group
    assert msg.hex == hexmsg(0x02, 0x56, 0x01, 0x11, 0x22, 0x33, 0x44)

def test_allLinkRecordResponse():
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
    assert msg.hex == hexmsg(0x02, 0x57, flag, group, 0x33, 0x44, 0x55, link1, link2, link3)

def test_buttonEventReport():
    event = 0x03
    msg = ButtonEventReport(event)
    assert msg.event == event
    assert msg.hex == hexmsg(0x02, 0x54, event)

def test_cancelAllLinking():
    msg = CancelAllLinking()
    assert msg.hex == hexmsg(0x02, 0x65)
    assert not msg.isack
    assert not msg.isnak

    msg = CancelAllLinking(0x06)
    assert msg.hex == hexmsg(0x02, 0x65, 0x06)
    assert msg.isack 
    assert not msg.isnak

    msg = CancelAllLinking(0x15)
    assert msg.hex == hexmsg(0x02, 0x65, 0x15)
    assert not msg.isack 
    assert msg.isnak

def test_extendedReceive():
    pass

def test_extendedSend():
    pass

def test_getFirstAllLinkRecord():
    pass

def test_getImConfiguration():
    pass

def test_getIMInfo():
    pass

def test_getNextAllLinkRecord():
    pass

def test_message():
    pass

def test_messageBase():
    pass

def test_messageConstants():
    pass

def test_resetIM():
    pass

def test_sendAlllinkCommand():
    pass

def test_standardReceive():
    pass

def test_standardSend():
    pass

def test_startAllLinking():
    pass

def test_userReset():
    pass

def test_x10received():
    pass

def test_x10send():
    pass

def hexmsg(*arg):
    msg = bytearray([])
    for b in arg:
        if b is None:
            pass
        elif isinstance(b,int):
            msg.append(b)
        elif isinstance(b, Address):
            msg.extend(b.bytes)
            
    return binascii.hexlify(msg).decode()