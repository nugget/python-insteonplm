"""INSTEON Device Type Dimmable Lighting Control Module."""
from insteonplm.devices import Device
from insteonplm.states.dimmable import (DimmableSwitch,
                                        DimmableSwitch_Fan,
                                        DimmableKeypadA)
from insteonplm.states.onOff import OnOffKeypad, OnOffKeypadLed


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
        """Init the DimmableLightingControl Class."""
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
        """Init the DimmableLightingControl_2475F Class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._stateList[0x01] = DimmableSwitch(
            self._address, "lightOnLevel", 0x01, self._send_msg,
            self._message_callbacks, 0x00)
        self._stateList[0x02] = DimmableSwitch_Fan(
            self._address, "fanOnLevel", 0x02, self._send_msg,
            self._message_callbacks, 0x00)


class DimmableLightingControl_2334_222(Device):
    """On/Off KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SwichedLightingControlKeypad device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        self._leds = OnOffKeypadLed(
            self._address, "keypadLEDs", 0x00, self._send_msg,
            self._message_callbacks, 0x00, self._plm.loop)

        self._stateList[0x01] = DimmableKeypadA(
            self._address, "keypadButtonMain", 0x01, self._send_msg,
            self._message_callbacks, 0x00, self._leds)

    def _add_buttons(self, button_list):
        for group in button_list:
            self._stateList[group] = OnOffKeypad(
                self._address, "keypadButton{}".format(button_list[group]),
                group, self._send_msg, self._message_callbacks, 0x00,
                self._plm.loop, self._leds)

            self._leds.register_led_updates(self._stateList[group].led_changed,
                                            group)


class DimmableLightingControl_2334_222_8(DimmableLightingControl_2334_222):
    """Dimmable 8 Button KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        self._add_buttons(button_list)


class DimmableLightingControl_2334_222_6(DimmableLightingControl_2334_222):
    """Dimmable 6 Button KeypadLinc Switched Lighting Control."""

    def __init__(self, plm, address, cat, subcat, product_key=None,
                 description=None, model=None):
        """Init the SwitchedLightingControl_2487S device class."""
        super().__init__(plm, address, cat, subcat, product_key,
                         description, model)

        button_list = {3: 'A', 4: 'B', 5: 'C', 6: 'D'}
        self._add_buttons(button_list)
