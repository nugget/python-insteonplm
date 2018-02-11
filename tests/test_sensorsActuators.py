import asyncio
import logging
import insteonplm
from insteonplm.constants import *
from insteonplm.aldb import ALDB
from insteonplm.address import Address

from insteonplm.messages import (StandardSend, StandardReceive,
                                 ExtendedSend, ExtendedReceive)
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.devices.sensorsActuators import (SensorsActuators, 
                                                 SensorsActuators_2450)
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks 


def test_SensorsActuators_2450_status():

    def run_test(loop):

        plm = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x07
        subcat = 0x00
        product_key = 0x00
        description = 'I/O Linc'
        model = '2450'

        callbacks = MockCallbacks()

        device = SensorsActuators_2450.create(plm, address, cat, subcat, product_key, description, model)
    
        assert device.states[0x01].name == 'relayOpenClosed'    
        assert device.states[0x02].name == 'sensorOpenClosed'

        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)

        device.async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)

        # First state
        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00).hex

        plm.message_received(StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x55, 
                                             flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0)))
        yield from asyncio.sleep(.3, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        # Second state
        plm.message_received(StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01, acknak=MESSAGE_ACK))
        yield from asyncio.sleep(.1, loop=loop)
        plm.message_received(StandardReceive(address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x33, 
                                                 flags=MessageFlags.create(MESSAGE_TYPE_BROADCAST_MESSAGE, 0)))
        yield from asyncio.sleep(.1, loop=loop)

        assert plm.sentmessage == StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01).hex
        assert callbacks.callbackvalue1 == 0xff
        assert callbacks.callbackvalue2 == 1

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))