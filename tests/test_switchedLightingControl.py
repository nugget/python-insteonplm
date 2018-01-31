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
    assert plm.sentmessage == StandardSend(Address('1a2b3c'), COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff).hex

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

    plm.message_received(StandardReceive(Address('1a2b3c'), Address('4d5e6f'), COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff))
    assert callback.lightOnLevel == 0xff

def test_SwitchedLightingControl_2663_222():
    address = '1a2b3c'
    target = '4d5e6f'
    
    class lightStatus(object):
        lightOnLevelTop = None
        lightOnLevelBot = None

        def state_top_status_callback(self, id, state, value):
            print('Called device callback top')
            self.lightOnLevelTop = value

        def state_bot_status_callback(self, id, state, value):
            print('Called device callback bottom')
            self.lightOnLevelBot = value

    plm = MockPLM()
    light = SwitchedLightingControl_2663_222(plm, address, 0x02, 0x04, 0x0, 'Some switch', 'ABC123')
    callback = lightStatus()
    light.states[0x01].register_updates(callback.state_top_status_callback)
    light.states[0x02].register_updates(callback.state_bot_status_callback)

    plm.message_received(StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff))
    assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01).hex

    userdata = Userdata.create()
    userdata['d1'] = 0x02
    plm.message_received(ExtendedReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, userdata, cmd2=0xaa))
    assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01).hex

    
    callback.lightOnLevelTop = 0x11
    callback.lightOnLevelBot = 0x22
    plm.message_received(StandardSend(address,  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, flags=0x05,acknak=MESSAGE_ACK))
    plm.message_received(StandardReceive(address, target, {'cmd1':0x23, 'cmd2':0xaa}, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0)))
    assert callback.lightOnLevelTop == 0xaa
    assert callback.lightOnLevelBot == 0x22

    plm.message_received(StandardSend(address,  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01, flags=0x05,acknak=MESSAGE_ACK))
    plm.message_received(StandardReceive(address, target, {'cmd1':0x23, 'cmd2':0x02}, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0)))
    assert callback.lightOnLevelTop == 0x00
    assert callback.lightOnLevelBot == 0xff