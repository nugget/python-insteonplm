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
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_0X11_NONE, 0xff)

    def light_on_fast (self):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_FAST_0X12_NONE, oxff)

    def light_off(self):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_0X13_0X00)

    def light_off_fast(self):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_OFF_FAST_0X14_0X00)

    def light_status_request (self):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)

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
