import asyncio
import logging
import insteonplm
from insteonplm.constants import *
from insteonplm.aldb import ALDB
from insteonplm.address import Address
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedSend import ExtendedSend 
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl_2663_222 
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl_2475F
from insteonplm.devices.securityHealthSafety import SecurityHealthSafety 
from insteonplm.devices.securityHealthSafety import SecurityHealthSafety_2982_222
from insteonplm.devices.sensorsActuators import SensorsActuators_2450 
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks 

def test_switchedLightingControl():

    def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
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

        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02621a2b3c0011ff'
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_group():
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
        ackmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, acknak=MESSAGE_ACK)
        dirmsg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3))
        plm.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(dirmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff
        
        yield from asyncio.sleep(.1, loop=loop)
        plm.sentmessage = None
        device.states[0x02].on()
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE, {'d1':0x02}, cmd2=0xff).hex

        ackmsg = ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE, {'d1':0x02}, cmd2=0xff, acknak=MESSAGE_ACK)
        callbacksfound = plm.message_callbacks.get_callbacks_from_message(ackmsg)
        dirmsg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0, 2, 3))
        plm.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(dirmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue2 == 0xff
        yield from asyncio.sleep(.1, loop=loop)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_switchedLightingControl_2663_222():
    plm = MockPLM()
    address = '1a2b3c'
    cat = 0x02
    subcat = 0x0d
    product_key = 0x00
    description = 'ToggleLinc Relay'
    model = '2466S'
    device = SwitchedLightingControl_2663_222.create(plm, address, cat, subcat, product_key,description, model)
    assert len(device.states) == 2

def test_switchedLightingControl_2663_222_status():
    @asyncio.coroutine
    def run_test(loop):
        class lightStatus(object):
            lightOnLevel1 = None
            lightOnLevel2 = None

            def device_status_callback1(self, id, state, value):
                print('Called device 1 callback')
                self.lightOnLevel1 = value
    
            def device_status_callback2(self, id, state, value):
                print('Called device 2 callback')
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

def test_switchedLightingControl_2475F_status():

    def run_test(loop):
        class fanLincStatus(object):
            lightOnLevel = None
            fanOnLevel = None

            def device_status_callback1(self, id, state, value):
                print('Called device 1 callback')
                self.lightOnLevel = value
    
            def device_status_callback2(self, id, state, value):
                print('Called device 2 callback')
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

def test_securityhealthsafety():
    @asyncio.coroutine
    def run_test(loop):
        class sensorState(object):
            sensor = None

            def sensor_status_callback(self, id, state, value):
                print('Called sensor callback')
                self.sensor = value

        mockPLM = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'
        cmd1 = 0x11
        cmd2 = 0x04

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = sensorState()

        device = SecurityHealthSafety.create(mockPLM, address, cat, subcat, product_key, description, model)
        device.states[0x01].register_updates(callbacks.sensor_status_callback)
        msg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2, flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        mockPLM.message_received(msg)
        asyncio.sleep(.1, loop=loop)
        assert callbacks.sensor == cmd2
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_securityhealthsafety_2982_222():
    
    class sensorState(object):
        sensor = None

        def sensor_status_callback(self, id, state, value):
            print('Called sensor callback')
            self.sensor = value

    mockPLM = MockPLM()
    address = '1a2b3c'
    target = '4d5e6f'
    id1 = '1a2b3c'
    id2 = '1a2b3c_2'
    cmd1 = 0x11
    cmd2 = 0x04

    cat = 0x10
    subcat = 0x00
    product_key = 0x00
    description = 'Generic Security, Heath and Safety Device'
    model = ''

    callbacks = sensorState()

    device = SecurityHealthSafety_2982_222.create(mockPLM, address, cat, subcat, product_key, description, model)
    device.states[0x01].register_updates(callbacks.sensor_status_callback)
    msg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2, flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 0, 0))
    mockPLM.message_received(msg)
    assert callbacks.sensor == 0x6f

def test_SensorsActuators_2450():

    def run_test(loop):
        class IOLincStatus(object):
            relayOnLevel = None
            sensorOnLevel = None

            def device_status_callback1(self, id, state, value):
                print('Called state 1 callback ', value)
                self.relayOnLevel = value
    
            def device_status_callback2(self, id, state, value):
                print('Called state 2 callback ', value)
                self.sensorOnLevel = value

        mockPLM = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x07
        subcat = 0x00
        product_key = 0x00
        description = 'I/O Linc'
        model = '2450'

        callbacks = IOLincStatus()

        device = SensorsActuators_2450.create(mockPLM, address, cat, subcat, product_key, description, model)
    
        assert device.states[0x01].name == 'relayOpenClosed'    
        assert device.states[0x02].name == 'sensorOpenClosed'

        device.states[0x01].register_updates(callbacks.device_status_callback1)
        device.states[0x02].register_updates(callbacks.device_status_callback2)

        device.async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        assert mockPLM.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00).hex

        ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, acknak=MESSAGE_ACK)
        statusmsg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x55, flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0))
        mockPLM.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop=loop)
        mockPLM.message_received(statusmsg)
        yield from asyncio.sleep(.3, loop=loop)
        assert callbacks.relayOnLevel == 0xff

        
        assert mockPLM.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01).hex
    
        ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01, acknak=MESSAGE_ACK)
        statusmsg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x33, flags=MessageFlags.create(MESSAGE_TYPE_BROADCAST_MESSAGE, 0))
        mockPLM.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop=loop)
        mockPLM.message_received(statusmsg)
        yield from asyncio.sleep(.1, loop=loop)

        assert callbacks.relayOnLevel == 0xff
        assert callbacks.sensorOnLevel == 1

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))