"""Test the INSTEON PLM device."""
import asyncio
import logging
import binascii

import insteonplm
from insteonplm.constants import MESSAGE_FLAG_BROADCAST_0X80
from insteonplm.plm import PLM
from insteonplm.address import Address


# pylint: disable=too-few-public-methods
class MockConnection():
    """A mock up of the Connection class."""

    def __init__(self):
        """Instantiate the Connection object."""
        self.log = logging.getLogger(__name__)
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
                self.log = logging.getLogger(__name__)
                self.write_timeout = 0
                self.timeout = 0

        class Transport:
            """Mock transport class within Connection class."""

            def __init__(self):
                """Initialize the mock Transport class."""
                self.log = logging.getLogger(__name__)
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
                self.lastmessage = data
                self.log.info('Message sent: %s',
                              binascii.hexlify(self.lastmessage))

        conn.transport = Transport()
        return conn


@asyncio.coroutine
def do_plm(loop, log, devicelist):
    """Asyncio coroutine to test the PLM."""
    log.info('Connecting to Insteon PLM')

    # pylint: disable=not-an-iterable
    conn = yield from MockConnection.create(loop=loop)

    def async_insteonplm_light_callback(device):
        """Log that our new device callback worked."""
        log.info('New Device: %s %02x %02x %s, %s', device.id, device.cat,
                 device.subcat, device.description, device.model)

    def async_light_on_level_callback(device_id, state, value):
        """Callback to catch changes to light value."""
        log.info('Device %s state %s value is changed to %02x',
                 device_id, state, value)

    conn.protocol.add_device_callback(async_insteonplm_light_callback)

    plm = conn.protocol
    plm.connection_made(conn.transport)

    log.info('Replying with IM Info')
    log.info('_____________________')
    msg = insteonplm.messages.getIMInfo.GetImInfo(address='1a2b3c', cat=0x03,
                                                  subcat=0x20, firmware=0x00,
                                                  acknak=0x06)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(.1)
    assert plm.address == Address('1a2b3c')
    assert plm.cat == 0x03
    assert plm.subcat == 0x20
    assert plm.product_key == 0x00

    log.info('Replying with an All-Link Record')
    log.info('________________________________')
    msg = insteonplm.messages.allLinkRecordResponse.AllLinkRecordResponse(
        flags=0x00, group=0x01, address='4d5e6f',
        linkdata1=0x01, linkdata2=0x0b, linkdata3=0x000050)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(.1)

    log.info('Replying with Last All-Link Record')
    log.info('__________________________________')
    msg = insteonplm.messages.getNextAllLinkRecord.GetNextAllLinkRecord(0x15)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(.1)

    log.info('Replying with Device Info Record')
    log.info('________________________________')
    msg = insteonplm.messages.standardReceive.StandardReceive(
        address='4d5e6f', target='010b00',
        commandtuple={'cmd1': 0x01, 'cmd2': 0x00},
        flags=MESSAGE_FLAG_BROADCAST_0X80)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(.1)
    for addr in plm.devices:
        log.info('Device: ', addr)

    log.info('Replying with Device Status Record')
    log.info('__________________________________')
    plm.devices['4d5e6f'].states[0x01].async_refresh_state()
    msg = insteonplm.messages.standardSend.StandardSend(
        address='4d5e6f', commandtuple={'cmd1': 0x19, 'cmd2': 0x00},
        flags=0x00, acknak=0x06)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(.1)
    msg = insteonplm.messages.standardReceive.StandardReceive(
        address='4d5e6f', target='1a2b3c',
        commandtuple={'cmd1': 0x17, 'cmd2': 0xff},
        flags=0x20)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(.1)

    assert plm.devices['4d5e6f'].states[0x01].value == 0xff

    # Too much backlog of messages at this point to be clear on
    # what message will be
    # returned.

    # log.info('Replying with NAK Record')
    # log.info('__________________________________')
    # msg = insteonplm.messages.standardSend.StandardSend(
    #     address='4d5e6f', commandtuple={'cmd1': 0x011,'cmd2': 0xff},
    #     flags=0x00, acknak=0x15)
    # plm.data_received(msg.bytes)
    # yield from asyncio.sleep(3)
    # assert plm.transport.lastmessage == msg.bytes[:-1]


def test_plm():
    """Main test for the PLM."""
    devicelist = (
        {
            "address": "3c4fc5",
            "cat": 0x01,
            "subcat": 0x0b,
            "product_key": 0x000050
        },
        {
            "address": "43af9b",
            "cat": 0x02,
            "subcat": 0x1a,
            "product_key": 0x00
        }
    )

    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_plm(loop, log, devicelist))
