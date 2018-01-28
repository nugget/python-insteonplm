from insteonplm.messagecallback import MessageCallback
from insteonplm.constants import *
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.userdata import Userdata

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
    print('msg: ', msg.to_hex())

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

    msg1 = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xcd)
    msg2 = StandardSend('222222', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
    msg3 = StandardSend('333333', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_NAK)
    msg4 = StandardSend('444444', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_ACK)

    callback1 = callbacks.get_callbacks_from_message(msg1)
    callback2 = callbacks.get_callbacks_from_message(msg2)
    callback3 = callbacks.get_callbacks_from_message(msg3)
    callback4 = callbacks.get_callbacks_from_message(msg4)
    
    assert len(callback1) == 2
    assert len(callback2) == 1
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
