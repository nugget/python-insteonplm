from insteonplm.states.stateBase import StateBase

class StateList(object):
    """Internal class used to hold a list of device states."""
    def __init__(self):
        self._stateList = {}

    def __len__(self):
        """Get the number of states in the StateList"""
        return len(self._stateList)

    def __iter__(self):
        """Iterate through each state in the StateList"""
        for state in self._stateList:
            yield state

    def __getitem__(self, group):
        """Get a state from the StateList"""
        return self._stateList.get(group, None)

    def __setitem__(self, group, state):
        """Add or update a state in the StateList"""
        if not isinstance(state, StateBase):
            return ValueError

        self._stateList[group] = state

    def __repr__(self):
        """Juman representation of a state in the StateList"""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def add(self, plm, device, stateType, stateName, group, defaultValue=None):
        """Add a state to the StateList"""
        self._stateList[group] = stateType(plm, device, stateName, group, defaultValue=defaultValue)
        