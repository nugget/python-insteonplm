"""Mock callback module to support device and state testing."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
# pylint: disable=too-many-instance-attributes
class MockCallbacks():
    """Mock callback class to support device and state testing."""

    def __init__(self):
        """Init the MockCallbacks Class."""
        self.callbackvalue1 = None
        self.callbackvalue2 = None
        self.callbackvalue3 = None
        self.callbackvalue4 = None
        self.callbackvalue5 = None
        self.callbackvalue6 = None
        self.callbackvalue7 = None
        self.callbackvalue8 = None
        self.callbackvalue9 = None

    def callbackmethod1(self, addr, state, value):
        """Receive notice of callback method 1."""
        self._report_callback(1, addr, state, value)
        self.callbackvalue1 = value

    def callbackmethod2(self, addr, state, value):
        """Receive notice of callback method 2."""
        self._report_callback(2, addr, state, value)
        self.callbackvalue2 = value

    def callbackmethod3(self, addr, state, value):
        """Receive notice of callback method 3."""
        self._report_callback(3, addr, state, value)
        self.callbackvalue3 = value

    def callbackmethod4(self, addr, state, value):
        """Receive notice of callback method 5."""
        self._report_callback(4, addr, state, value)
        self.callbackvalue4 = value

    def callbackmethod5(self, addr, state, value):
        """Receive notice of callback method 5."""
        self._report_callback(5, addr, state, value)
        self.callbackvalue5 = value

    def callbackmethod6(self, addr, state, value):
        """Receive notice of callback method 6."""
        self._report_callback(6, addr, state, value)
        self.callbackvalue6 = value

    def callbackmethod7(self, addr, state, value):
        """Receive notice of callback method 7."""
        self._report_callback(7, addr, state, value)
        self.callbackvalue7 = value

    def callbackmethod8(self, addr, state, value):
        """Receive notice of callback method 8."""
        self._report_callback(8, addr, state, value)
        self.callbackvalue8 = value

    def callbackmethod9(self, addr, state, value):
        """Receive notice of callback method 9."""
        _LOGGER.debug('Called method 9 callback')
        self.callbackvalue9 = value

    @staticmethod
    def _report_callback(callback, addr, state, value):
        _LOGGER.debug('Called method %d for address %s group %s value %s',
                      callback, addr, state, value)
