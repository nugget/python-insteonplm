import logging

class StateBase(object):
    """
    Base class used by Insteon devices to hold a device state such as "Light On Level", "Temperature" or "Fan Mode".
    The class is defined with the following options:
        stateName: Required text name of the state, such as "LightOnLevel". This value is returned when an async
                   request is made to update the state value.
        updatemethod: Required callback method where callback is defined as:
                      callback(self)
        defaultvalue: Optional parameter to set the default value of the state.

    The following public properties are available:

    stateName - Text name for the device state.
    value - Cached value of the state value. If this value is None, referencing this property forces an udpate
            by calling async_refresh_state

    The following public methods are available:
    connect(self, handler) - Used to monitor changes to the state of the device. 
                             This method registers a callback for notifiction of state changes eg.:
                                - device.lightOnLevel.connect(callback)
    
    update(self, *args) - used by the device to update subscribers of a state change

    async_refresh_state(self) - called by a device or a subscriber to force an update to the state value

    where callback defined as:
        - callback(self, device_id, stateName, state_value)

    """
    def __init__(self, plm, device, statename, group, updatemethod=None, defaultvalue=None):
        self._plm = plm
        self._device = device
        self._handlers = []
        self._stateName = statename
        self._group = group
        self._value = defaultvalue
        self._updatemethod = updatemethod
        
        self._log = logging.getLogger(__name__)

    def connect(self, handler):
        self._log.debug("Registered callback for state: %s", self._stateName)
        self._handlers.append(handler)

    def update(self, val):
        """Save value to state.value property and notify listeners of the change"""
        self._value = val
        for handler in self._handlers:
            handler(deviceid, self._stateName, val)

    @property
    def value(self):
        if self._value == None:
            self.async_refresh_state()
        return self._value

    @property
    def stateName(self):
        return self._stateName

    def async_refresh_state(self):
        if self._updatemethod is not None:
            self._updatemethod()