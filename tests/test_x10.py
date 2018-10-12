"""Test insteonplm X10 devices."""
import asyncio
import logging

from insteonplm.constants import (X10_COMMAND_ON,
                                  X10_COMMAND_OFF,
                                  X10_COMMAND_ALL_UNITS_OFF)
from insteonplm.devices.x10 import (X10OnOff,
                                    X10Dimmable,
                                    X10AllUnitsOff,
                                    X10AllLightsOff,
                                    X10AllLightsOn)
from insteonplm.messages.x10send import X10Send
from insteonplm.messages.x10received import X10Received
from .mockCallbacks import MockCallbacks
from .mockPLM import MockPLM


_LOGGER = logging.getLogger(__name__)


def test_x10OnOff():
    """Test X10 On/Off device."""
    async def run_test(loop):
        housecode = 'C'  # byte 0x02
        unitcode = 9     # byte 0x07
        plm = MockPLM(loop)
        device = X10OnOff(plm, housecode, unitcode)
        plm.devices[device.address.id] = device
        _LOGGER.debug('X10 device id: %s', device.address.id)
        assert device.address.human == 'X10.{}.{:02d}'.format(housecode,
                                                              unitcode)

        # Send On command and test both commands sent
        device.states[0x01].on()
        await asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632700'
        msg = X10Send(0x27, 0x00, 0x06)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632280'
        await asyncio.sleep(.1, loop=loop)
        msg = X10Send(0x22, 0x00, 0x06)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)

        # Send Off command and test both commands sent
        device.states[0x01].off()
        await asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632700'
        msg = X10Send(0x27, 0x00, 0x06)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632380'
        await asyncio.sleep(.1, loop=loop)
        msg = X10Send(0x23, 0x00, 0x06)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_dimmable():
    """Test X10 dimmable device."""
    async def run_test(loop):
        housecode = 'C'  # byte 0x02
        unitcode = 9     # byte 0x07
        newval = 200
        steps = round(newval / (255 / 22)) + 1
        _LOGGER.info('Steps %d', steps)
        plm = MockPLM(loop)
        cb = MockCallbacks()
        device = X10Dimmable(plm, housecode, unitcode)
        device.states[0x01].register_updates(cb.callbackmethod1)
        plm.devices[device.address.id] = device

        device.states[0x01].set_level(200)
        # pylint: disable=unused-variable
        for i in range(0, steps):
            _LOGGER.info('Sending ACK messages')
            msg = X10Send(0x27, 0x00, 0x06)
            device.receive_message(msg)
            await asyncio.sleep(.1, loop=loop)

            await asyncio.sleep(.1, loop=loop)
            msg = X10Send(0x25, 0x80, 0x06)
        _LOGGER.info('New value: 0x%02x', cb.callbackvalue1)
        assert cb.callbackvalue1 == round((steps - 1) * (255 / 22))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_on_received():
    """Test X10 on message received."""
    async def run_test(loop):
        housecode = 'C'  # byte 0x02
        unitcode = 9     # byte 0x07
        plm = MockPLM(loop)
        cb = MockCallbacks()
        device = X10Dimmable(plm, housecode, unitcode, 22)
        plm.devices[device.address.id] = device
        device.states[0x01].register_updates(cb.callbackmethod1)

        msg = X10Received.command_msg(housecode, X10_COMMAND_ON)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)
        assert cb.callbackvalue1 == 0xff

        msg = X10Received.command_msg(housecode, X10_COMMAND_OFF)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)
        assert cb.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_all_unit_types():
    """Test X10 All Unit device types."""
    plm = MockPLM()
    all_units_off = X10AllUnitsOff(plm, 'A', 20)
    all_lights_off = X10AllLightsOff(plm, 'A', 22)
    all_lights_on = X10AllLightsOn(plm, 'A', 21)

    assert all_units_off.description == 'X10 All Units Off Device'
    assert all_lights_off.description == 'X10 All Lights Off Device'
    assert all_lights_on.description == 'X10 All Lights On Device'
    assert all_units_off.id == 'x10A20'


def test_all_units_on_off():
    """Test X10 All Units Off command."""
    async def run_test(loop):
        plm = MockPLM(loop)
        callbacks = MockCallbacks()
        all_units_off = X10AllUnitsOff(plm, 'A', 20)
        all_lights_off = X10AllLightsOff(plm, 'A', 22)
        all_lights_on = X10AllLightsOn(plm, 'A', 21)

        all_units_off.states[0x01].register_updates(callbacks.callbackmethod1)
        all_lights_off.states[0x01].register_updates(callbacks.callbackmethod2)
        all_lights_on.states[0x01].register_updates(callbacks.callbackmethod3)

        msg = X10Received.command_msg('A', X10_COMMAND_ALL_UNITS_OFF)
        plm.message_received(msg)
        _LOGGER.debug('Should have 1st callback')
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00
        _LOGGER.debug('Should have 2nd callback')
        await asyncio.sleep(2, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)
