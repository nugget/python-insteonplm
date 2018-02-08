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
    register_updates()
    async_refresh_state()
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

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
        self.log.debug('Starting OnOffSwitch.on')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, 0xff), self._on_message_received)
        self.log.debug('Ending OnOffSwitch.on')

    def off(self):
        self.log.debug('Starting OnOffSwitch.off')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00), self._off_message_received)
        self.log.debug('Ending OnOffSwitch.off')

    def _on_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch._on_message_received')
        self._update_subscribers(0xff)
        self.log.debug('Ending OnOffSwitch._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch._off_message_received')
        self._update_subscribers(0x00)
        self.log.debug('Ending OnOffSwitch._off_message_received')

    def _manual_change_received(self, msg):
        self.log.debug('Starting OnOffSwitch._manual_change_received')
        self._send_status_request()
        self.log.debug('Ending OnOffSwitch._manual_change_received')

    def _send_status_request(self):
        self.log.debug('Starting OnOffSwitch._send_status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00), self._status_message_received)

    def _status_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch._status_message_received')
        self._update_subscribers(msg.cmd2)
        self.log.debug('Ending OnOffSwitch._status_message_received')

class OnOffSwitch_OutletTop(StateBase):
    """Device state representing a the top outlet On/Off switch that is controllable.

    Available methods are:
    on(self)
    off(self)
    register_updates(self, call_back)
    async_refresh_state(self)
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)
        
        self._updatemethod = self._send_status_0x01_request

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
        self.log.debug('Starting OnOffSwitch_OutletTop.on')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, 0xff), self._on_message_received)
        self.log.debug('Ending OnOffSwitch_OutletTop.on')

    def off(self):
        self.log.debug('Starting OnOffSwitch_OutletTop.off')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00), self._off_message_received)
        self.log.debug('Ending OnOffSwitch_OutletTop.off')

    def _on_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletTop._on_message_received')
        self._update_subscribers(0xff)
        self.log.debug('Ending OnOffSwitch_OutletTop._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletTop._off_message_received')
        self._update_subscribers(0x00)
        self.log.debug('Ending OnOffSwitch_OutletTop._off_message_received')

    def _manual_change_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletTop._manual_change_received')
        self._send_status_0x01_request()
        self.log.debug('Ending OnOffSwitch_OutletTop._manual_change_received')

    def _send_status_0x01_request(self):
        self.log.debug('Starting OnOffSwitch_OutletTop._status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01), self._status_message_0x01_received)
        self.log.debug('Ending OnOffSwitch_OutletTop._status_request')
        
    def _status_message_0x01_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting OnOffSwitch_OutletTop._status_message_0x01_received')
        if msg.cmd2 == 0x00 or msg.cmd2 == 0x02:
            self.log.debug('Sending Top Outlet %s Off', self._address)
            self._update_subscribers(0x00)
        elif msg.cmd2 == 0x01 or msg.cmd2 == 0x03:
            self.log.debug('Sending Top Outlet %s On', self._address)
            self._update_subscribers(0xff)
        else:
            raise ValueError
        self.log.debug('Ending OnOffSwitch_OutletTop._status_message_0x01_received')
        
class OnOffSwitch_OutletBottom(StateBase):
    """Device state representing a the bottom outlet On/Off switch that is controllable.

    Available methods are:
    on(self)
    off(self)
    register_upodates(self, call_back)
    async_refresh_state(self)
    """

    def __init__(self, address, statename, group, send_message_method, set_message_callback_method, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, set_message_callback_method, defaultvalue)

        self._updatemethod = self._send_status_0x01_request
        self._udata = {'d1': self._group}

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
        self.log.debug('Starting OnOffSwitch_OutletBottom.on')
        self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, self._udata, cmd2=0xff), self._on_message_received)
        self.log.debug('Ending OnOffSwitch_OutletBottom.on')

    def off(self):
        self.log.debug('Starting OnOffSwitch_OutletBottom.off')
        self._send_method(ExtendedSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00, self._udata), self._off_message_received)
        self.log.debug('Ending OnOffSwitch_OutletBottom.off')

    def _on_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._on_message_received')
        self._update_subscribers(0xff)
        self.log.debug('Ending OnOffSwitch_OutletBottom._on_message_received')

    def _off_message_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._off_message_received')
        self._update_subscribers(0x00)
        self.log.debug('Ending OnOffSwitch_OutletBottom._off_message_received')

    def _manual_change_received(self, msg):
        self.log.debug('Starting OnOffSwitch_OutletBottom._manual_change_received')
        self._send_status_0x01_request()
        self.log.debug('Ending OnOffSwitch_OutletBottom._manual_change_received')

    def _send_status_0x01_request(self):
        self.log.debug('Starting OnOffSwitch_OutletBottom._send_status_0x01_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01), self._status_message_received)
        self.log.debug('Ending OnOffSwitch_OutletBottom._send_status_0x01_request')

    def _status_message_received(self, msg):
        """
        The following status values can be recieve:
            0x00 = Both Outlets Off 
            0x01 = Only Top Outlet On 
            0x02 = Only Bottom Outlet On 
            0x03 = Both Outlets On 
        """
        self.log.debug('Starting OnOffSwitch_OutletBottom._status_message_received')

        if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
            self.log.debug('Sending Bottom Outlet %s Off', self._address)
            self._update_subscribers(0x00)
        elif msg.cmd2 == 0x02 or msg.cmd2 == 0x03:
            self.log.debug('Sending Bottom Outlet %s On', self._address)
            self._update_subscribers(0xff)
        else:
            raise ValueError
        self.log.debug('Ending OnOffSwitch_OutletBottom._status_message_received')

class OpenClosedRelay(StateBase):
    """Device state representing an On/Off switch that is controllable.

    Available methods are:
    open()
    close()
    register_updates()
    async_refresh_state()
    """
    
    def __init__(self, address, statename, group, send_message_method, message_callbacks, defaultvalue=None):
        super().__init__(address, statename, group, send_message_method, message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._open_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None)), 
                                    self._open_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._close_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                                             address=self._address,
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
                                                             cmd2=None), 
                                    self._close_message_received)

        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None)), 
                                    self._open_message_received)
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
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
        self._message_callbacks.add(StandardReceive.template(commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
                                                             address=self._address, 
                                                             target=bytearray([0x00, 0x00, self._group]),
                                                             flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_BROADCAST, None),
                                                             cmd2=None), 
                                    self._close_message_received)
        
    def open(self):
        self.log.debug('Starting OpenCloseRelay.open')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_ON_0X11_NONE, 0xff), self._open_message_received)
        self.log.debug('Ending OpenCloseRelay.open')

    def close(self):
        self.log.debug('Starting OpenCloseRelay.close')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_OFF_0X13_0X00), self._close_message_received)
        self.log.debug('Ending OpenCloseRelay.close')

    def _open_message_received(self, msg):
        self.log.debug('Starting OpenCloseRelay._open_message_received')
        if msg.flags.isDirectACK:
            self._update_subscribers(0xff)
        self.log.debug('Ending OpenCloseRelay._open_message_received')

    def _close_message_received(self, msg):
        self.log.debug('Starting OpenCloseRelay._close_message_received')
        if msg.flags.isDirectACK:
            self._update_subscribers(0x00)
        self.log.debug('Ending OpenCloseRelay._close_message_received')

    def _send_status_request(self):
        self.log.debug('Starting OpenCloseRelay._send_status_request')
        self._send_method(StandardSend(self._address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00), self._status_message_received)
        self.log.debug('Ending OpenCloseRelay._send_status_request')

    def _status_message_received(self, msg):
        self.log.debug('Starting OpenCloseRelay._status_message_received')
        if msg.cmd2 == 0x00:
            self._update_subscribers(0x00)
        else:
            self._update_subscribers(0xff)
        self.log.debug('Starting OpenCloseRelay._status_message_received')