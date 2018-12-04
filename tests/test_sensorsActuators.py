"""Test INSTEON Sensor Actuator devices."""

import asyncio
import logging

from insteonplm.constants import (COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                                  MESSAGE_ACK,
                                  MESSAGE_TYPE_DIRECT_MESSAGE_ACK)
# SensorsActuators class not tested ?
from insteonplm.devices.sensorsActuators import SensorsActuators_2450
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks

_LOGGING = logging.getLogger(__name__)
_LOGGING.setLevel(logging.DEBUG)


def test_SensorsActuators_2450_status():
    """Test SensorActuator device model 2450."""
    async def run_test(loop):
        """Asyncio test run."""
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x07
        subcat = 0x00
        product_key = 0x00
        description = 'I/O Linc'
        model = '2450'

        callbacks = MockCallbacks()

        device = SensorsActuators_2450(plm, address, cat, subcat,
                                       product_key, description, model)
        plm.devices[address] = device
        assert device.states[0x01].name == 'openClosedRelay'
        assert device.states[0x02].name == 'ioLincSensor'

        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)

        device.async_refresh_state()
        await asyncio.sleep(.1, loop=loop)

        # First state
        sentmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        assert plm.sentmessage == sentmsg.hex

        receivedmsg = StandardSend(address,
                                   COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                   acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        await asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x55,
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0))
        plm.message_received(receivedmsg)
        await asyncio.sleep(.3, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        # Second state
        receivedmsg = StandardSend(address,
                                   COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                                   acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        await asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, {'cmd1': 0x01, 'cmd2': 0x00},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, 0))
        plm.message_received(receivedmsg)
        await asyncio.sleep(.1, loop=loop)

        sentmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01)
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue1 == 0xff
        assert callbacks.callbackvalue2 == 0

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)
