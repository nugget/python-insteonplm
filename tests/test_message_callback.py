from insteonplm.messagecallback import MessageCallback
from insteonplm.constants import *
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.userdata import Userdata
from .mockCallbacks import MockCallbacks


import logging
log = logging.getLogger(__name__)

def test_messagecallback_basic():
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"

    msg_template = StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE, flags=0x80)
    callbacks[msg_template] = callbacktest1

    msg = StandardReceive('1a2b3c', '4d5e6f', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, flags=0x80)

    callback1 = callbacks.get_callbacks_from_message(msg)
    print('Callback: ', callback1)
    print('MT Code: {:x}'.format(msg.code))
    print('msg: ', msg.hex)

    assert len(callback1) == 1
    assert callback1[0] == callbacktest1

def test_messagecallback_msg():
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE), callbacktest)
    msg1 = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x00)
    msg2 = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)

    callback1 = callbacks.get_callbacks_from_message(msg1)
    callback2 = callbacks.get_callbacks_from_message(msg2)

    assert callback1[0] == callbacktest
    assert callback2[0] == callbacktest

def test_messagecallback_acknak():
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"
    callbacktest3 = "test callback 3"
    callbacktest4 = "test callback 4"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add(StandardSend.template(address = address), callbacktest1)
    callbacks.add(StandardSend.template(address = address, acknak=MESSAGE_ACK), callbacktest2)
    callbacks.add(StandardSend.template(), callbacktest3)
    callbacks.add(StandardSend.template(acknak=MESSAGE_NAK), callbacktest4)

    msg1 = StandardSend(address,  COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xcd)
    msg2 = StandardSend('222222', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
    msg3 = StandardSend('333333', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_NAK)
    msg4 = StandardSend('444444', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_ACK)

    log.debug('Getting callbacks for message 1')
    callback1 = callbacks.get_callbacks_from_message(msg1)
    log.debug('Getting callbacks for message 2')
    callback2 = callbacks.get_callbacks_from_message(msg2)
    log.debug('Getting callbacks for message 3')
    callback3 = callbacks.get_callbacks_from_message(msg3)
    log.debug('Getting callbacks for message 4')
    callback4 = callbacks.get_callbacks_from_message(msg4)
    
    assert len(callback1) == 4
    assert len(callback2) == 2
    assert len(callback3) == 2
    assert len(callback4) == 1

def test_message_callback_extended():
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add(ExtendedReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE, userdata=Userdata({'d1':0x02})), callbacktest)
    msg1 = ExtendedReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, Userdata({'d1':0x02}), cmd2=0xff)
    msg2 = ExtendedReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, Userdata({'d1':0x03, 'd2':0x02}), cmd2=0xff)

    callback1 = callbacks.get_callbacks_from_message(msg1)
    callback2 = callbacks.get_callbacks_from_message(msg2)

    assert callback1[0] == callbacktest
    assert len(callback2) == 0

def test_delete_callback():
    
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"
    callbacktest3 = "test callback 3"

    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add(StandardSend.template(), callbacktest1)
    callbacks.add(StandardSend.template(), callbacktest2)
    callbacks.add(StandardSend.template(acknak=MESSAGE_NAK), callbacktest3)

    msg = StandardSend('333333', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_NAK)

    callbackList = callbacks.get_callbacks_from_message(msg)
    assert len(callbackList) == 3

    callbacks.remove(StandardSend.template(), callbacktest2)
    callbackList = callbacks.get_callbacks_from_message(msg)
    assert len(callbackList) == 2

def test_misc_messages():
    
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

    callbacklist1 = callbacks.get_callbacks_from_message(msg1)
    callbacklist2 = callbacks.get_callbacks_from_message(msg2)
    callbacklist3 = callbacks.get_callbacks_from_message(msg3)
    callbacklist4 = callbacks.get_callbacks_from_message(msg4)

    assert callbacklist1[0] == callbacktest1
    assert callbacklist2[0] == callbacktest2
    assert len(callbacklist3) == 0
    assert callbacklist4[0] == callbacktest3

def test_extended_ack():
    callbacks = MockCallbacks()
    callbacks.callbackvalue1 = "Callback 1"
    callbacks.callbackvalue2 = "Callback 2"
    message_callbacks = MessageCallback()
    address = '1a2b3c'
    
    message_callbacks.add(ExtendedSend.template(address, acknak=MESSAGE_ACK), callbacks.callbackvalue1)
    message_callbacks.add(StandardSend.template(address, acknak=MESSAGE_ACK), callbacks.callbackvalue2)
    extmsg = ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE, {'d1':0x02}, cmd2=0xff, acknak=MESSAGE_ACK)
    stdmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_ACK)
    result1 = message_callbacks.get_callbacks_from_message(extmsg)
    result2 = message_callbacks.get_callbacks_from_message(stdmsg)

    assert result2 == [callbacks.callbackvalue2]
    assert result1 == [callbacks.callbackvalue1]

    