"""INSTEON State Entities."""
import logging
from insteonplm.address import Address


class State(object):
    """INSTEON device state base class.

    Base class used by Insteon devices to hold a device state such as "Light On
    Level", "Temperature" or "Fan Mode".

    The class is defined with the following options:
        stateName: Required text name of the state, such as "LightOnLevel".
                   This value is returned when an async request is made to
                   update the state value.
        updatemethod: Required callback method where callback is defined as:
                      callback(self)
        defaultvalue: Optional parameter to set the default value of the state.

    The following public properties are available:

    stateName - Text name for the device state.
    value - Cached value of the state value. If this value is None, referencing
            this property forces an udpate by calling async_refresh_state

    The following public methods are available:

    register_updates(self, callback) - Used to monitor changes to the state of
        the device. This method registers a callback for notifiction of state
        changes eg.:
            - device.state[0].register_updates(callback)
        where callback defined as:
            - callback(self, device_id, stateName, state_value)

    async_refresh_state(self) - called by a device or a subscriber to force an
        update to the state value
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Initialzie tthe State Class."""
        self.log = logging.getLogger(__name__)

        self._address = Address(address)
        self._observer_callbacks = []
        self._stateName = statename
        self._group = group
        self._value = defaultvalue

        self._updatemethod = None
        self._send_method = send_message_method
        self._message_callbacks = message_callbacks

    @property
    def value(self):
        """Return the value of the state."""
        if self._value is None:
            self.async_refresh_state()
        return self._value

    @property
    def name(self):
        """Return the name of the state."""
        return self._stateName

    @property
    def address(self):
        """Return the device address."""
        return self._address

    @property
    def group(self):
        """Return the link group of the state."""
        return self._group

    def async_refresh_state(self):
        """Call the update method to request current state value."""
        if self._updatemethod is not None:
            self._updatemethod()

    def register_updates(self, callback):
        """Register a callback to notify a listener of state changes."""
        self.log.debug("Registered callback for state: %s", self._stateName)
        self._observer_callbacks.append(callback)

    def _update_subscribers(self, val):
        """Save state value and notify listeners of the change."""
        self._value = val
        for callback in self._observer_callbacks:
            callback(self._address, self._group, val)
