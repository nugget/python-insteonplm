from .stateBase import StateBase
from insteonplm.constants import *
from insteonplm.messages import (StandardSend, ExtendedSend, 
                                 StandardReceive, ExtendedReceive, 
                                 MessageFlags)

class OnOffSwitch(StateBase):
    """Device state representing an On/Off switch that is controllable.

    Available methods are:
    on()
    off()
    connect()
    update(self, val)
    async_refresh_state()
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._message_callbacks.add(StandardReceive(address, None, None, 0x11, None), self._on_message_received)
        self._message_callbacks.add(StandardReceive(address, None, None, 0x13, None), self._off_message_received)
        self._message_callbacks.add(StandardSend(address,0x19, 0x00, None, acknak=MESSAGE_ACK), self._status_request_ack_received)

    def on(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE['cmd1'], 0xff))

    def off(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00['cmd1'], 0x00))

    def _on_message_received(self, msg):
        self._value = 0xff
        self._update_subscribers(self._value)

    def _off_message_received(self, msg):
        self._value = 0x00
        self._update_subscribers(self._value)

    def _send_status_request(self):
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd'], 0x00))

    def _status_request_ack_received(self, msg):
        self.log.debug('Starting OnOffSwitch._status_request_ack_received')
        self._message_callbacks.add(StandardReceive(self._address, None,
                                                    MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None), 
                                                    None, None), 
                                    self._status_message_received, True)
        self.log.debug('Ending OnOffSwitch._status_request_ack_received')

    def _status_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch._status_message_received')
        self._message_callbacks.remove(StandardReceive(self._address, None, 
                                                          MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None), 
                                                          None, None), 
                                          self._status_message_received)
        self._value = msg.cmd2
        self._update_subscribers(self._value)
        self.log.debug('Starting OnOffSwitch._status_message_received')

class OnOffSwitch_OutletTop(OnOffSwitch):
    """Device state representing a the top outlet On/Off switch that is controllable.

    Available methods are:
    on(self)
    off(self)
    connect(self, call_back)
    update(self, val)
    async_refresh_state(self)
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)
        
        self._message_callbacks.add(StandardSend(self._address ,0x19, 0x01, flags=None, acknak=MESSAGE_ACK ), 
                                    self._status_request_0x01_ack_received)

    def _status_message_0x01_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Ending OnOffSwitch_OutletTop._status_message_0x01_received')

        self._message_callbacks.remove(StandardReceive(self._address, None,
                                                       MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None), 
                                                       None, None), 
                                       self._status_message_0x01_received)

        if msg.cmd2 == 0x00 or msg.cmd2 == 0x02:
            self.log.debug('Sending Top Outlet %s Off', self._address)
            self._value = 0x00
            self._update_subscribers(self._value)
        elif msg.cmd2 == 0x01 or msg.cmd2 == 0x03:
            self.log.debug('Sending Top Outlet %s On', self._address)
            self._value = 0xff
            self._update_subscribers(self._value)
        else:
            raise ValueError
        self.log.debug('Ending OnOffSwitch_OutletTop._status_message_0x01_received')

    def _status_request_0x01_ack_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletTop._status_request_0x01_ack_received')
        self._message_callbacks.add(StandardReceive(self._address, None,
                                                    MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None), 
                                                    None, None), 
                                    self._status_message_0x01_received)
        self.log.debug('Ending OnOffSwitch_OutletTop._status_request_0x01_ack_received')
        
class OnOffSwitch_OutletBottom(StateBase):
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
        self._message_callbacks.add(ExtendedReceive(self._address, None, 0x11, None, self._udata), self._on_message_received)
        self._message_callbacks.add(ExtendedReceive(self._address, None, 0x13, None, self._udata), self._off_message_received)
        self._message_callbacks.add(StandardSend(self._address ,0x19, 0x01, flags=None, acknak=MESSAGE_ACK), 
                                    self._status_request_ack_received)

    def on(self):
        self._send_method(ExtendedSend(self._address, 0x11, 0xff, self._udata))

    def off(self):
        self._send_method(ExtendedSend(self._address, 0x13, 0x00, self._udata))

    def _on_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._on_message_received')
        self._value = 0xff
        self._update_subscribers(self._value)
        self.log.debug('Ending OnOffSwitch_OutletBottom._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._off_message_received')
        self._value = 0x00
        self._update_subscribers(self._value)
        self.log.debug('Ending OnOffSwitch_OutletBottom._off_message_received')

    def _status_request(self):
        self.log.debug('Starting OnOffSwitch_OutletBottom._status_request')
        self._send_method(StandardSend(self._address, 0x19, 0x01))
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

        self._message_callbacks.add(StandardReceive(self._address, None,
                                                    MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None), 
                                                    None, None), 
                                    self._status_message_received)

        if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
            self.log.debug('Sending Bottom Outlet %s Off', self._address)
            self._value = 0x00
            self._update_subscribers(self._value)
        elif msg.cmd2 == 0x02 or msg.cmd2 == 0x03:
            self.log.debug('Sending Bottom Outlet %s On', self._address)
            self._value = 0xff
            self._update_subscribers(self._value)
        else:
            raise ValueError
        self.log.debug('Ending OnOffSwitch_OutletBottom._status_message_received')
    
    def _status_request_ack_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._status_request_ack_received')
        self._message_callbacks.add(StandardReceive(self._address, None,
                                                    MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK, None), 
                                                    None, None), 
                                    self._status_message_received)
        self.log.debug('Ending OnOffSwitch_OutletBottom._status_request_ack_received')
