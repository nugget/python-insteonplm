import asyncio
import logging
import insteonplm
from insteonplm.constants import *
from insteonplm.aldb import ALDB
from insteonplm.address import Address

from insteonplm.messages import (StandardSend, StandardReceive,
                                 ExtendedSend, ExtendedReceive)
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.devices.securityHealthSafety import (SecurityHealthSafety, 
                                                     SecurityHealthSafety_2842_222, 
                                                     SecurityHealthSafety_2845_2222,
                                                     SecurityHealthSafety_2852_222,
                                                     SecurityHealthSafety_2982_222)
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks 

@asyncio.coroutine
def onOffSenorTest(onOffClass, loop):
        plm = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'
        cmd1 = 0x11
        cmd2 = 0x04

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = onOffClass.create(plm, address, cat, subcat, product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2, 
                              flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        plm.message_received(msg)
        asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 1

        device = onOffClass.create(plm, address, cat, subcat, product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(address, target, COMMAND_LIGHT_OFF_0X13_0X00, 
                              flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        plm.message_received(msg)
        asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0


def test_securityhealthsafety():
    @asyncio.coroutine
    def run_test(loop):
        class sensorState(object):
            sensor = None

            def sensor_status_callback(self, id, state, value):
                self.sensor = value

        plm = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'
        cmd1 = 0x11
        cmd2 = 0x04

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = SecurityHealthSafety.create(plm, address, cat, subcat, product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2, 
                              flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        plm.message_received(msg)
        asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == cmd2

        device = SecurityHealthSafety.create(plm, address, cat, subcat, product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(address, target, COMMAND_LIGHT_OFF_0X13_0X00, 
                              flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        plm.message_received(msg)
        asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))

def test_securityhealthsafety_2982_222():

    plm = MockPLM()
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

    callbacks = MockCallbacks()

    device = SecurityHealthSafety_2982_222.create(plm, address, cat, subcat, product_key, description, model)
    device.states[0x01].register_updates(callbacks.callbackmethod1)
    msg = StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2, flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 0, 0))
    plm.message_received(msg)
    #target hiByte
    assert callbacks.callbackvalue1 == 0x6f 

def test_securityHealthSafety_2842_222():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(onOffSenorTest(SecurityHealthSafety_2842_222, loop))

def test_securityHealthSafety_2845_2222():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(onOffSenorTest(SecurityHealthSafety_2845_2222, loop))

def test_securityHealthSafety_2852_222():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(onOffSenorTest(SecurityHealthSafety_2852_222, loop))