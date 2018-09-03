"""Test message callbacks."""

import logging
from insteonplm.messagecallback import MessageCallback
from insteonplm.constants import (COMMAND_LIGHT_ON_0X11_NONE,
                                  MESSAGE_ACK,
                                  MESSAGE_NAK)
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.userdata import Userdata
from .mockCallbacks import MockCallbacks


_LOGGER = logging.getLogger(__name__)


def test_messagecallback_basic():
    """Test messagecallback basic."""
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"

    msg_template = StandardReceive.template(
        commandtuple=COMMAND_LIGHT_ON_0X11_NONE, flags=0x80)
    callbacks[msg_template] = callbacktest1

    msg = StandardReceive('1a2b3c', '4d5e6f', COMMAND_LIGHT_ON_0X11_NONE,
                          cmd2=0xff, flags=0x80)

    callback1 = callbacks.get_callbacks_from_message(msg)

    assert len(callback1) == 1
    assert callback1[0] == callbacktest1


def test_messagecallback_msg():
    """Test messagecallback msg."""
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    template_on = StandardReceive.template(
        commandtuple=COMMAND_LIGHT_ON_0X11_NONE)
    callbacks.add(template_on, callbacktest)
    msg1 = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE,
                           cmd2=0x00)
    msg2 = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE,
                           cmd2=0xff)

    callback1 = callbacks.get_callbacks_from_message(msg1)
    callback2 = callbacks.get_callbacks_from_message(msg2)

    assert callback1[0] == callbacktest
    assert callback2[0] == callbacktest


# pylint: disable=too-many-locals
def test_messagecallback_acknak():
    """Test messagecallback acknak."""
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"
    callbacktest3 = "test callback 3"
    callbacktest4 = "test callback 4"
    address = '1a2b3c'

    template_address = StandardSend.template(address=address)
    template_address_ack = StandardSend.template(address=address,
                                                 acknak=MESSAGE_ACK)
    template_empty = StandardSend.template()
    template_nak = StandardSend.template(acknak=MESSAGE_NAK)
    callbacks.add(template_address, callbacktest1)
    callbacks.add(template_address_ack, callbacktest2)
    callbacks.add(template_empty, callbacktest3)
    callbacks.add(template_nak, callbacktest4)

    msg1 = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xcd)
    msg2 = StandardSend('222222', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
    msg3 = StandardSend('333333', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff,
                        acknak=MESSAGE_NAK)
    msg4 = StandardSend('444444', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff,
                        acknak=MESSAGE_ACK)

    _LOGGER.debug('Getting callbacks for message 1')
    callback1 = callbacks.get_callbacks_from_message(msg1)
    _LOGGER.debug('Getting callbacks for message 2')
    callback2 = callbacks.get_callbacks_from_message(msg2)
    _LOGGER.debug('Getting callbacks for message 3')
    callback3 = callbacks.get_callbacks_from_message(msg3)
    _LOGGER.debug('Getting callbacks for message 4')
    callback4 = callbacks.get_callbacks_from_message(msg4)

    assert len(callback1) == 4
    assert len(callback2) == 2
    assert len(callback3) == 2
    assert len(callback4) == 1


def test_message_callback_extended():
    """Test message callback extended."""
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    template_ext_on = ExtendedReceive.template(
        commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
        userdata=Userdata({'d1': 0x02}))
    callbacks.add(template_ext_on, callbacktest)
    msg1 = ExtendedReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE,
                           Userdata({'d1': 0x02}), cmd2=0xff)
    msg2 = ExtendedReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE,
                           Userdata({'d1': 0x03, 'd2': 0x02}), cmd2=0xff)

    callback1 = callbacks.get_callbacks_from_message(msg1)
    callback2 = callbacks.get_callbacks_from_message(msg2)

    assert callback1[0] == callbacktest
    assert not callback2


def test_delete_callback():
    """Test delete callback."""
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"
    callbacktest3 = "test callback 3"

    callbacks.add(StandardSend.template(), callbacktest1)
    callbacks.add(StandardSend.template(), callbacktest2)
    callbacks.add(StandardSend.template(acknak=MESSAGE_NAK), callbacktest3)

    msg = StandardSend('333333', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff,
                       acknak=MESSAGE_NAK)

    callback_list = callbacks.get_callbacks_from_message(msg)
    assert len(callback_list) == 3

    callbacks.remove(StandardSend.template(), callbacktest2)
    callback_list = callbacks.get_callbacks_from_message(msg)
    assert len(callback_list) == 2


def test_misc_messages():
    """Test misc messages."""
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"
    callbacktest3 = "test callback 3"

    msgtemplate1 = AllLinkRecordResponse(None, None, None, None, None, None)
    msgtemplate2 = GetImInfo()
    msgtemplate3 = GetNextAllLinkRecord(acknak=MESSAGE_NAK)
    callbacks.add(msgtemplate1, callbacktest1)
    callbacks.add(msgtemplate2, callbacktest2)
    callbacks.add(msgtemplate3, callbacktest3)

    msg1 = AllLinkRecordResponse(0x00, 0x01, '1a2b3c', 0x01, 0x02, 0x03)
    msg2 = GetImInfo()
    msg3 = GetNextAllLinkRecord(acknak=MESSAGE_ACK)
    msg4 = GetNextAllLinkRecord(acknak=MESSAGE_NAK)

    callback_list1 = callbacks.get_callbacks_from_message(msg1)
    callback_list2 = callbacks.get_callbacks_from_message(msg2)
    callback_list3 = callbacks.get_callbacks_from_message(msg3)
    callback_list4 = callbacks.get_callbacks_from_message(msg4)

    assert callback_list1[0] == callbacktest1
    assert callback_list2[0] == callbacktest2
    assert not callback_list3
    assert callback_list4[0] == callbacktest3


def test_extended_ack():
    """Test extended ack."""
    callbacks = MockCallbacks()
    callbacks.callbackvalue1 = "Callback 1"
    callbacks.callbackvalue2 = "Callback 2"
    message_callbacks = MessageCallback()
    address = '1a2b3c'

    template_ext_ack = ExtendedSend.template(address, acknak=MESSAGE_ACK)
    template_std_ack = StandardSend.template(address, acknak=MESSAGE_ACK)

    message_callbacks.add(template_ext_ack, callbacks.callbackvalue1)
    message_callbacks.add(template_std_ack, callbacks.callbackvalue2)
    extmsg = ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE, {'d1': 0x02},
                          cmd2=0xff, acknak=MESSAGE_ACK)
    stdmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff,
                          acknak=MESSAGE_ACK)
    result1 = message_callbacks.get_callbacks_from_message(extmsg)
    result2 = message_callbacks.get_callbacks_from_message(stdmsg)

    assert result2 == [callbacks.callbackvalue2]
    assert result1 == [callbacks.callbackvalue1]
