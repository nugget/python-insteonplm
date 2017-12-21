from .devicebase import DeviceBase
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *

class DimmableLightingControl(DeviceBase):
    """Dimmable Lighting Controller 0x01
    
    INSTEON On/Off switch device class. Available device control options are:
        - light_on(onlevel=0xff)
        - light_on_fast(onlevel=0xff)
        - light_off()
        - light_off_fast()

    To monitor changes to the state of the device subscribe to the state monitor:
         - lightOnLevel.connect(callback)  (state='LightOnLevel')

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        DeviceBase.__init__(self, plm, address, cat, subcat, product_key, description, model, groupbutton)

        # Setting the default value of the light to 0 (i.e. Off)
        self.lightOnLevel = StateChangeSignal('LightOnLevel', self.light_status_request, 0x00)

        self._nextCommandIsStatus = False

        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_ON_0X11_NONE, self._light_on_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50, COMMAND_LIGHT_OFF_0X13_0X00, self._light_off_command_received)
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_ON_0X11_NONE, self._light_on_command_received, MESSAGE_ACK)
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_OFF_0X13_0X00, self._light_off_command_received, MESSAGE_ACK)
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, self._light_status_request_ack, MESSAGE_ACK)

    def light_on(self, onlevel=0xff):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_0X11_NONE, onlevel)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_ON_0X11_NONE, onlevel, **userdata)

    def light_on_fast(self, onlevel=0xff):
        if self._groupbutton == 0x01:
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_ON_FAST_0X12_NONE, onlevel)
        else:
            userdata = {'d1':self._groupbutton}
            self._plm.send_extended(self._address.hex, COMMAND_LIGHT_ON_FAST_0X12_NONE, onlevel, **userdata)

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

    def light_status_request(self):
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)

    def receive_message(self, msg):
        self.log.debug('Next command is status: %r', self._nextCommandIsStatus)
        if self._nextCommandIsStatus:
            self._status_update_received(msg)
        else:
            super().receive_message(msg)

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
        # Also handles Standard or Extended (0x62) Lights On (0x11) ACK
        # When any of these messages are received any state listeners are updated with the 
        # current light on level (cmd2)
        self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, msg.cmd2)

    def _light_off_command_received(self, msg):
        self.lightOnLevel.update(msg.id, self.lightOnLevel._stateName, 0)

    def _light_status_request_ack(self, msg):
        self.log.debug('Starting _light_status_request')
        self._nextCommandIsStatus = True
        self.log.debug('Ending _light_status_request')

    def _status_update_received(self, msg):
        self.log.debug('Starting _status_update_received')
        self._nextCommandIsStatus = False
        self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, msg.cmd2)
        self.log.debug('Ending _status_update_received')