from .state import State
from insteonplm.constants import *

class OnOffSwitch(State):
    """Device state representing an On/Off switch that is controllable.

    Available methods are:
    on()
    off()
    async_refresh_state()
    connect()
    update()
    """

    def __init__(self, plm, device, statename, group, defaultvalue=None):
        State.__init__(self, plm, device, statename, group, self._update, defaultvalue)

    def on(self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_0X11_NONE, onlevel)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_ON_0X11_NONE, onlevel, **userdata)

    def off(self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_0X13_0X00)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_OFF_0X13_0X00, **userdata)

    def _update(self):
        


