"""Mock Connection for the PLM."""

import asyncio
import binascii
import logging

import async_timeout

_LOGGER = logging.getLogger(__name__)


async def wait_for_plm_command(plm, cmd, loop):
    """Wait for a command to hit the PLM."""
    try:
        with async_timeout.timeout(10, loop=loop):
            while not plm.transport.lastmessage == cmd.hex:
                await asyncio.sleep(.1, loop=loop)
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
    async def create(cls, loop=None):
        """Create the MockConnection."""
        from insteonplm.plm import PLM
        conn = cls()
        conn.loop = loop or asyncio.get_event_loop()
        conn.protocol = PLM(
            connection_lost_callback=None,
            loop=conn.loop)

        # pylint: disable=too-few-public-methods
        class Serial:
            """Mock serial class within Connection class."""

            def __init__(self):
                """Init the mock Serial class."""
                self.write_timeout = 0
                self.timeout = 0

        class Transport:
            """Mock transport class within Connection class."""

            def __init__(self):
                """Init the mock Transport class."""
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

            @staticmethod
            def is_closing():
                """Return if the Mock Connection is closing."""
                return False

        conn.transport = Transport()
        return conn
