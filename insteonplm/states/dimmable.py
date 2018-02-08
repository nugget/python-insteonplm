import logging
from .stateBase import StateBase
from insteonplm.constants import *
from insteonplm.messages import (StandardSend, ExtendedSend, 
                                 StandardReceive, ExtendedReceive, 
                                 MessageFlags)

class DimmableSwitch(StateBase):
    """Device state representing an On/Off switch that is controllable.

    Available methods are:
    on()
    off()
    set_level()
    brightent()
    dim()
    connect()
    update(self, val)
    async_refresh_state()
    """
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self.log.debug('Registering callbacks for DimmableSwitch device %s', self._address.human)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._on_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._on_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._off_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._off_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
                                                             address=self._address, 
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._manual_change_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
                                                             address=self._address, 
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._manual_change_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
                                                             address=self._address, 
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._manual_change_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
                                                             address=self._address, 
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._manual_change_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._on_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._on_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._off_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._off_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._manual_change_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._manual_change_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._manual_change_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._manual_change_received)

    def on(self):
        self.log.debug('Starting DimmableSwitch.on')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, cmd2 = 0xff), self._on_message_received)
        self.log.debug('Ending DimmableSwitch.on')

    def off(self):
        self.log.debug('Starting DimmableSwitch.off')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00), self._off_message_received)
        self.log.debug('Ending DimmableSwitch._off')

    def set_level(self, val):
        self.log.debug('Starting DimmableSwitch.set_level')
        if val == 0:
            self.off()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val*100
            elif val <= 0xff:
                setlevel = val
            self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, cmd2 = setlevel), self._on_message_received)
        self.log.debug('Ending DimmableSwitch.set_level')

    def brighten(self):
        self.log.debug('Starting DimmableSwitch.brighten')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00))
        self.log.debug('Ending DimmableSwitch.brighten')

    def dim(self):
        self.log.debug('Starting DimmableSwitch.dim')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00))
        self.log.debug('Ending DimmableSwitch.dim')

    def _on_message_received(self, msg):
        self.log.debug('Starting DimmableSwitch._on_message_received')
        self._update_subscribers(msg.cmd2)
        self.log.debug('Ending DimmableSwitch._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting DimmableSwitch._off_message_received')
        self._update_subscribers(0x00)
        self.log.debug('Starting DimmableSwitch._off_message_received')

    def _manual_change_received(self, msg):
        self._send_status_request()

    def _send_status_request(self):
        self.log.debug('Starting DimmableSwitch._send_status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00), self._status_message_received)
        self.log.debug('Ending DimmableSwitch._send_status_request')

    def _status_message_received(self, msg):
        self.log.debug('Starting DimmableSwitch._status_message_received')
        self._update_subscribers(msg.cmd2)
        self.log.debug('Starting DimmableSwitch._status_message_received')

class DimmableSwitch_Fan(StateBase):
    """Device state representing a the bottom outlet On/Off switch that is controllable.

    Available methods are:
    on(self)
    off(self)
    async_refresh_state(self)
    connect(self, call_back)
    update(self, val)
    async_refresh_state(self)
    """

    def __init__(self, address, statename, group, send_message_method, set_message_callback_method, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, set_message_callback_method, defaultvalue)

        self._updatemethod = self._status_request
        self._udata = {'d1': self._group}

    def on(self):
        self.log.debug('Starting DimmableSwitch_Fan.on')
        self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, self._udata, cmd2 = FAN_SPEED_MEDIUM), self._on_message_received)
        self.log.debug('Ending DimmableSwitch_Fan.on')

    def set_level(self, val):
        self.log.debug('Starting DimmableSwitch_Fan.set_level')
        speed = self._value_to_fan_speed(val)
        if val == 0:
            speed.off()
        else:
            self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, self._udata, cmd2 = speed), self._on_message_received)
        self.log.debug('Ending DimmableSwitch_Fan.set_level')

    def off(self):
        self.log.debug('Starting DimmableSwitch_Fan.off')
        self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_OFF_0X13_0x00, self._udata), self._off_message_received)
        self.log.debug('Ending DimmableSwitch_Fan.off')

    def _on_message_received(self, msg):
        self.log.debug('Starting DimmableSwitch_Fan._on_message_received')
        self._update_subscribers(0xff)
        self.log.debug('Ending DimmableSwitch_Fan._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting DimmableSwitch_Fan._off_message_received')
        self._update_subscribers(0x00)
        self.log.debug('Ending DimmableSwitch_Fan._off_message_received')

    def _status_request(self):
        self.log.debug('Starting DimmableSwitch_Fan._status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE, cmd2=0x03), self._status_message_received)
        self.log.debug('Ending DimmableSwitch_Fan._status_request')

    def _status_message_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting DimmableSwitch_Fan._status_message_received')
        self._update_subscribers(msg.cmd2)
        self.log.debug('Ending DimmableSwitch_Fan._status_message_received')

    def _value_to_fan_speed(self, speed):
        if speed > 0xfe:
            return SPEED_HIGH
        elif speed > 0x7f:
            return SPEED_MEDIUM
        elif speed > 0:
            return SPEED_LOW
        return SPEED_OFF