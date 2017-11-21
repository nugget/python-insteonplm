import unittest
from insteonplm.messages.message import Message
from insteonplm.messages.standardReceive import StandardReceive

def test_message():
    
    rawmessage = bytearray([0x02, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    shortmessage = bytearray([0x02, 0x50, 0x00])
    msg = Message.create(rawmessage) 

    assert isinstance(msg, StandardReceive)
    assert Message.iscomplete(rawmessage)
    assert not Message.iscomplete(shortmessage)


