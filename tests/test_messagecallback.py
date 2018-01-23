import sys
sys.path.append('../')
#import insteonplm
from insteonplm.messagecallback import MessageCallback
from insteonplm.constants import *
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.standardSend import StandardSend

def test_messagecallback_basic():
    callbacks = MessageCallback()
    callbacktest1 = "test callback 1"
    callbacktest2 = "test callback 2"

    msg_template = StandardReceive(None, None, 0x80, 0x11, None)
    callbacks[msg_template] = callbacktest1

    msg = StandardReceive('1a2b3c', '4d5e6f', 0x80, 0x11, 0xff)

    callback1 = callbacks[msg]
    print('Callback: ', callback1)
    print('MT Code: {:x}'.format(msg.code))
    print('msg: ', msg.to_hex())
    assert callback1 == callbacktest1

def test_messagecallback_msg():
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add_message_callback(StandardReceive(None, None, None, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], None), callbacktest)
    msg1 = StandardReceive(address, target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], COMMAND_LIGHT_ON_0X11_NONE['cmd2'])
    msg2 = StandardReceive(address, target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff)

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

    callbacks.add_message_callback(StandardSend(None, None, None, None), callbacktest1)
    callbacks.add_message_callback(StandardSend(None, None, None, None), callbacktest2)
    callbacks.add_message_callback(StandardSend(None, None, None, None, acknak=MESSAGE_NAK), callbacktest3)

    msg1 = StandardSend('111111', 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xcd)
    msg2 = StandardSend('222222', 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff)
    msg3 = StandardSend('333333', 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff, MESSAGE_NAK)
    msg4 = StandardSend('444444', 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff, MESSAGE_ACK)

    callback1 = callbacks.get_callbacks_from_message(msg1)
    callback2 = callbacks.get_callbacks_from_message(msg2)
    callback3 = callbacks.get_callbacks_from_message(msg3)
    callback4 = callbacks.get_callbacks_from_message(msg4)
    
    assert len(callback1) == 2
    assert callback1[0] == callbacktest1
    assert callback1 == callback2
    assert callback3[0] == callbacktest3
    assert len(callback4) == 0


if __name__ == "__main__":
    test_messagecallback_basic()