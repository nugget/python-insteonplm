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

class SwitchedLightingControl_2663_222(SwitchedLightingControl):

    def __init__(self, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton=0x01):
        super().__init__(plm, address, cat, subcat, product_key, description, model, groupbutton)

        # 2663-222 has a custom COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00 where cmd1:0x19 and cmd2:0x01 otherwise you only get the top outlet status
        self._message_callbacks.add_message_callback(MESSAGE_SEND_STANDARD_MESSAGE_0X62, {'cmd1':0x19, 'cmd2':0x01}, self._light_status_request_ack, MESSAGE_ACK)

    @classmethod
    def create(cls, plm, address, cat, subcat, product_key=None, description=None, model=None, groupbutton = 0x01):
        devices = []
        devices.append(SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description, model, 0x01))
        devices.append(SwitchedLightingControl_2663_222(plm, address, cat, subcat, product_key, description, model, 0x02))
        return devices
    
    def receive_message(self, msg):
        """ 
        PLM will dispatch commands to the first device in a class. If there are two devices, like the 2662-222, 
        the device needs to recognize that the message is for a different group than the first group
        and dispatch the message to the correct device.
        """
        if msg.code == MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51:
            # I think byte 0 ('d1') of the extended message is always the group number for 0x01 and 0x02 devices
            if msg.userdata[0] == self._groupbutton:  
                return super().receive_message(msg)
            else:
                id = self._get_device_id(msg.userdata[0])
                device = self._plm.devices[id]
                if device is not None:
                    return device.receive_message(msg)
        return super().receive_message(msg)
    
    def light_status_request(self):
        """ 
        Status request options are set in cmd2 as:
            0x00 Top outlet only
            0x01 Top and Bottom outlets
        Sending status request for both outlets all the time.
        """
        self._plm.send_standard(self.address.hex, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00, 0x01)

    def _status_update_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        device2 = self._plm.devices[self._get_device_id(0x02)]
        self._nextCommandIsStatus = False
        if msg.cmd2 == 0x00:
            self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, 0x00)
            device2.lightOnLevel.update(device2.id, self.lightOnLevel._stateName, 0x00)
        elif msg.cmd2 == 0x01:
            self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, 0xff)
            device2.lightOnLevel.update(device2.id, self.lightOnLevel._stateName, 0x00)
        elif msg.cmd2 == 0x02:
            self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, 0x00)
            device2.lightOnLevel.update(device2.id, self.lightOnLevel._stateName, 0xff)
        elif msg.cmd2 == 0x03:
            self.lightOnLevel.update(self.id, self.lightOnLevel._stateName, 0xff)
            device2.lightOnLevel.update(device2.id, self.lightOnLevel._stateName, 0xff)
        else:
            raise ValueError