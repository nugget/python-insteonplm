import asyncio
import logging
import insteonplm
from insteonplm.constants import *
from insteonplm.aldb import ALDB
from insteonplm.address import Address

from insteonplm.messages import (StandardSend, StandardReceive,
                                 ExtendedSend, ExtendedReceive)
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.devices.switchedLightingControl import (SwitchedLightingControl, 
                                                        SwitchedLightingControl_2663_222)
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks 

def test_switchedLightingControl():

    def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl(plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00 # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff).hex
        assert callbacks.callbackvalue1 == 0xff

        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, COMMAND_LIGHT_OFF_0X13_0X00, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00).hex
        assert callbacks.callbackvalue1 == 0x00
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_maual_changes():

    def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl(plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00 # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        plm.message_received(StandardReceive(address, '000001', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x66, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        plm.message_received(StandardReceive(address,'000001', COMMAND_LIGHT_OFF_0X13_0X00, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_status():

    def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl(plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00 # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        device.states[0x01].async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x09, 'cmd2': 0xff},
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00).hex
        assert callbacks.callbackvalue1 == 0xff
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_2663_222():
    @asyncio.coroutine
    def run_test(loop):
        plm = MockPLM(loop)
        callbacks = MockCallbacks()

        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00 # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address
    
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)

        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff).hex
        plm.message_received(StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x09, 'cmd2':0xff}, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff
        
        device.states[0x02].on()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE, {'d1':0x02}, cmd2=0xff, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x09, 'cmd2':0xff}, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE, {'d1':0x02}, cmd2=0xff).hex
        assert callbacks.callbackvalue2 == 0xff

        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00).hex
        plm.message_received(StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x09, 'cmd2':0x00}, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00).hex
        assert callbacks.callbackvalue1 == 0x00
        
        device.states[0x02].off()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(ExtendedSend(address, COMMAND_LIGHT_OFF_0X13_0X00, {'d1':0x02}, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x09, 'cmd2':0x00}, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == ExtendedSend(address, COMMAND_LIGHT_OFF_0X13_0X00, {'d1':0x02}).hex
        assert callbacks.callbackvalue2 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_2663_222_manual_change():
    @asyncio.coroutine
    def run_test(loop):
        plm = MockPLM(loop)
        callbacks = MockCallbacks()

        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00 # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address
    
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)

        plm.message_received(StandardReceive(address, '000001', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x66, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        plm.message_received(StandardReceive(address,'000001', COMMAND_LIGHT_OFF_0X13_0X00, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00

        plm.message_received(StandardReceive(address, '000002', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x66,
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue2 == 0xff
        
        plm.message_received(StandardReceive(address, '000002', COMMAND_LIGHT_OFF_0X13_0X00,
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue2 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_2663_222_status():
    @asyncio.coroutine
    def run_test(loop):
        class lightStatus(object):
            lightOnLevel1 = None
            lightOnLevel2 = None

            def device_status_callback1(self, id, state, value):
                self.lightOnLevel1 = value
    
            def device_status_callback2(self, id, state, value):
                self.lightOnLevel2 = value

        mockPLM = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        callbacks = lightStatus()

        device = SwitchedLightingControl_2663_222.create(mockPLM, address, cat, subcat, product_key, description, model)
    
        assert device.states[0x01].name == 'outletTopOnOff'
        assert device.states[0x02].name == 'outletBottomOnOff'

        device.states[0x01].register_updates(callbacks.device_status_callback1)
        device.states[0x02].register_updates(callbacks.device_status_callback2)


        device.states[0x02].async_refresh_state()
        yield from asyncio.sleep(.1, loop)
        ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01, acknak=MESSAGE_ACK)
        statusmsg = StandardReceive(address, target,  {'cmd1':0x03, 'cmd2':0x01}, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2,3))
        mockPLM.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop)
        mockPLM.message_received(statusmsg)
        yield from asyncio.sleep(.1, loop)
        #assert callbacks.lightOnLevel1 == 0xff
        assert callbacks.lightOnLevel2 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))