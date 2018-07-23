"""INSTEON Device Type Dimmable Lighting Control Module."""
from insteonplm.devices import Device
from insteonplm.states.dimmable import (DimmableSwitch,
                                        DimmableSwitch_Fan,
                                        DimmableKeypadA,
                                        DimmableKeypad)
from insteonplm.messages.userdata import Userdata
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.constants import COMMAND_EXTENDED_GET_SET_0X2E_0X00


class DimmableLightingControl(Device):
    """Dimmable Lighting Controller.

    INSTEON On/Off switch device class. Available device control options are:
        - light_on(onlevel=0xff)
        - light_on_fast(onlevel=0xff)
        - light_off()
        - light_off_fast()

    To monitor changes to the state of the device subscribe to the state
    monitor:
         - lightOnLevel.connect(callback)  (state='LightOnLevel')

    where callback defined as:
        - callback(self, device_id, state, state_value)
    """

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the DimmableLightingControl Class."""
        Device.__init__(self, plm, address, cat, subcat, product_key,
                        description, model)

        self._stateList[0x01] = DimmableSwitch(
            self._address, "lightOnLevel", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class DimmableLightingControl_2475F(DimmableLightingControl):
    """FanLinc model 2475F Dimmable Lighting Control.

    Device Class 0x01 subcat 0x2e

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

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initalize the DimmableLightingControl_2475F Class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = DimmableSwitch(
            self._address, "lightOnLevel", 0x01, self._send_msg,
            self._message_callbacks, 0x00)
        self._stateList[0x02] = DimmableSwitch_Fan(
            self._address, "fanOnLevel", 0x02, self._send_msg,
            self._message_callbacks, 0x00)


class SwitchedLightingControl_2334_222(Device):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwichedLightingControlKeypad device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = DimmableKeypadA(
            self._address, "keypadButtonA", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

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
            self._stateList[group] = DimmableKeypad(
                self._address, "keypadButton{}".format(button_list[group]),
                group, self._send_msg, self._message_callbacks, 0x00)

            self._stateList[group].on_method = self._led_on
            self._stateList[group].off_method = self._led_off


class SwitchedLightingControl_2334_222_8(SwitchedLightingControl_2334_222):
    """Dimmable 8 Button KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        self._add_buttons(button_list)


class SwitchedLightingControl_2334_222_6(SwitchedLightingControl_2334_222):
    """Dimmable 6 Button KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Initialize the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G'}
        self._add_buttons(button_list)
