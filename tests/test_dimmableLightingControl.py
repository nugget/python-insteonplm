import asyncio
import logging
import insteonplm
from insteonplm.constants import *
from insteonplm.aldb import ALDB
from insteonplm.address import Address

from insteonplm.messages import (StandardSend, StandardReceive,
                                 ExtendedSend, ExtendedReceive)
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.devices.dimmableLightingControl import (DimmableLightingControl, 
                                                        DimmableLightingControl_2475F)
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks 


def test_dimmableLightingControl():

    def run_test(loop):
        log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x01
        subcat = 0x04
        product_key = None
        description = 'SwitchLinc Dimmer (1000W)'
        model = '2476DH'
        device = DimmableLightingControl(plm, address, cat, subcat, product_key, description, model)

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

        device.states[0x01].set_level(0x55)
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x55, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x55, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x55).hex
        assert callbacks.callbackvalue1 == 0x55
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_dimmableLightingControl_manual_changes():
    def run_test(loop):
        log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x01
        subcat = 0x04
        product_key = None
        description = 'SwitchLinc Dimmer (1000W)'
        model = '2476DH'
        device = DimmableLightingControl(plm, address, cat, subcat, product_key, description, model)

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
        assert callbacks.callbackvalue1 == 0x66

        plm.message_received(StandardReceive(address,'000001', COMMAND_LIGHT_OFF_0X13_0X00, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_dimmableLightingControl_status():

    def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x01
        subcat = 0x04
        product_key = None
        description = 'SwitchLinc Dimmer (1000W)'
        model = '2476DH'

        device = DimmableLightingControl(plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00 # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        device.async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x08, 'cmd2':0x27}, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00).hex
        assert callbacks.callbackvalue1 == 0x27
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_2475F():

    def run_test(loop):
        class fanLincStatus(object):
            lightOnLevel = None
            fanOnLevel = None

            def device_status_callback1(self, id, state, value):
                self.lightOnLevel = value
    
            def device_status_callback2(self, id, state, value):
                self.fanOnLevel = value

        mockPLM = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x01
        subcat = 0x2e
        product_key = 0x00
        description = 'FanLinc Dual Band'
        model = '2475F'

        callbacks = fanLincStatus()

        device = DimmableLightingControl_2475F.create(mockPLM, address, cat, subcat, product_key, description, model)
    
        assert device.states[0x01].name == 'lightOnLevel'
        assert device.states[0x02].name == 'fanOnLevel'

        device.states[0x01].register_updates(callbacks.device_status_callback1)
        device.states[0x02].register_updates(callbacks.device_status_callback2)

        device.states[0x01].async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, acknak=MESSAGE_ACK)
        statusmsg = StandardReceive(address, target, {'cmd1':0xdf, 'cmd2':0x55}, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2,3))
        mockPLM.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop=loop)
        mockPLM.message_received(statusmsg)
        yield from asyncio.sleep(.1, loop=loop)

        assert callbacks.lightOnLevel == 0x55

        device.states[0x02].async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        ackmsg = StandardSend(address, {'cmd1':0x19, 'cmd2':0x03}, flags=0x00, acknak=MESSAGE_ACK)
        statusmsg = StandardReceive(address, target, {'cmd1':0xab, 'cmd2':0x77}, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2,3))
        mockPLM.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop=loop)
        mockPLM.message_received(statusmsg)
        yield from asyncio.sleep(.1, loop=loop)

        assert callbacks.lightOnLevel == 0x55
        assert callbacks.fanOnLevel == 0x77

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_dimmableLightingControl_2475F_status():

    def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x01
        subcat = 0x2e
        product_key = 0x00
        description = 'FanLinc Dual Band'
        model = '2475F'

        device = DimmableLightingControl_2475F(plm, address, cat, subcat, product_key, description, model)

        callbacks = MockCallbacks()
        device.states[0x02].register_updates(callbacks.callbackmethod1)

        device.states[0x02].async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE, cmd2=0x03, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, {'cmd1': 0x08, 'cmd2':0x27}, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3)))
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE, cmd2=0x03).hex
        assert callbacks.callbackvalue1 == 0x27
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))