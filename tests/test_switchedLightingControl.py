"""Test Switched Lighting Control devices."""

import asyncio
from insteonplm.constants import (COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                  COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                                  MESSAGE_ACK,
                                  MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                  MESSAGE_TYPE_DIRECT_MESSAGE_ACK)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.devices.switchedLightingControl import (
    SwitchedLightingControl, SwitchedLightingControl_2663_222)
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks


def test_switchedLightingControl():
    """Test SwitchedLightingControl."""
    def run_test(loop):
        """Asyncio test method."""
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl(plm, address, cat, subcat,
                                         product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00  # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE,
                                   cmd2=0xff, acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff,
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue1 == 0xff

        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00,
                                   acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, COMMAND_LIGHT_OFF_0X13_0X00,
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00)
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_switchedLightingControl_maual_changes():
    """Test SwitchedLightingControl maual changes."""
    def run_test(loop):
        """Asyncio test method."""
        plm = MockPLM(loop)
        address = '1a2b3c'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl(plm, address, cat, subcat,
                                         product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00  # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        receivedmsg = StandardReceive(
            address, '000001', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x66,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        receivedmsg = StandardReceive(
            address, '000001', COMMAND_LIGHT_OFF_0X13_0X00,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_switchedLightingControl_status():
    """Test SwitchedLightingControl status."""
    def run_test(loop):
        """Asyncio test method."""
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl(plm, address, cat, subcat,
                                         product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00  # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        callbacks = MockCallbacks()
        device.states[0x01].register_updates(callbacks.callbackmethod1)

        device.states[0x01].async_refresh_state()
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardSend(address,
                                   COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
                                   acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, {'cmd1': 0x09, 'cmd2': 0xff},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue1 == 0xff

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_switchedLightingControl_2663_222():
    """Test SwitchedLightingControl device 2663-222."""
    @asyncio.coroutine
    def run_test(loop):
        """Asyncio test method."""
        plm = MockPLM(loop)
        callbacks = MockCallbacks()

        address = '1a2b3c'
        target = '4d5e6f'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl_2663_222(
            plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00  # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)

        device.states[0x01].on()
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0xff)
        assert plm.sentmessage == sentmsg.hex
        receivedmsg = StandardSend(address, COMMAND_LIGHT_ON_0X11_NONE,
                                   cmd2=0xff, acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, {'cmd1': 0x09, 'cmd2': 0xff},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        device.states[0x02].on()
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE,
                                   {'d1': 0x02}, cmd2=0xff, acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, {'cmd1': 0x09, 'cmd2': 0xff},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = ExtendedSend(address, COMMAND_LIGHT_ON_0X11_NONE,
                               {'d1': 0x02}, cmd2=0xff)
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue2 == 0xff

        device.states[0x01].off()
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00)
        assert plm.sentmessage == sentmsg.hex
        receivedmsg = StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00,
                                   acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, {'cmd1': 0x09, 'cmd2': 0x00},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = StandardSend(address, COMMAND_LIGHT_OFF_0X13_0X00)
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue1 == 0x00

        device.states[0x02].off()
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = ExtendedSend(address, COMMAND_LIGHT_OFF_0X13_0X00,
                                   {'d1': 0x02}, acknak=MESSAGE_ACK)
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        receivedmsg = StandardReceive(
            address, target, {'cmd1': 0x09, 'cmd2': 0x00},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        sentmsg = ExtendedSend(address, COMMAND_LIGHT_OFF_0X13_0X00,
                               {'d1': 0x02})
        assert plm.sentmessage == sentmsg.hex
        assert callbacks.callbackvalue2 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_switchedLightingControl_2663_222_manual_change():
    """Test SwitchedLightingControl device 2663-222 manual change."""
    @asyncio.coroutine
    def run_test(loop):
        """Asyncio test method."""
        plm = MockPLM(loop)
        callbacks = MockCallbacks()

        address = '1a2b3c'
        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        device = SwitchedLightingControl_2663_222(
            plm, address, cat, subcat, product_key, description, model)

        assert device.address.hex == address
        assert device.cat == cat
        assert device.subcat == subcat
        assert device.product_key == 0x00  # Product key should not be None
        assert device.description == description
        assert device.model == model
        assert device.id == address

        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)

        receivedmsg = StandardReceive(
            address, '000001', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x66,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0xff

        receivedmsg = StandardReceive(
            address, '000001', COMMAND_LIGHT_OFF_0X13_0X00,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00

        receivedmsg = StandardReceive(
            address, '000002', COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x66,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue2 == 0xff

        receivedmsg = StandardReceive(
            address, '000002', COMMAND_LIGHT_OFF_0X13_0X00,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 2, 3))
        plm.message_received(receivedmsg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue2 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_switchedLightingControl_2663_222_status():
    """Test SwitchedLightingControl device 2663-222 status."""
    @asyncio.coroutine
    def run_test(loop):
        """Asyncio test method."""
        class lightStatus(object):
            """Callback class to capture state changes."""

            lightOnLevel1 = None
            lightOnLevel2 = None

            def device_status_callback1(self, device_id, state, value):
                """Callback method to capture upper outlet changes."""
                self.lightOnLevel1 = value

            def device_status_callback2(self, device_id, state, value):
                """Callback method to capture lower outlet changes."""
                self.lightOnLevel2 = value

        mockPLM = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'

        cat = 0x02
        subcat = 0x0d
        product_key = None
        description = 'ToggleLinc Relay'
        model = '2466S'

        callbacks = lightStatus()

        device = SwitchedLightingControl_2663_222.create(
            mockPLM, address, cat, subcat, product_key, description, model)

        assert device.states[0x01].name == 'outletTopOnOff'
        assert device.states[0x02].name == 'outletBottomOnOff'

        device.states[0x01].register_updates(callbacks.device_status_callback1)
        device.states[0x02].register_updates(callbacks.device_status_callback2)

        device.states[0x02].async_refresh_state()
        yield from asyncio.sleep(.1, loop)
        ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01,
                              acknak=MESSAGE_ACK)
        statusmsg = StandardReceive(
            address, target, {'cmd1': 0x03, 'cmd2': 0x01},
            flags=MessageFlags.create(MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
                                      0, 2, 3))
        mockPLM.message_received(ackmsg)
        yield from asyncio.sleep(.1, loop)
        mockPLM.message_received(statusmsg)
        yield from asyncio.sleep(.1, loop)
        assert callbacks.lightOnLevel2 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
