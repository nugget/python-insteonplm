"""Test the MessageFlags class."""

from insteonplm.constants import (MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK,
                                  MESSAGE_TYPE_BROADCAST_MESSAGE,
                                  MESSAGE_TYPE_DIRECT_MESSAGE,
                                  MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                  MESSAGE_TYPE_DIRECT_MESSAGE_NAK)
from insteonplm.messages.messageFlags import MessageFlags


def test_messageType():
    """Test message flags match the expected message type."""
    direct = MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE << 5)
    direct_ack = MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE_ACK << 5)
    all_link_cleanup = MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP << 5)
    all_link_cleanup_ack = MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK << 5)
    broadcast = MessageFlags(MESSAGE_TYPE_BROADCAST_MESSAGE << 5)
    direct_nak = MessageFlags(MESSAGE_TYPE_DIRECT_MESSAGE_NAK << 5)
    all_link_broadcast = MessageFlags(MESSAGE_TYPE_ALL_LINK_BROADCAST << 5)
    all_link_cleanup_nak = MessageFlags(MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK << 5)

    assert direct.messageType == MESSAGE_TYPE_DIRECT_MESSAGE
    assert direct.isDirect

    assert direct_ack.messageType == MESSAGE_TYPE_DIRECT_MESSAGE_ACK
    assert direct_ack.isDirectACK

    assert all_link_cleanup.messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP
    assert all_link_cleanup.isAllLinkCleanup

    assert (all_link_cleanup_ack.messageType ==
            MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK)
    assert all_link_cleanup_ack.isAllLinkCleanupACK

    assert broadcast.messageType == MESSAGE_TYPE_BROADCAST_MESSAGE
    assert broadcast.isBroadcast

    assert direct_nak.messageType == MESSAGE_TYPE_DIRECT_MESSAGE_NAK
    assert direct_nak.isDirectNAK

    assert all_link_broadcast.messageType == MESSAGE_TYPE_ALL_LINK_BROADCAST
    assert all_link_broadcast.isAllLinkBroadcast

    assert (all_link_cleanup_nak.messageType ==
            MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK)
    assert all_link_cleanup_nak.isAllLinkCleanupNAK


def test_extended():
    """Test the extended flag."""
    assert MessageFlags(0x10).extended == 1
    assert MessageFlags(0x10).isExtended


# pylint: disable=too-many-statements
def test_eq():
    """Test comarision for equality."""
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
