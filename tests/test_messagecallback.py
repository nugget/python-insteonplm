import insteonplm
from insteonplm.messagecallback import MessageCallback
from insteonplm.constants import *
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend

def test_messagecallback_basic():
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"

    callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE, callbacktest1)
    callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, None, callbacktest2)

    callback1 = callbacks['50:01:None:None']
    callback2 = callbacks['50:02:None:None']
    assert callback1 == callbacktest1
    assert callback2 == callbacktest2

def test_messagecallback_msg():
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, callbacktest)
    msg1 = StandardReceive(address, target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], COMMAND_LIGHT_ON_0X11_NONE['cmd2'])
    msg2 = StandardReceive(address, target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff)

    callback1 = callbacks.get_callback_from_message(msg1)
    callback2 = callbacks.get_callback_from_message(msg2)

    assert callback1 == callbacktest
    assert callback2 == callbacktest

def test_messagecallback_acknak():
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, None, callbacktest, MESSAGE_NAK)
    msg1 = StandardSend(target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff, MESSAGE_NAK)
    msg2 = StandardSend(target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff, MESSAGE_ACK)

    callback1 = callbacks.get_callback_from_message(msg1)
    callback2 = callbacks.get_callback_from_message(msg2)

    assert callback1 == callbacktest
    assert callback2 == None