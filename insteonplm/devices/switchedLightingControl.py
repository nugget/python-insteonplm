from .devicebase import DeviceBase
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *

class SwitchedLightingControl(DeviceBase):
    """Switched Lighting Control Device Class 0x02"""

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        DeviceBase.__init__(self, plm, address, cat, subcat, product_key, description, model, groupbutton)
        self.lightOnLevel = StateChangeSignal()

        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, self._light_on_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_OFF_0X13_0X00, self._light_off_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_ON_0X11_NONE, self._light_on_command_received, MESSAGE_ACK)
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_OFF_0X13_0X00, self._light_off_command_received, MESSAGE_ACK)

    def light_on(self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_0X11_NONE, 0xff)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_ON_0X11_NONE, 0xff, **userdata)

    def light_on_fast (self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_FAST_0X12_NONE, oxff)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_ON_FAST_0X12_NONE, 0xff, **userdata)

    def light_off(self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_0X13_0X00)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_OFF_0X13_0X00, **userdata)

    def light_off_fast(self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_FAST_0X14_0X00)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_OFF_FAST_0X14_0X00, **userdata)

    def light_status_request (self):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, **userdata)

    def get_operating_flags(self):
        return NotImplemented

    def set_operating_flags(self):
        return NotImplemented

    def light_manually_turned_off(self):
        return NotImplemented

    def light_manually_turned_On(self):
        return NotImplemented

    def _light_on_command_received(self, msg):
        # Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Light On
        # Also handles Standard or Extended (0x62) Lights On (0x11) ACK/NAK
        # When any of these messages are received
        if msg.isack:
            self.lightOnLevel.update(msg.address.hex, msg.cmd2)

    def _light_off_command_received(self, msg):
        self.lightOnLevel.update(msg.address.hex, 0)

class SwitchedLightingControl_2663_222(SwitchedLightingControl):
    def create(cls, plm, address, cat, subcat, product_key = None, description = None, model = None, groupbutton = 0x01):
        devices = []
        devices[0] = super().create(plm, address, cat, subcat, product_key, description, model, groupbutton)
        devices[1] = super().create(plm, address, cat, subcat, product_key, description, model, 0x02)
        self.log.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WE GOT HERE !!!!!!!!!!!!!!!!!!!!!!!")
        return devices