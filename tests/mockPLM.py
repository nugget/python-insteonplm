"""Mock PLM class for testing devices."""
import logging
from insteonplm.messagecallback import MessageCallback
from insteonplm.linkedDevices import LinkedDevices


class MockPLM(object):
    """Mock PLM class for testing devices."""

    def __init__(self, loop=None):
        """Initialize the MockPLM class."""
        self.log = logging.getLogger()
        self.sentmessage = ''
        self._message_callbacks = MessageCallback()
        self.loop = loop
        self.devices = LinkedDevices()

    @property
    def message_callbacks(self):
        """Return the message callback list."""
        return self._message_callbacks

    def send_msg(self, msg):
        """Send a message mock routine."""
        self.sentmessage = msg.hex

    def message_received(self, msg):
        """Fake a message being received by the PLM."""
        if hasattr(msg, 'address'):
            device = self.devices[msg.address.id]
            if device:
                device.receive_message(msg)
            else:
                self.log.info('Received message for unknown device %s',
                                msg.address)
        for callback in (
                self._message_callbacks.get_callbacks_from_message(msg)):
            callback(msg)
