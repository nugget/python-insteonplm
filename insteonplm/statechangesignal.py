class StateChangeSignal(object):
    """
    Class used by Insteon devices to hold a device state such as "Light On Level", "Temperature" or "Fan Mode".
    The class is defined with the following options:
        statename: Required text name of the state, such as "LightOnLevel". This value is returned when an async
                   request is made to update the state value.
        updatemethod: Required callback method where callback is defined as:
                      callback(self)
        defaultvalue: Optional parameter to set the default value of the state.

    The following public properties are available:

    statename - Text name for the device state.
    value - Cached value of the state value. If this value is None, referencing this property forces an udpate
            by calling async_refresh_state

    The following public methods are available:
    connect(self, handler) - Used to monitor changes to the state of the device. 
                             This method registers a callback for notifiction of state changes eg.:
                                - device.lightOnLevel.connect(callback)
    
    update(self, *args) - used by the device to update subscribers of a state change

    async_refresh_state(self) - called by a device or a subscriber to force an update to the state value

    where callback defined as:
        - callback(self, device_id, state, state_value)

    """
    def __init__(self, statename, updatemethod, defaultvalue=None):
        self._handlers = []
        self._stateName = statename
        self._value = defaultvalue
        self._updatemethod = updatemethod

    def connect(self, handler):
        self._handlers.append(handler)

    def update(self, *args):
        for handler in self._handlers:
            handler(*args)

    @property
    def value(self):
        if self._value == None:
            self.async_refresh_state()
        return self._value

    @property
    def statename(self):
        return self._stateName

    def async_refresh_state(self):
        self._updatemethod()