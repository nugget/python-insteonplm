"""Test the INSTEON PLM device."""
import asyncio
import async_timeout
import logging
import binascii

import insteonplm
from insteonplm.constants import (COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_OFF_0X13_0X00,
                                  MESSAGE_FLAG_BROADCAST_0X80,
                                  COMMAND_ID_REQUEST_0X10_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  MESSAGE_NAK,
                                  MESSAGE_ACK)
from insteonplm.plm import PLM
from insteonplm.address import Address
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse

_LOGGER = logging.getLogger()
SEND_MSG_WAIT = 1.1
SEND_MSG_ACKNAK_WAIT = .2
DIRECT_ACK_WAIT_TIMEOUT = 3.1
RECV_MSG_WAIT = .1


@asyncio.coroutine
def wait_for_plm_command(plm, cmd, loop):
    try:
        with async_timeout.timeout(10, loop=loop):
            while not plm.transport.lastmessage == cmd.hex:
                yield from asyncio.sleep(.1, loop=loop)
            _LOGGER.info('Expected message sent %s', cmd)
            return True
    except asyncio.TimeoutError:
        _LOGGER.error('Expected message not sent %s', cmd)
        return False


# pylint: disable=too-few-public-methods
class MockConnection():
    """A mock up of the Connection class."""

    def __init__(self):
        """Instantiate the Connection object."""
        self.loop = None
        self.protocol = None
        self.transport = None

    @classmethod
    @asyncio.coroutine
    def create(cls, loop=None):
        """Create a mock connection."""
        conn = cls()
        conn.loop = loop or asyncio.get_event_loop()
        conn.protocol = PLM(
            connection_lost_callback=None,
            loop=conn.loop)

        # pylint: disable=too-few-public-methods
        class Serial:
            """Mock serial class within Connection class."""

            def __init__(self):
                """Initialize the mock Serial class."""
                self.write_timeout = 0
                self.timeout = 0

        class Transport:
            """Mock transport class within Connection class."""

            def __init__(self):
                """Initialize the mock Transport class."""
                self.serial = Serial()
                self.lastmessage = None
                self._mock_buffer_size = 128

            def set_write_buffer_limits(self, num):
                """Mock set write buffer limits."""
                pass

            def get_write_buffer_size(self):
                """Mock get write buffer size."""
                return self._mock_buffer_size

            def write(self, data):
                """Mock write data to the Connection."""
                self.lastmessage = binascii.hexlify(data).decode()
                _LOGGER.info('Message sent: %s', self.lastmessage)

        conn.transport = Transport()
        return conn


@asyncio.coroutine
def do_plm(loop):
    """Asyncio coroutine to test the PLM."""
    _LOGGER.info('Connecting to Insteon PLM')

    # pylint: disable=not-an-iterable
    conn = yield from MockConnection.create(loop=loop)

    def async_insteonplm_light_callback(device):
        """Log that our new device callback worked."""
        _LOGGER.warn('New Device: %s %02x %02x %s, %s', device.id, device.cat,
                     device.subcat, device.description, device.model)

    def async_light_on_level_callback(device_id, state, value):
        """Callback to catch changes to light value."""
        _LOGGER.info('Device %s state %s value is changed to %02x',
                     device_id, state, value)

    conn.protocol.add_device_callback(async_insteonplm_light_callback)

    plm = conn.protocol
    plm.connection_made(conn.transport)

    _LOGGER.info('Replying with IM Info')
    _LOGGER.info('_____________________')
    cmd_sent = yield from wait_for_plm_command(plm, GetImInfo(), loop)
    if not cmd_sent:
        assert False
    msg = insteonplm.messages.getIMInfo.GetImInfo(address='1a2b3c', cat=0x03,
                                                  subcat=0x20, firmware=0x00,
                                                  acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)
    assert plm.address == Address('1a2b3c')
    assert plm.cat == 0x03
    assert plm.subcat == 0x20
    assert plm.product_key == 0x00

    _LOGGER.info('Replying with an All-Link Record')
    _LOGGER.info('________________________________')
    cmd_sent = yield from wait_for_plm_command(plm, GetFirstAllLinkRecord(),
                                               loop)
    if not cmd_sent:
        assert False
    msg = GetFirstAllLinkRecord(MESSAGE_ACK)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)

    msg = AllLinkRecordResponse(
        flags=0x00, group=0x01, address='4d5e6f',
        linkdata1=0x01, linkdata2=0x0b, linkdata3=0x000050)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)

    _LOGGER.info('Replying with Last All-Link Record')
    _LOGGER.info('__________________________________')
    cmd_sent = yield from wait_for_plm_command(plm, GetNextAllLinkRecord(),
                                               loop)
    if not cmd_sent:
        assert False
    msg = GetNextAllLinkRecord(MESSAGE_NAK)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)

    _LOGGER.info('Replying with Device Info Record')
    _LOGGER.info('________________________________')
    msg = StandardSend('4d5e6f', COMMAND_ID_REQUEST_0X10_0X00)
    cmd_sent = wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False
    msg = StandardSend('4d5e6f', COMMAND_ID_REQUEST_0X10_0X00,
                       acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT, loop=loop)
    msg = StandardReceive(
        address='4d5e6f', target='010b00',
        commandtuple={'cmd1': 0x01, 'cmd2': 0x00},
        flags=MESSAGE_FLAG_BROADCAST_0X80)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)
    for addr in plm.devices:
        _LOGGER.info('Device: %s', addr)

    _LOGGER.info('Replying with Device Status Record')
    _LOGGER.info('__________________________________')
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
    cmd_sent = yield from wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                       acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)

    msg = insteonplm.messages.standardReceive.StandardReceive(
        address='4d5e6f', target='1a2b3c',
        commandtuple={'cmd1': 0x17, 'cmd2': 0xaa},
        flags=0x20)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(RECV_MSG_WAIT)

    assert plm.devices['4d5e6f'].states[0x01].value == 0xaa

    _LOGGER.info('Testing device message ACK/NAK handling')
    _LOGGER.info('_______________________________________')
    plm.devices['4d5e6f'].states[0x01].on()
    plm.devices['4d5e6f'].states[0x01].off()
    plm.devices['4d5e6f'].states[0x01].set_level(0xbb)

    # Test that the first ON command is sent
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
    cmd_sent = yield from wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # ACK the ON command
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_ON_0X11_NONE,
                       cmd2=0xff, flags=0x00, acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)

    # Let the Direct ACK timeout expire
    yield from asyncio.sleep(DIRECT_ACK_WAIT_TIMEOUT)

    # Test that the Off command has now sent
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00)
    cmd_sent = yield from wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # NAK the OFF command and test that the OFF command is resent
    plm.transport.lastmessage = ''
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00,
                       acknak=MESSAGE_NAK)
    plm.data_received(msg.bytes)

    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00)
    cmd_sent = yield from wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # Let the ACK/NAK timeout expire and test that the OFF command is resent
    plm.transport.lastmessage = ''
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00)
    cmd_sent = yield from wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False

    # ACK the OFF command and let the Direct ACK message expire
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_OFF_0X13_0X00,
                       acknak=MESSAGE_ACK)
    plm.data_received(msg.bytes)

    # Test that the second SET_LEVEL command is sent
    msg = StandardSend('4d5e6f', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xbb)
    cmd_sent = yield from wait_for_plm_command(plm, msg, loop)
    if not cmd_sent:
        assert False


def test_plm():
    """Main test for the PLM."""
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_plm(loop))
