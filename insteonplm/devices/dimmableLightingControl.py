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
        self.lightOnLevel = StateChangeSignal(self.id, 'LightOnLevel', self.light_status_request, 0x00)

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
        self.log.debug('Starting DimmableLightingControl.receive_message')
        self.log.debug('Next command is status: %r', self._nextCommandIsStatus)
        if self._nextCommandIsStatus:
            self._status_update_received(msg)
        else:
            super().receive_message(msg)
        self.log.debug('Ending DimmableLightingControl.receive_message')

    def get_operating_flags(self):
        return NotImplemented

    def set_operating_flags(self):
        return NotImplemented

    def light_manually_turned_off(self):
        return NotImplemented

    def light_manually_turned_On(self):
        return NotImplemented

    def _light_on_command_received(self, msg):
        self.log.debug('Starting _light_on_command_received')
        # Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Light On
        # Also handles Standard or Extended (0x62) Lights On (0x11) ACK
        # When any of these messages are received any state listeners are updated with the 
        # current light on level (cmd2).
        # Some times the onlevel comes in as cmd2:0x00. We assume this to be 0xff
        if msg.cmd2 == 0x00:
            onlevel = 0xff
        else:
            onlevel = msg.cmd2

        if msg.code == MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51 or \
          (msg.code == MESSAGE_SEND_STANDARD_MESSAGE_0X62 and msg.isextendedflag):
            group = msg.userdata[0]
            device = self._plm.devices[self._get_device_id(group)]
            device.lightOnLevel.value = onlevel
        else:
            self.lightOnLevel.value = onlevel
        self.log.debug('Ending _light_on_command_received')

    def _light_off_command_received(self, msg):
        self.log.debug('Starting _light_off_command_received')
        if msg.code == MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51 or \
          (msg.code == MESSAGE_SEND_STANDARD_MESSAGE_0X62 and msg.isextendedflag):
            group = msg.userdata[0]
            device = self._plm.devices[self._get_device_id(group)]
            device.lightOnLevel.value = 0x00
        else:
            self.lightOnLevel.value = 0x00
        self.log.debug('Ending _light_off_command_received')

    def _light_status_request_ack(self, msg):
        self.log.debug('Starting _light_status_request_ack')
        self._nextCommandIsStatus = True
        self.log.debug('Ending _light_status_request_ack')

    def _status_update_received(self, msg):
        self.log.debug('Starting _status_update_received')
        self._nextCommandIsStatus = False
        self.lightOnLevel.value = msg.cmd2
        self.log.debug('Ending _status_update_received')

class DimmableLightingControl_2475F(DimmableLightingControl):
    
    """FanLinc model 2475F Dimmable Lighting Control Device Class 0x01 subcat 0x2e
    
    Two separate INSTEON On/Off switch devices are created with ID
        1) Ligth
            - ID: xxxxxx (where xxxxxx is the Insteon address of the device)
            - Controls: 
                - light_on(onlevel=0xff)
                - light_on_fast(onlevel=0xff)
                - light_off()
                - light_off_fast()
            - Monitor: lightOnLevel.connect(callback)
        2) Fan
            - ID: xxxxxx_2  (where xxxxxx is the Insteon address of the device)
            - Controls: 
                - fan_on(onlevel=0xff)
                - fan_off()
                - light_on(onlevel=0xff)  - Same as fan_on(onlevel=0xff)
                - light_off()  - Same as fan_off()
            - Monitor: fanSpeed.connect(callback)

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)

        self.fanSpeed = StateChangeSignal(self.id, "fanSpeed", self.light_status_request, 0x00)
        self._nextCommandIsFanStatus = False

        # 2475F has a custom COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00 where cmd1:0x19 and cmd2:0x03 to get the fan status
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, {'cmd1':0x19, 'cmd2':0x03}, 
                                                     self._fan_status_request_ack, MESSAGE_ACK)
    
    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton = 0x01):
        devices = []
        devices.append(DimmableLightingControl_2475F(plm, address, cat, subcat, product_key, description + ' Light', model, 0x01))
        devices.append(DimmableLightingControl_2475F(plm, address, cat, subcat, product_key, description + ' Fan', model, 0x02))
        return devices
    
    def receive_message(self, msg):
        """ 
        PLM will dispatch commands to the first device in a class. If there are two devices, like the 2475F, 
        the device needs to recognize that the message is for a different group than the first group
        and dispatch the message to the correct device.
        """
        
        self.log.debug('Starting DimmableLightingControl_2475F.receive_message')
        self.log.debug('Next command is fan status: %r', self._nextCommandIsFanStatus)
        if self._nextCommandIsFanStatus:
            self._fan_status_update_received(msg)
        elif msg.code == MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51:
            # I think byte 0 ('d1') of the extended message is always the group number for 0x01 and 0x02 devices
            if msg.userdata[0] == self._groupbutton:  
                super().receive_message(msg)
            else:
                id = self._get_device_id(msg.userdata[0])
                device = self._plm.devices[id]
                if device is not None:
                    device.receive_message(msg)
        else:
            super().receive_message(msg)
        
        self.log.debug('Ending DimmableLightingControl_2475F.receive_message')
    
    def light_status_request(self):
        """ 
        Status request options are set in cmd2 as:
            0x00 Light control
            0x03 Fan control.
        """
        self.log.debug('Starting DimmableLightingControl_2475F.light_status_request')
        if self._groupbutton == 0x01:
            self.log.debug('Sending light status request')
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        else:
            self.log.debug('Sending fan status request')
            self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, 0x03)
            
        self.log.debug('Ending DimmableLightingControl_2475F.light_status_request')
    
    def _fan_status_request_ack(self, msg):
        self.log.debug('Starting DimmableLightingControl_2475F._fan_status_request_ack')
        self._nextCommandIsFanStatus = True
        self.log.debug('Ending DimmableLightingControl_2475F._fan_status_request_ack')

    def _fan_status_update_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Off 
            0x01:0x7f = Low
            0x80:0xfe = Med
            0xff = High
        """
        self.log.debug('Starting DimmableLightingControl_2475F._fan_status_update_received')
        device2 = self._plm.devices[self._get_device_id(0x02)]
        self._nextCommandIsFanStatus = False
        device2.fanSpeed.value = msg.cmd2
        self.log.debug('Ending DimmableLightingControl_2475F._fan_status_update_received')

    def _light_on_command_received(self, msg):
        device1 = self._plm.devices[self._get_device_id(0x01)]
        device2 = self._plm.devices[self._get_device_id(0x02)]
        device1.light_status_request()
        device2.ligth_status_request()

    def _light_off_command_received(self, msg):
        device1 = self._plm.devices[self._get_device_id(0x01)]
        device2 = self._plm.devices[self._get_device_id(0x02)]
        device1.light_status_request()
        device2.ligth_status_request()