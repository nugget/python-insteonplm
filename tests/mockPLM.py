"""Mock PLM class for testing devices."""
from insteonplm.messagecallback import MessageCallback


class MockPLM(object):
    """Mock PLM class for testing devices."""

    def __init__(self, loop=None):
        """Initialize the MockPLM class."""
        self.sentmessage = ''
        self._message_callbacks = MessageCallback()
        self.loop = loop

    @property
    def message_callbacks(self):
        """Return the message callback list."""
        return self._message_callbacks

    def send_msg(self, msg):
        """Send a message mock routine."""
        self.sentmessage = msg.hex

    def message_received(self, msg):
        """Fake a message being received by the PLM."""
        for callback in (
                self._message_callbacks.get_callbacks_from_message(msg)):
            callback(msg)
