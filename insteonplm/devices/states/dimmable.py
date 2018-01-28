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

        self._message_callbacks.add(StandardReceive.template(address = self._address,
                                                             commandtuple = COMMAND_LIGHT_ON_0X11_NONE), 
                                    self._on_message_received)
        self._message_callbacks.add(StandardReceive.template(address = self._address,
                                                             commandtuple = COMMAND_LIGHT_OFF_0X13_0X00, cmd2 = None), 
                                    self._off_message_received)
        self._message_callbacks.add(StandardSend.template(address = self._address,
                                                          commandtuple = COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                                          acknak = MESSAGE_ACK), 
                                    self._status_request_ack_received)

    def on(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, cmd2 = 0xff))

    def off(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00))

    def set_level(self, val):
        if val == 0:
            self.off()
        else:
            setlevel = 255
            if val < 1:
                setlevel = val*100
            elif val <= 0xff:
                setlevel = val
            self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, cmd2 = setlevel))

    def brighten(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00))

    def dim(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00))

    def _on_message_received(self, msg):
        self._update_subscribers(0xff)

    def _off_message_received(self, msg):
        self._update_subscribers(0x00)

    def _send_status_request(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00))

    def _status_request_ack_received(self, msg):
        self.log.debug('Starting OnOffSwitch._status_request_ack_received')
        self._message_callbacks.add(StandardReceive.template(address = self._address,
                                                             flags = MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None)), 
                                    self._status_message_received, True)
        self.log.debug('Ending OnOffSwitch._status_request_ack_received')

    def _status_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch._status_message_received')
        self._message_callbacks.remove(StandardReceive.template(address = self._address,
                                                             flags = MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None)), 
                                       self._status_message_received)
        self._update_subscribers(msg.cmd2)
        self.log.debug('Starting OnOffSwitch._status_message_received')

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
        self._message_callbacks.add(ExtendedReceive.template(address = self._address, 
                                                             commandtuple = COMMAND_LIGHT_ON_0X11_NONE, 
                                                             userdata = self._udata), 
                                    self._on_message_received)
        self._message_callbacks.add(ExtendedReceive.template(address = self._address, 
                                                             commandtuple = COMMAND_LIGHT_OFF_0X13_0X00, 
                                                             userdata = self._udata), 
                                    self._off_message_received)
        self._message_callbacks.add(StandardSend.template(address = self._address,
                                                          commandtuple = COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE,
                                                          cmd2=0x03,
                                                          acknak=MESSAGE_ACK), 
                                    self._status_request_ack_received)

    def on(self):
        self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, self._udata, cmd2 = FAN_SPEED_MEDIUM))

    def set_level(self, val):
        speed = self._value_to_fan_speed(val)
        if val == 0:
            speed.off()
        else:
            self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, self._udata, cmd2 = speed))

    def off(self):
        self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_OFF_0X13_0x00, self._udata))

    def _on_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._on_message_received')
        self._update_subscribers(0xff)
        self.log.debug('Ending OnOffSwitch_OutletBottom._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._off_message_received')
        self._update_subscribers(0x00)
        self.log.debug('Ending OnOffSwitch_OutletBottom._off_message_received')

    def _status_request(self):
        self.log.debug('Starting OnOffSwitch_OutletBottom._status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE, cmd2=0x03))
        self.log.debug('Ending OnOffSwitch_OutletBottom._status_request')

    def _status_message_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting OnOffSwitch_OutletBottom._status_message_received')

        self._message_callbacks.add(StandardReceive.template(address = self._address,
                                                             flags = MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None)), 
                                    self._status_message_received)

        if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
            self.log.debug('Sending Bottom Outlet %s Off', self._address)
            self._update_subscribers(0x00)
        elif msg.cmd2 == 0x02 or msg.cmd2 == 0x03:
            self.log.debug('Sending Bottom Outlet %s On', self._address)
            self._update_subscribers(0xff)
        else:
            raise ValueError
        self.log.debug('Ending OnOffSwitch_OutletBottom._status_message_received')
    
    def _status_request_ack_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._status_request_ack_received')
        self._message_callbacks.add(StandardReceive.template(address = self._address,
                                                             flags = MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None)), 
                                    self._status_message_received)
        self.log.debug('Ending OnOffSwitch_OutletBottom._status_request_ack_received')

    def _value_to_fan_speed(self, speed):
        if speed > 0xfe:
            return SPEED_HIGH
        elif speed > 0x7f:
            return SPEED_MEDIUM
        elif speed > 0:
            return SPEED_LOW
        return SPEED_OFF