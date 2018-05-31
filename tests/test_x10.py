"""Test insteonplm X10 devices."""
import asyncio
import logging

from insteonplm.constants import (X10_COMMAND_ON,
                                  X10_COMMAND_OFF,
                                  X10_COMMAND_DIM,
                                  X10_COMMAND_BRIGHT)
from insteonplm.devices.x10 import (X10OnOff,
                                    X10Dimmable,
                                    X10AllUnitsOff,
                                    X10AllLightsOff,
                                    X10AllLightsOn)
from insteonplm.messages.x10send import X10Send
from insteonplm.messages.x10received import X10Received
import insteonplm.utils
from .mockCallbacks import MockCallbacks
from .mockPLM import MockPLM


_LOGGER = logging.getLogger()


def test_x10OnOff():
    @asyncio.coroutine
    def run_test(loop):
        housecode = 'C' # byte 0x02
        unitcode = 9    # byte 0x07
        plm = MockPLM(loop)
        device = X10OnOff(plm, housecode, unitcode)
        plm.devices[device.address.id] = device
        _LOGGER.debug('X10 device id: %s', device.address.id)
        assert device.address.human == 'X10.{}.{:02d}'.format(housecode, unitcode)

        # Send On command and test both commands sent
        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632700'
        msg = X10Send(0x27, 0x00, 0x06)
        device.receive_message(msg)
        yield from  asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632280'
        yield from  asyncio.sleep(.1, loop=loop)
        msg = X10Send(0x22, 0x00, 0x06)
        device.receive_message(msg)
        yield from  asyncio.sleep(.1, loop=loop)

        # Send Off command and test both commands sent
        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632700'
        msg = X10Send(0x27, 0x00, 0x06)
        device.receive_message(msg)
        yield from  asyncio.sleep(.1, loop=loop)
        assert plm.sentmessage == '02632380'
        yield from  asyncio.sleep(.1, loop=loop)
        msg = X10Send(0x23, 0x00, 0x06)
        device.receive_message(msg)
        yield from  asyncio.sleep(.1, loop=loop)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_dimmable():
    @asyncio.coroutine
    def run_test(loop):
        housecode = 'C' # byte 0x02
        unitcode = 9    # byte 0x07
        newval = 200
        steps = round(newval / (255/22)) + 1
        _LOGGER.info('Steps %d', steps)
        plm = MockPLM(loop)
        cb = MockCallbacks()
        device = X10Dimmable(plm, housecode, unitcode)
        device.states[0x01].register_updates(cb.callbackmethod1)
        plm.devices[device.address.id] = device

        device.states[0x01].set_level(200)
        for i in range(0, steps):
            _LOGGER.info('Sending ACK messages')
            msg = X10Send(0x27, 0x00, 0x06)
            device.receive_message(msg)
            yield from  asyncio.sleep(.1, loop=loop)

            yield from  asyncio.sleep(.1, loop=loop)
            msg = X10Send(0x25, 0x80, 0x06)
        _LOGGER.info('New value: 0x%02x', cb.callbackvalue1)
        assert cb.callbackvalue1 == round((steps -1)*(255 / 22))
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_on_received():
    @asyncio.coroutine
    def run_test(loop):
        housecode = 'C' # byte 0x02
        unitcode = 9    # byte 0x07
        plm = MockPLM(loop)
        cb = MockCallbacks()
        device = X10Dimmable(plm, housecode, unitcode, 22)
        plm.devices[device.address.id] = device
        device.states[0x01].register_updates(cb.callbackmethod1)

        msg = X10Received.command_msg(housecode, X10_COMMAND_ON)
        device.receive_message(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert cb.callbackvalue1 == 0xff

        msg = X10Received.command_msg(housecode, X10_COMMAND_OFF)
        device.receive_message(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert cb.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_all_unit_types():
    plm = MockPLM()
    all_unit_off = X10AllUnitsOff(plm, 'A', 20)
    all_lights_off = X10AllLightsOff(plm, 'A', 22)
    all_lights_on = X10AllLightsOn(plm, 'A', 21)

    assert all_unit_off.description == 'X10 All Units Off Device'
    assert all_lights_off.description == 'X10 All Lights Off Device'
    assert all_lights_on.description == 'X10 All Lights On Device'