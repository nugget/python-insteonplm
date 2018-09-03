"""Mock PLM class for testing devices."""
import logging
from insteonplm.messagecallback import MessageCallback
from insteonplm.linkedDevices import LinkedDevices

_LOGGER = logging.getLogger(__name__)


class MockPLM():
    """Mock PLM class for testing devices."""

    def __init__(self, loop=None):
        """Init the MockPLM class."""
        self.sentmessage = ''
        self._message_callbacks = MessageCallback()
        self.loop = loop
        self.devices = LinkedDevices()

    @property
    def message_callbacks(self):
        """Return the message callback list."""
        return self._message_callbacks

    # pylint: disable=unused-argument
    def send_msg(self, msg, wait_nak=True, wait_timeout=2):
        """Send a message mock routine."""
        self.sentmessage = msg.hex

    def message_received(self, msg):
        """Fake a message being received by the PLM."""
        if hasattr(msg, 'address'):
            device = self.devices[msg.address.id]
            if device:
                device.receive_message(msg)
            else:
                _LOGGER.info('Received message for unknown device %s',
                             msg.address)
        for callback in (
                self._message_callbacks.get_callbacks_from_message(msg)):
            callback(msg)

    # pylint: disable=unused-argument
    def start_all_linking(self, linkcode, group):
        """Fake start all linking."""
        self.sentmessage = b'02112233445566'
