"""Mock Connection for the PLM."""

import asyncio
import binascii
import logging


_LOGGER = logging.getLogger()


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
        from insteonplm.plm import PLM
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