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
    flag2 = MessageFlags.create(MESSAGE_TYPE_BROADCAST_MESSAGE, 0)

    assert flag1 == flag2




 
 

