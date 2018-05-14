"""Test insteonplm X10 devices."""
import asyncio
import logging

from insteonplm.devices.x10 import X10OnOff
from insteonplm.messages.x10send import X10Send
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
        yield from asyncio.sleep(.1, loop)
        assert plm.sentmessage == '02632700'
        msg = X10Send(0x27, 0x00, 0x06)
        plm.message_received(msg)
        yield from  asyncio.sleep(.1, loop)
        assert plm.sentmessage == '02632280'
        yield from  asyncio.sleep(.1, loop)
        msg = X10Send(0x22, 0x00, 0x06)
        plm.message_received(msg)
        yield from  asyncio.sleep(.1, loop)

        # Send Off command and test both commands sent
        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop)
        assert plm.sentmessage == '02632700'
        msg = X10Send(0x27, 0x00, 0x06)
        plm.message_received(msg)
        yield from  asyncio.sleep(.1, loop)
        assert plm.sentmessage == '02632380'
        yield from  asyncio.sleep(.1, loop)
        msg = X10Send(0x23, 0x00, 0x06)
        plm.message_received(msg)
        yield from  asyncio.sleep(.1, loop)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))