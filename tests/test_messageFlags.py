from insteonplm.constants import *
from insteonplm.messages.messageFlags import MessageFlags

def test_messageType():
    assert MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE << 5).messageType == MESSAGE_TYPE_DIRECT_MESSAGE
    assert MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE << 5).isDirect

    assert MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE_ACK << 5).messageType == MESSAGE_TYPE_DIRECT_MESSAGE_ACK
    assert MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE_ACK << 5).isDirectACK

    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP << 5).messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP
    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP << 5).isAllLinkCleanup

    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK << 5).messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK
    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK << 5).isAllLinkCleanupACK

    assert MessageFlags(MESSAGE_TYPE_BROADCAST_MESSAGE << 5).messageType == MESSAGE_TYPE_BROADCAST_MESSAGE
    assert MessageFlags(MESSAGE_TYPE_BROADCAST_MESSAGE << 5).isBroadcast

    assert MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE_NAK << 5).messageType == MESSAGE_TYPE_DIRECT_MESSAGE_NAK
    assert MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE_NAK << 5).isDirectNAK

    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_BROADCAST << 5).messageType == MESSAGE_TYPE_ALL_LINK_BROADCAST
    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_BROADCAST << 5).isAllLinkBroadcast

    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK << 5).messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK
    assert MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK << 5).isAllLinkCleanupNAK

def test_extended():
    assert MessageFlags(0x10).extended == 1
    assert MessageFlags(0x10).isExtended

def test_eq():
    flag1 = MessageFlags(0x80)
    flag2 = MessageFlags(0x25)
    flag3 = MessageFlags(0x27)
    flag4 = MessageFlags(0x16)
    flag5 = MessageFlags(0x37)
    flag6 = MessageFlags(0x6f)

    pattern1 = MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, 0)
    pattern2 = MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None)
    pattern3 = MessageFlags.template(None, 0)
    pattern4 = MessageFlags.template(None, 1)
    pattern5 = MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0)
    pattern6 = MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 1)
    pattern7 = MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None)

    assert flag1.matches_pattern(pattern1)
    assert not flag2.matches_pattern(pattern1)
    assert not flag3.matches_pattern(pattern1)
    assert not flag4.matches_pattern(pattern1)
    assert not flag5.matches_pattern(pattern1)
    assert not flag6.matches_pattern(pattern1)

    assert flag1.matches_pattern(pattern2)
    assert not flag2.matches_pattern(pattern2)
    assert not flag3.matches_pattern(pattern2)
    assert not flag4.matches_pattern(pattern2)
    assert not flag5.matches_pattern(pattern2)
    assert not flag6.matches_pattern(pattern2)

    assert flag1.matches_pattern(pattern3)
    assert flag2.matches_pattern(pattern3)
    assert flag3.matches_pattern(pattern3)
    assert not flag4.matches_pattern(pattern3)
    assert not flag5.matches_pattern(pattern3)
    assert flag6.matches_pattern(pattern3)

    assert not flag1.matches_pattern(pattern4)
    assert not flag2.matches_pattern(pattern4)
    assert not flag3.matches_pattern(pattern4)
    assert flag4.matches_pattern(pattern4)
    assert flag5.matches_pattern(pattern4)
    assert not flag6.matches_pattern(pattern4)

    assert not flag1.matches_pattern(pattern5)
    assert flag2.matches_pattern(pattern5)
    assert flag3.matches_pattern(pattern5)
    assert not flag4.matches_pattern(pattern5)
    assert not flag5.matches_pattern(pattern5)
    assert not flag6.matches_pattern(pattern5)

    assert not flag1.matches_pattern(pattern6)
    assert not flag2.matches_pattern(pattern6)
    assert not flag3.matches_pattern(pattern6)
    assert not flag4.matches_pattern(pattern6)
    assert flag5.matches_pattern(pattern6)
    assert not flag6.matches_pattern(pattern6)

    assert not flag1.matches_pattern(pattern7)
    assert flag2.matches_pattern(pattern7)
    assert flag3.matches_pattern(pattern7)
    assert not flag4.matches_pattern(pattern7)
    assert flag5.matches_pattern(pattern7)
    assert not flag6.matches_pattern(pattern7)





 
 

