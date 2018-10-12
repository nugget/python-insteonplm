"""Test the INSTEON PLM device."""
import asyncio
import logging

import insteonplm
from insteonplm.constants import (COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_OFF_0X13_0X00,
                                  MESSAGE_FLAG_BROADCAST_0X80,
                                  COMMAND_ID_REQUEST_0X10_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  MESSAGE_NAK,
                                  MESSAGE_ACK,
                                  X10_COMMAND_ON,
                                  X10_COMMAND_OFF)
from insteonplm.address import Address
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.x10received import X10Received

from .mockConnection import MockConnection, wait_for_plm_command
from .mockCallbacks import MockCallbacks

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('insteonplm')
_INSTEON_LOGGER.setLevel(logging.DEBUG)
SEND_MSG_WAIT = 1.1
SEND_MSG_ACKNAK_WAIT = .2
DIRECT_ACK_WAIT_TIMEOUT = 3.1
RECV_MSG_WAIT = .1


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
async def do_plm(loop):
    """Asyncio coroutine to test the PLM."""
    _LOGGER.info('Connecting to Insteon PLM')

    # pylint: disable=not-an-iterable
    conn = await MockConnection.create(loop=loop)

    def async_insteonplm_light_callback(device):
        """Log that our new device callback worked."""
        _LOGGER.warning('New Device: %s %02x %02x %s, %s', device.id,
                        device.cat, device.subcat, device.description,
                        device.model)

    # pylint: disable=unused-variable
    def async_light_on_level_callback(device_id, state, value):
        """Callback to catch changes to light value."""
        _LOGGER.info('Device %s state %s value is changed to %02x',
                     device_id, state, value)

    conn.protocol.add_device_callback(async_insteonplm_light_callback)

    plm = conn.protocol
    plm.connection_made(conn.transport)

    _LOGGER.info('Replying with IM Info')
    _LOGGER.info('_____________________')
    cmd_sent = await wait_for_plm_command(plm, GetImInfo(), loop)
    if not cmd_sent:
        assert False
    msg = insteonplm.messages.getIMInfo.GetImInfo(address='1a2b3c', cat=0x03,
                                                  subcat=0x20, firmware=0x00,
                                                  acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    assert plm.address == Address('1a2b3c')
    assert plm.cat == 0x03
    assert plm.subcat == 0x20
    assert plm.product_key == 0x00

    _LOGGER.info('Replying with an All-Link Record')
    _LOGGER.info('________________________________')
    cmd_sent = await wait_for_plm_command(plm, GetFirstAllLinkRecord(), loop)
    if not cmd_sent:
        assert False
    msg = GetFirstAllLinkRecord(MESSAGE_ACK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)

    msg = AllLinkRecordResponse(
        flags=0x00, group=0x01, address='4d5e6f',
        linkdata1=0x01, linkdata2=0x0b, linkdata3=0x000050)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT)

    _LOGGER.info('Replying with Last All-Link Record')
    _LOGGER.info('__________________________________')
    cmd_sent = await wait_for_plm_command(plm, GetNextAllLinkRecord(), loop)
    if not cmd_sent:
        assert False
    msg = GetNextAllLinkRecord(MESSAGE_NAK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    msg = GetNextAllLinkRecord(MESSAGE_NAK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    msg = GetNextAllLinkRecord(MESSAGE_NAK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    msg = GetNextAllLinkRecord(MESSAGE_NAK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)

    _LOGGER.info('Replying with Device Info Record')
    _LOGGER.info('________________________________')
    msg = StandardSend('4d5e6f', COMMAND_ID_REQUEST_0X10_0X00)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False
    msg = StandardSend('4d5e6f', COMMAND_ID_REQUEST_0X10_0X00,
                       acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    msg = StandardReceive(
        address='4d5e6f', target='010b00',
        commandtuple={'cmd1': 0x01, 'cmd2': 0x00},
        flags=MESSAGE_FLAG_BROADCAST_0X80)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    for addr in plm.devices:
        _LOGGER.info('Device: %s', addr)

    _LOGGER.info('Replying with Device Status Record')
    _LOGGER.info('__________________________________')
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                       acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)

    msg = insteonplm.messages.standardReceive.StandardReceive(
        address='4d5e6f', target='1a2b3c',
        commandtuple={'cmd1': 0x17, 'cmd2': 0xaa},
        flags=0x20)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)

    assert plm.devices['4d5e6f'].states[0x01].value == 0xaa

    _LOGGER.info('Testing device message ACK/NAK handling')
    _LOGGER.info('_______________________________________')
    plm.devices['4d5e6f'].states[0x01].on()
    plm.devices['4d5e6f'].states[0x01].off()
    plm.devices['4d5e6f'].states[0x01].set_level(0xbb)

    # Test that the first ON command is sent
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # ACK the ON command
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_ON_0X11_NONE,
                       cmd2=0xff, flags=0x00, acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)

    # Let the Direct ACK timeout expire
    await asyncio.sleep(DIRECT_ACK_WAIT_TIMEOUT, loop=loop)

    # Test that the Off command has now sent
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # NAK the OFF command and test that the OFF command is resent
    plm.transport.lastmessage = ''
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00,
                       acknak=MESSAGE_NAK)
    plm.data_received(msg.bytes)

    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # Let the ACK/NAK timeout expire and test that the OFF command is resent
    plm.transport.lastmessage = ''
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # ACK the OFF command and let the Direct ACK message expire
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00,
                       acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)

    # Test that the second SET_LEVEL command is sent
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xbb)
    cmd_sent = await wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    await plm.close()
    _LOGGER.error('PLM closed in test_plm')
    await asyncio.sleep(0, loop=loop)
    open_tasks = asyncio.Task.all_tasks(loop=loop)
    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)


# pylint: disable=too-many-statements
async def do_plm_x10(loop):
    """Asyncio coroutine to test the PLM X10 message handling."""
    _LOGGER.info('Connecting to Insteon PLM')

    # pylint: disable=not-an-iterable
    conn = await MockConnection.create(loop=loop)

    cb = MockCallbacks()

    plm = conn.protocol
    plm.connection_made(conn.transport)

    _LOGGER.info('Replying with IM Info')
    _LOGGER.info('_____________________')
    cmd_sent = await wait_for_plm_command(plm, GetImInfo(), loop)
    if not cmd_sent:
        assert False
    msg = insteonplm.messages.getIMInfo.GetImInfo(address='1a2b3c', cat=0x03,
                                                  subcat=0x20, firmware=0x00,
                                                  acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)

    _LOGGER.info('Replying with an All-Link Record NAK')
    _LOGGER.info('____________________________________')
    cmd_sent = await wait_for_plm_command(plm, GetFirstAllLinkRecord(), loop)
    if not cmd_sent:
        assert False
    msg = GetFirstAllLinkRecord(MESSAGE_NAK)
    plm.data_received(msg.bytes)
    await asyncio.sleep(RECV_MSG_WAIT, loop=loop)

    _LOGGER.info('Add X10 device and receive messages')
    _LOGGER.info('____________________________________')
    housecode = 'C'
    unitcode = 9
    plm.add_x10_device(housecode, unitcode, 'OnOff')
    x10_id = Address.x10(housecode, unitcode).id
    plm.devices[x10_id].states[0x01].register_updates(cb.callbackmethod1)

    msg = X10Received.unit_code_msg(housecode, unitcode)
    plm.data_received(msg.bytes)
    await asyncio.sleep(.1, loop=loop)
    msg = X10Received.command_msg(housecode, X10_COMMAND_ON)
    plm.data_received(msg.bytes)
    await asyncio.sleep(.1, loop=loop)
    assert cb.callbackvalue1 == 0xff

    msg = X10Received.unit_code_msg(housecode, unitcode)
    plm.data_received(msg.bytes)
    await asyncio.sleep(.1, loop=loop)
    msg = X10Received.command_msg(housecode, X10_COMMAND_OFF)
    plm.data_received(msg.bytes)
    await asyncio.sleep(.1, loop=loop)
    assert cb.callbackvalue1 == 0x00

    await plm.close()
    _LOGGER.error('PLM closed in test_x10')
    await asyncio.sleep(0, loop=loop)
    open_tasks = asyncio.Task.all_tasks(loop=loop)
    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)


def test_plm():
    """Main test for the PLM."""
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_plm(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_plm_x10():
    """Test X10 message handling."""
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_plm_x10(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGER.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGER.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)
