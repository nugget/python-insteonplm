"""Insteon Switched Lighting Control Device Class Module."""
from insteonplm.devices import Device
from insteonplm.states.onOff import (OnOffSwitch,
                                     OnOffSwitch_OutletTop,
                                     OnOffSwitch_OutletBottom,
                                     OnOffKeypadA,
                                     OnOffKeypad)
from insteonplm.messsages.userdata import Userdata
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.const import COMMAND_EXTENDED_GET_SET_0X2E_0X00


class SwitchedLightingControl(Device):
    """Switched Lighting Control.

    Device Class 0x02 subcat Any

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

    def __init__(self, plm, address, cat, subcat, product_key=0x00,
                 description='', model=''):
        """Initialize the SwitchedLightingControl device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = OnOffSwitch(
            self._address, "lightOnOff", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class SwitchedLightingControl_2663_222(Device):
    """On/Off outlet model 2663-222 Switched Lighting Control.

    Device Class 0x02 subcat 0x39

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

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwitchedLightingControl_2663_222 device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = OnOffSwitch_OutletTop(
            self._address, "outletTopOnOff", 0x01, self._send_msg,
            self._message_callbacks, 0x00)
        self._stateList[0x02] = OnOffSwitch_OutletBottom(
            self._address, "outletBottomOnOff", 0x02, self._send_msg,
            self._message_callbacks, 0x00)


class SwichedLightingControlKeypad(Device):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwichedLightingControlKeypad device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = OnOffKeypadA(
            self._address, "onOffButtonA", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

        self._led_changed = {}

    def _led_on(self, group):
        bitmask = 1 if self._stateList[0x01].led.value else 0
        for curr_group in self._stateList:
            bitshift = curr_group - 1
            ledvalue = self._stateList[curr_group].led.value
            bitmask = ((1 if ledvalue else 0) << bitshift) | bitmask

        bitmask = bitmask | 1 << group - 1
        user_data = Userdata({'d1': 0x01,
                              'd2': 0x09,
                              'd3': bitmask})
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_GET_SET_0X2E_0X00,
                           user_data)
        self._led_changed = {'group': group, 'val': 1}
        self._send_message(cmd, self._led_updated)

    def _led_off(self, group):
        bitmask = 1 if self._stateList[0x01].led.value else 0
        for curr_group in self._stateList:
            bitshift = curr_group - 1
            ledvalue = self._stateList[curr_group].led.value
            bitmask = ((1 if ledvalue else 0) << bitshift) | bitmask

        bitmask = bitmask & 0xff ^ 1 << group - 1
        user_data = Userdata({'d1': 0x01,
                              'd2': 0x09,
                              'd3': bitmask})
        cmd = ExtendedSend(self._address,
                           COMMAND_EXTENDED_GET_SET_0X2E_0X00,
                           user_data)
        self._led_changed = {'group': group, 'val': 0}
        self._send_message(cmd, self._led_updated)

    def _led_updated(self, msg):
        group = self._led_changed.get('group')
        if group:
            val = self._led_changed.get('val')
            self._stateList[group].led.notify_subscribers(val)

    def _add_buttons(self, button_list):
        for group in button_list:
            self._stateList[group] = OnOffKeypad(
                self._address, "onOffButton{}".format(button_list[group]),
                group, self._send_msg, self._message_callbacks, 0x00)

            self._stateList[group].on_method = self._led_on
            self._stateList[group].off_method = self._led_off


class SwitchedLightingControl_2487S_8(SwichedLightingControlKeypad):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        self._add_buttons(button_list)


class SwitchedLightingControl_2487S_6(SwichedLightingControlKeypad):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G'}
        self._add_buttons(button_list)
