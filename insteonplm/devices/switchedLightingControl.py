from .devicebase import DeviceBase
from insteonplm.statechangesignal import StateChangeSignal
from insteonplm.constants import *
from .dimmableLightingControl import DimmableLightingControl 

class SwitchedLightingControl(DimmableLightingControl):
    """Switched Lighting Control Device Class 0x02
    
    INSTEON On/Off switch device class. Available device control options are:
        - light_on()
        - light_on_fast()
        - light_off()
        - light_off_fast()
    To monitor the state of the device subscribe to the state monitor:
         - lightOnLevel.connect(callback)
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def light_on(self):
        DimmableLightingControl.light_on(self)

    def light_on_fast (self):
        DimmableLightingControl.light_on_fast (self)

    def light_off(self):
        DimmableLightingControl.light_off(self)

    def light_off_fast(self):
        DimmableLightingControl.light_off_fast(self)

    def light_status_request(self):
        DimmableLightingControl.light_status_request(self)

    def get_operating_flags(self):
        DimmableLightingControl.get_operating_flags(self)

    def set_operating_flags(self):
        DimmableLightingControl.set_operating_flags(self)

    def light_manually_turned_off(self):
        DimmableLightingControl.light_manually_turned_off(self)

    def light_manually_turned_On(self):
        DimmableLightingControl.light_manually_turned_On(self)

    def _light_on_command_received(self, msg):
        self.log.debug('Starting _light_on_command_received')
        # Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Light On
        # Also handles Standard or Extended (0x62) Lights On (0x11) ACK
        # When any of these messages are received any state listeners are updated with the 
        # current light on level (cmd2)
        if msg.code == MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51 or \
          (msg.code == MESSAGE_SEND_STANDARD_MESSAGE_0X62 and msg.isextendedflag):
            group = msg.userdata[0]
            device = self._plm.devices[self._get_device_id(group)]
            device.lightOnLevel.update(device.id, 0xff)
        else:
            self.lightOnLevel.update(self.id, 0xff)
        self.log.debug('Ending _light_on_command_received')

class SwitchedLightingControl_2663_222(SwitchedLightingControl):
    
    """On/Off outlet model 2663-222 Switched Lighting Control Device Class 0x02 subcat 0x39
    
    Two separate INSTEON On/Off switch devices are created with ID
        - 'address': Top Outlet
        - 'address_2': Bottom Outlet

    Available device control options are:
        - light_on()
        - light_on_fast()
        - light_off()
        - light_off_fast()
    To monitor the state of the device subscribe to the state monitor:
         - lightOnLevel.connect(callback)
    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)

        # 2663-222 has a custom COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00 where cmd1:0x19 and cmd2:0x01 otherwise you only get the top outlet status
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, {'cmd1':0x19, 'cmd2':0x01}, self._light_status_request_ack, MESSAGE_ACK)
    
    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton = 0x01):
        devices = []
        devices.append(SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description + ' Top', model, 0x01))
        devices.append(SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description + ' Bottom', model, 0x02))
        return devices
    
    def light_status_request(self):
        """ 
        Status request options are set in cmd2 as:
            0x00 Top outlet only
            0x01 Top and Bottom outlets
        Sending status request for both outlets all the time.
        """
        self.log.debug('Starting SwitchedLightingControl_2663_222.light_status_request')
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, 0x01)
        self.log.debug('Starting SwitchedLightingControl_2663_222.light_status_request')

    def _status_update_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting SwitchedLightingControl_2663_222._status_update_received')
        device1 = self._plm.devices[self._get_device_id(0x01)]
        device2 = self._plm.devices[self._get_device_id(0x02)]
        self._nextCommandIsStatus = False
        if msg.cmd2 == 0x00:
            self.log.debug('Sending Top Outlet %s Off', device1.id)
            device1.lightOnLevel.update(device1.id, 0x00)
            self.log.debug('Sending Bottom Outlet %s Off', device2.id)
            device2.lightOnLevel.update(device2.id, 0x00)
        elif msg.cmd2 == 0x01:
            self.log.debug('Sending Top Outlet %s On', device1.id)
            device1.lightOnLevel.update(device1.id, 0xff)
            self.log.debug('Sending Bottom Outlet %s Off', device2.id)
            device2.lightOnLevel.update(device2.id, 0x00)
        elif msg.cmd2 == 0x02:
            self.log.debug('Sending Top Outlet %s Off', device1.id)
            device1.lightOnLevel.update(device1.id, 0x00)
            self.log.debug('Sending Bottom Outlet %s On', device2.id)
            device2.lightOnLevel.update(device2.id, 0xff)
        elif msg.cmd2 == 0x03:
            self.log.debug('Sending Top Outlet %s On', device1.id)
            device1.lightOnLevel.update(device1.id, 0xff)
            self.log.debug('Sending Bottom Outlet %s On', device2.id)
            device2.lightOnLevel.update(device2.id, 0xff)
        else:
            raise ValueError
        self.log.debug('Starting SwitchedLightingControl_2663_222._status_update_received')

    def _light_on_command_received(self, msg):
        self.light_status_request()

    def _light_off_command_received(self, msg):
        self.light_status_request()