"""Test insteonplm X10 devices."""
import asyncio

from insteonplm.devices.x10 import X10OnOff
from insteonplm.messages.x10send import X10Send
from .mockPLM import MockPLM

def test_x10OnOff():
    @asyncio.coroutine
    def run_test(loop):
        housecode = 'C' # byte 0x02
        unitcode = 9    # byte 0x07
        plm = MockPLM(loop)
        device = X10OnOff(plm, housecode, unitcode)
        plm.devices[device.address.hex] = device
        assert device.address.human == 'X10.{}.{:02d}'.format(housecode, unitcode)

        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop)
        print('Message: ', plm.sentmessage)
        msg = X10Send(0x27, 0x00, 0x06)
        plm.message_received(msg)
        yield from  asyncio.sleep(.1, loop)
        print('Message: ', plm.sentmessage)
        yield from asyncio.sleep(10, loop)
        assert False
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))