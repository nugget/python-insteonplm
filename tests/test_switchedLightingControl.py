from insteonplm.devices.switchedLightingControl import SwitchedLightingControl, SwitchedLightingControl_2663_222
from insteonplm.messages.standardSend import StandardSend 
from insteonplm.messages.standardReceive import StandardReceive 
from insteonplm.messages.extendedReceive import ExtendedReceive 
from insteonplm.messages.userdata import Userdata
from insteonplm.messages.messageFlags import MessageFlags 
from insteonplm.address import Address
from insteonplm.constants import *
from .mockPLM import MockPLM

def test_switchedLightingControl_basic():
    plm = MockPLM()
    light = SwitchedLightingControl(plm, Address('1a2b3c'), 0x02, 0x04, 0x0, 'Some switch', 'ABC123')
    light.states[0x01].on()
    assert plm.sentmessage == str(StandardSend(Address('1a2b3c'), 0x11, 0xff))

def test_switchedLightingControl_callback():
    
    class lightStatus(object):
        lightOnLevel = None

        def state_status_callback(self, id, state, value):
            print('Called device callback')
            self.lightOnLevel = value

    plm = MockPLM()
    light = SwitchedLightingControl(plm, Address('1a2b3c'), 0x02, 0x04, 0x0, 'Some switch', 'ABC123')
    callback = lightStatus()
    light.states[0x01].register_updates(callback.state_status_callback)

    plm.message_received(StandardReceive(Address('1a2b3c'), Address('4d5e6f'), 0x00, 0x11, 0xff))
    assert callback.lightOnLevel == 0xff

def test_SwitchedLightingControl_2663_222():
    
    class lightStatus(object):
        lightOnLevelTop = None
        lightOnLevelBot = None

        def state_top_status_callback(self, id, state, value):
            print('Called device callback top')
            self.lightOnLevelTop = value

        def state_bot_status_callback(self, id, state, value):
            print('Called device callback top')
            self.lightOnLevelBot = value

    plm = MockPLM()
    light = SwitchedLightingControl_2663_222(plm, Address('1a2b3c'), 0x02, 0x04, 0x0, 'Some switch', 'ABC123')
    callback = lightStatus()
    light.states[0x01].register_updates(callback.state_top_status_callback)
    light.states[0x02].register_updates(callback.state_bot_status_callback)

    plm.message_received(StandardReceive(Address('1a2b3c'), Address('4d5e6f'), 0x00, 0x11, 0xff))
    assert callback.lightOnLevelTop == 0xff
    assert callback.lightOnLevelBot == None

    userdata = Userdata.create()
    userdata['d1'] = 0x02
    plm.message_received(ExtendedReceive(Address('1a2b3c'), Address('4d5e6f'), 0x11, 0xaa, userdata))
    assert callback.lightOnLevelBot == 0xff

    
    callback.lightOnLevelTop = 0x11
    callback.lightOnLevelBot = 0x22
    plm.message_received(StandardSend(Address('1a3b3c'),  0x19, 0x00, flags=0x05,acknak=MESSAGE_ACK))
    plm.message_received(StandardReceive(Address('1a3b3c'), Address('4d5e6f'), MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0) , 0x23, 0xaa))
    assert callback.lightOnLevelTop == 0xaa
    assert callback.lightOnLevelBot == 0x22

    plm.message_received(StandardSend(Address('1a3b3c'),  0x19, 0x01, flags=0x05,acknak=MESSAGE_ACK))
    plm.message_received(StandardReceive(Address('1a3b3c'), Address('4d5e6f'), MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0) , 0x23, 0x02))
    assert callback.lightOnLevelTop == 0x00
    assert callback.lightOnLevelBot == 0xff