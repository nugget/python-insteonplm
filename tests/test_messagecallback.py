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

    callback1 = callbacks.get_callback_from_message(msg1)
    callback2 = callbacks.get_callback_from_message(msg2)

    assert callback1 == callbacktest
    assert callback2 == callbacktest

def test_messagecallback_acknak():
    callbacks = MessageCallback()
    callbacktest = "test callback"
    address = '1a2b3c'
    target = '4d5e6f'

    callbacks.add_message_callback(StandardSend(None, None, None, None, acknak=MESSAGE_NAK), callbacktest)
    msg1 = StandardSend(target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff, MESSAGE_NAK)
    msg2 = StandardSend(target, 0x00, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff, MESSAGE_ACK)

    callback1 = callbacks.get_callback_from_message(msg1)
    callback2 = callbacks.get_callback_from_message(msg2)

    assert callback1 == callbacktest
    assert callback2 == None


if __name__ == "__main__":
    test_messagecallback_basic()