"""Mock callback module to support device and state testing."""
import logging


class MockCallbacks(object):
    """Mock callback class to support device and state testing."""

    def __init__(self):
        """Initialize the MockCallbacks Class."""
        self.log = logging.getLogger(__name__)
        self.callbackvalue1 = None
        self.callbackvalue2 = None
        self.callbackvalue3 = None
        self.callbackvalue4 = None
        self.callbackvalue5 = None
        self.callbackvalue6 = None
        self.callbackvalue7 = None
        self.callbackvalue8 = None
        self.callbackvalue9 = None

    def callbackmethod1(self, id, state, value):
        """Callback method 1."""
        self.log.debug('Called method 1 callback')
        self.callbackvalue1 = value

    def callbackmethod2(self, id, state, value):
        """Callback method 2."""
        self.log.debug('Called method 2 callback')
        self.callbackvalue2 = value

    def callbackmethod3(self, id, state, value):
        """Callback method 3."""
        self.log.debug('Called method 3 callback')
        self.callbackvalue3 = value

    def callbackmethod4(self, id, state, value):
        """Callback method 5."""
        self.log.debug('Called method 4 callback')
        self.callbackvalue4 = value

    def callbackmethod5(self, id, state, value):
        """Callback method 5."""
        self.log.debug('Called method 5 callback')
        self.callbackvalue5 = value

    def callbackmethod6(self, id, state, value):
        """Callback method 6."""
        self.log.debug('Called method 6 callback')
        self.callbackvalue6 = value

    def callbackmethod7(self, id, state, value):
        """Callback method 7."""
        self.log.debug('Called method 7 callback')
        self.callbackvalue7 = value

    def callbackmethod8(self, id, state, value):
        """Callback method 8."""
        self.log.debug('Called method 8 callback')
        self.callbackvalue8 = value

    def callbackmethod9(self, id, state, value):
        """Callback method 9."""
        self.log.debug('Called method 9 callback')
        self.callbackvalue9 = value
