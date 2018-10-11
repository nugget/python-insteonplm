"""Insteon Switched Lighting Control Device Class Module."""
from insteonplm.devices import Device
from insteonplm.states.onOff import (OnOffSwitch,
                                     OnOffSwitch_OutletTop,
                                     OnOffSwitch_OutletBottom,
                                     OnOffKeypadA,
                                     OnOffKeypad,
                                     OnOffKeypadLed)


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
        """Init the SwitchedLightingControl device class."""
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
        """Init the SwitchedLightingControl_2663_222 device class."""
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
        """Init the SwichedLightingControlKeypad device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._leds = OnOffKeypadLed(
            self._address, "keypadLEDs", 0x00, self._send_msg,
            self._message_callbacks, 0x00, self._plm.loop)

        self._stateList[0x01] = OnOffKeypadA(
            self._address, "keypadButtonMain", 0x01, self._send_msg,
            self._message_callbacks, 0x00, self._leds)

    def _add_buttons(self, button_list):
        for group in button_list:
            self._stateList[group] = OnOffKeypad(
                self._address, "onOffButton{}".format(button_list[group]),
                group, self._send_msg, self._message_callbacks, 0x00,
                self._plm.loop, self._leds)

            self._leds.register_led_updates(self._stateList[group].led_changed,
                                            group)


class SwitchedLightingControl_2334_222_8(SwichedLightingControlKeypad):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        self._add_buttons(button_list)


class SwitchedLightingControl_2334_222_6(SwichedLightingControlKeypad):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {3: 'A', 4: 'B', 5: 'C', 6: 'D'}
        self._add_buttons(button_list)
