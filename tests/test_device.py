"""Test insteonplm.evices module."""
import asyncio
import logging

from insteonplm.constants import (COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  MESSAGE_ACK)
from insteonplm.messages.standardSend import StandardSend
import insteonplm.devices
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl
from tests.mockPLM import MockPLM
from insteonplm.devices import DIRECT_ACK_WAIT_TIMEOUT

_LOGGING = logging.getLogger(__name__)


def test_create_device():
    """Test create device."""
    plm = MockPLM()
    device = insteonplm.devices.create(plm, '112233', 0x01, 0x0d, None)
    assert device.id == '112233'
    assert isinstance(device, DimmableLightingControl)


def test_create_device_from_bytearray():
    """Test create device from byte array."""
    plm = MockPLM()
    target = bytearray()
    target.append(0x01)
    target.append(0x0d)
    device = insteonplm.devices.create(plm, '112233',
                                       target[0], target[1],
                                       None)
    assert device.id == '112233'
    assert isinstance(device, DimmableLightingControl)


def test_send_msg():

    @asyncio.coroutine
    def run_test(loop):
        mockPLM = MockPLM(loop)
        address = '1a2b3c'
        device = insteonplm.devices.create(mockPLM, address, 0x01, 0x0d, 0x44)
        mockPLM.devices[address] = device

        # Send the ON command. This should be sent directly to the PLM
        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)

        # Send the OFF command. This should wait in queue until the
        # Direct ACK timeout
        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop=loop)

        # ACK the ON command
        msgreceived = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE,
                                   cmd2=0xff, flags=0x00, acknak=MESSAGE_ACK)
        mockPLM.message_received(msgreceived)
        asyncio.sleep(.1, loop=loop)

        _LOGGING.debug('Assert that the ON command is the command in the PLM')
        assert mockPLM.sentmessage == StandardSend(
            address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff, flags=0x00).hex

        # Sleep until the Direct ACK time out should expire
        yield from asyncio.sleep(DIRECT_ACK_WAIT_TIMEOUT + .2,
                                 loop=loop)

        # Confirm that the OFF command made it to the PLM
        assert mockPLM.sentmessage == StandardSend(
            address, COMMAND_LIGHT_OFF_0X13_0X00).hex

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
