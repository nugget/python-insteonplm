
from .stateBase import StateBase
from insteonplm.constants import *
from insteonplm.messages import (StandardSend, ExtendedSend, 
                                 StandardReceive, ExtendedReceive, 
                                 MessageFlags)

class OnOffSensor(StateBase):
    """Device state representing an On/Off sensor that is not controllable.

    Available methods are:
    - register_updates(self, callback)
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._message_callbacks.add(StandardReceive.tempate(commandtuple = COMMAND_LIGHT_ON_0X11_NONE), 
                                                            self._sensor_on_command_received)
        self._message_callbacks.add(StandardReceive.tempate(commandtuple = COMMAND_LIGHT_OFF_0X13_0X00, cmd2 = None), 
                                                            self._sensor_off_command_received)


    def _sensor_on_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor On
        When a message is received any state listeners are updated with the 
        return 0x01 for on
        """
        self.log.debug('Starting SecurityHealthSafety._sensor_on_command_received')
        self._update_subscribers(msg.cmd2)
        self.log.debug('Starting SecurityHealthSafety._sensor_on_command_received')

    def _sensor_off_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x13 Sensor Off
        When a message is received any state listeners are updated with the 
        return 0x00 for off
        """
        self.sensor.update(self.id, 0x00)

class MotionSensor(OnOffSensor):
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

class SmokeCO2Sensor(StateBase):
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)
        
        self._message_callbacks.add(StandardReceive.template(commandtuple = COMMAND_LIGHT_ON_0X11_NONE,
                                                             flags = MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, None)), self._sensor_state_received)

    def _sensor_state_received(self, msg):
        self.log.debug('Starting SecurityHealthSafety_2982_222._sensor_on_command_received')
        self.sensor.update(self.id, msg.targetHi)
        self.log.debug('Ending SecurityHealthSafety_2982_222._sensor_on_command_received')