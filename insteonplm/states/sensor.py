
from .stateBase import StateBase
from insteonplm.constants import *
from insteonplm.messages import (StandardSend, ExtendedSend, 
                                 StandardReceive, ExtendedReceive, 
                                 MessageFlags)

class VariableSensor(StateBase):
    """Device state representing an On/Off sensor that is not controllable.

    Available methods are:
    - register_updates(self, callback)
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._sensor_on_command_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._sensor_off_command_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._sensor_on_command_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
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
        self._update_subscribers(0x00)

class MotionSensor(StateBase):
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._sensor_on_command_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._sensor_off_command_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._sensor_on_command_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._sensor_off_command_received)

    def _sensor_on_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x11 Sensor On
        When a message is received any state listeners are updated with the 
        return 0x01 for on
        """
        self.log.debug('Starting MotionSensor._sensor_on_command_received')
        self._update_subscribers(0xff)
        self.log.debug('Starting MotionSensor._sensor_on_command_received')

    def _sensor_off_command_received(self, msg):
        """
        Message handler for Standard (0x50) or Extended (0x51) message commands 0x13 Sensor Off
        When a message is received any state listeners are updated with the 
        return 0x00 for off
        """
        self.log.debug('Starting MotionSensor._sensor_on_command_received')
        self._update_subscribers(0x00)
        self.log.debug('Starting MotionSensor._sensor_on_command_received')

class SmokeCO2Sensor(StateBase):
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)
        
        self._message_callbacks.add(StandardReceive.template(address=self._address,
                                                             commandtuple = COMMAND_LIGHT_ON_0X11_NONE,
                                                             flags = MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None)), 
                                    self._sensor_state_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._sensor_state_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._sensor_state_received)

    def _sensor_state_received(self, msg):
        self.log.debug('Starting SecurityHealthSafety_2982_222._sensor_on_command_received')
        self._update_subscribers(msg.targetHi)
        self.log.debug('Ending SecurityHealthSafety_2982_222._sensor_on_command_received')

class IoLincSensor(StateBase):
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None)), 
                                    self._open_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_BROADCAST_MESSAGE, None),
                                                             cmd2=None), 
                                    self._close_message_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._open_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._close_message_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._open_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._close_message_received)

    def _send_status_request(self):
        self.log.debug('Starting IoLincSensor._send_status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01), self._status_message_received)
        self.log.debug('Ending IoLincSensor._send_status_request')

    def _open_message_received(self, msg):
        self.log.debug('Starting IoLincSensor._open_message_received')
        if not msg.flags.isDirectACK:
            self._update_subscribers(0x01)
        self.log.debug('Ending IoLincSensor._open_message_received')

    def _close_message_received(self, msg):
        self.log.debug('Starting IoLincSensor._close_message_received')
        if not msg.flags.isDirectACK:
            self._update_subscribers(0x00)
        self.log.debug('Ending IoLincSensor._close_message_received')
    
    def _status_message_received(self, msg):
        self.log.debug('Starting IoLincSensor._status_message_received')
        if msg.cmd2 == 0x00:
            self._update_subscribers(0x00)
        else:
            self._update_subscribers(0x01)
        self.log.debug('Starting IoLincSensor._status_message_received')
