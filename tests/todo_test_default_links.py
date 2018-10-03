"""Test insteonplm.evices module."""
import asyncio
import logging


import insteonplm.devices
from insteonplm.constants import (MESSAGE_ACK,
                                  COMMAND_ENTER_LINKING_MODE_0X09_NONE,
                                  COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00)
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.standardSend import StandardSend
# from insteonplm.messages.startAllLinking import StartAllLinking
from insteonplm.messages.userdata import Userdata
from tests.mockPLM import MockPLM

_LOGGING = logging.getLogger(__name__)
_LOGGING.setLevel(logging.DEBUG)


def test_create_device():
    """Test create device."""
    async def run_test(loop):
        mockPLM = MockPLM(loop)
        linkcode = 0x01
        group = 0x00
        address = '112233'
        cat = 0x02
        subcat = 0x39
        firmware = 0x44
        # Create OutletLinc
        device = insteonplm.devices.create(mockPLM, address,
                                           cat, subcat, firmware)

        # Start the process with an All-Link complete message with
        # the IM as a controller of Group 0x00
        msg = AllLinkComplete(linkcode, group, address, cat, subcat, firmware)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)

        # The device should start linking based on the groups in
        # self.states
        assert mockPLM.sentmessage == StandardSend(
            device.address, COMMAND_ENTER_LINKING_MODE_0X09_NONE,
            cmd2=0x01).hex
        msg = StandardSend(device.address,
                           COMMAND_ENTER_LINKING_MODE_0X09_NONE,
                           cmd2=0x01, acknak=MESSAGE_ACK)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)
        # Confirm that the link attempt to group 0x01 completed
        msg = AllLinkComplete(0x00, 0x01, address, cat, subcat, firmware)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)

        # The device should then start linking to group 0x02
        assert mockPLM.sentmessage == StandardSend(
            device.address, COMMAND_ENTER_LINKING_MODE_0X09_NONE,
            cmd2=0x02).hex
        await asyncio.sleep(1, loop=loop)
        # Confirm that the link attempt to group 0x02 completed
        msg = AllLinkComplete(0x00, 0x01, address, cat, subcat, firmware)
        device.receive_message(msg)
        await asyncio.sleep(.1, loop=loop)

        # The device will now attempt to read the ALDB
        msg = ExtendedSend(address,
                           COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
                           userdata=Userdata())
        msg.set_checksum()
        assert mockPLM.sentmessage == msg.hex
        # Send a dummy ALDB record as a high water mark to end the process
        msg = ExtendedReceive(
            address, '111111',
            commandtuple=COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00,
            userdata=Userdata({'d1': 0,
                               'd2': 0x01,
                               'd3': 0xff,
                               'd4': 0x77,
                               'd5': 0,
                               'd6': 0,
                               'd7': 0,
                               'd8': 0,
                               'd9': 0,
                               'd10': 0,
                               'd11': 0,
                               'd12': 0,
                               'd13': 0,
                               'd14': 0x3b}))
        device.receive_message(msg)
        await asyncio.sleep(1, loop=loop)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    _LOGGING.error('Got here')
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)
