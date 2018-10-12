"""INSTEON General Controller Device Class."""
import asyncio
import logging

from insteonplm.constants import (X10_COMMAND_ALL_UNITS_OFF,
                                  X10_COMMAND_ALL_LIGHTS_ON,
                                  X10_COMMAND_ALL_LIGHTS_OFF)
from insteonplm.devices import X10Device
from insteonplm.messages.x10received import X10Received
from insteonplm.states.x10 import (X10OnOffSwitch, X10DimmableSwitch,
                                   X10OnOffSensor, X10AllUnitsOffSensor,
                                   X10AllLightsOnSensor, X10AllLightsOffSensor)


_LOGGER = logging.getLogger(__name__)


class X10OnOff(X10Device):
    """General X10 On / Off Switch Device Class."""

    def __init__(self, plm, housecode, unitcode):
        """Init the X10OnOff class."""
        super().__init__(plm, housecode, unitcode)
        self._description = 'X10 On / Off Device'

        self._stateList[0x01] = X10OnOffSwitch(
            self._address, "x10OnOffSwitch", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class X10Dimmable(X10Device):
    """General X10 Dimmable Switch Device Class."""

    def __init__(self, plm, housecode, unitcode, dim_steps=22):
        """Init the X10Dimmable class."""
        super().__init__(plm, housecode, unitcode)
        self._description = 'X10 Dimmable Device'

        self._stateList[0x01] = X10DimmableSwitch(
            self._address, "x10DimmableSwitch", 0x01, self._send_msg,
            self._message_callbacks, 0x00, dim_steps)


class X10Sensor(X10Device):
    """General X10 On / Off Sensor Device Class."""

    def __init__(self, plm, housecode, unitcode):
        """Init the X10Sensor class."""
        super().__init__(plm, housecode, unitcode)
        self._description = 'X10 On / Off Sensor Device'

        self._stateList[0x01] = X10OnOffSensor(
            self._address, "x10OnOffSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)


class X10AllUnitsOff(X10Device):
    """X10 All Units Off Device."""

    def __init__(self, plm, housecode, unitcode):
        """Init the X10AllUnitsOff class."""
        super().__init__(plm, housecode, 20)
        self._description = 'X10 All Units Off Device'

        self._stateList[0x01] = X10AllUnitsOffSensor(
            self._address, "x10AllUnitsOffSensor", 0x01, self._send_msg,
            self._message_callbacks, 0xff)

        self._stateList[0x01].register_updates(self._reset_state)
        self._register_messages()

    # pylint: disable=unused-argument
    def _reset_state(self, addr, name, val):
        loop = self._plm.loop
        if val == 0x00:
            asyncio.ensure_future(self._reset_state_value(loop), loop=loop)

    async def _reset_state_value(self, loop):
        await asyncio.sleep(1, loop=loop)
        self._stateList[0x01].reset()

    def _register_messages(self):
        all_units_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                                    X10_COMMAND_ALL_UNITS_OFF)
        self._plm.message_callbacks.add(all_units_off_msg,
                                        self.receive_message)


class X10AllLightsOn(X10Device):
    """X10 All Lights On Device."""

    def __init__(self, plm, housecode, unitcode):
        """Init the X10AllLightsOn class."""
        super().__init__(plm, housecode, 21)
        self._description = 'X10 All Lights On Device'

        self._stateList[0x01] = X10AllLightsOnSensor(
            self._address, "X10AllLightsOnSensor", 0x01, self._send_msg,
            self._message_callbacks, 0x00)

        self._stateList[0x01].register_updates(self._reset_state)
        self._register_messages()

    # pylint: disable=unused-argument
    def _reset_state(self, addr, name, val):
        loop = self._plm.loop
        if val == 0xff:
            asyncio.ensure_future(self._reset_state_value(loop), loop=loop)

    async def _reset_state_value(self, loop):
        await asyncio.sleep(1, loop=loop)
        self._stateList[0x01].reset()

    def _register_messages(self):
        all_on_msg = X10Received.command_msg(self.address.x10_housecode,
                                             X10_COMMAND_ALL_LIGHTS_ON)
        self._plm.message_callbacks.add(all_on_msg,
                                        self.receive_message)


class X10AllLightsOff(X10Device):
    """X10 All Lights Off Device."""

    def __init__(self, plm, housecode, unitcode):
        """Init the X10AllLightsOff class."""
        super().__init__(plm, housecode, 22)
        self._description = 'X10 All Lights Off Device'

        self._stateList[0x01] = X10AllLightsOffSensor(
            self._address, "X10AllLightsOffSensor", 0x01, self._send_msg,
            self._message_callbacks, 0xff)

        self._stateList[0x01].register_updates(self._reset_state)
        self._register_messages()

    # pylint: disable=unused-argument
    def _reset_state(self, addr, name, val):
        loop = self._plm.loop
        if val == 0x00:
            asyncio.ensure_future(self._reset_state_value(loop), loop=loop)

    async def _reset_state_value(self, loop):
        await asyncio.sleep(1, loop=loop)
        self._stateList[0x01].reset()

    def _register_messages(self):
        all_off_msg = X10Received.command_msg(self.address.x10_housecode,
                                              X10_COMMAND_ALL_LIGHTS_OFF)
        self._plm.message_callbacks.add(all_off_msg,
                                        self.receive_message)
