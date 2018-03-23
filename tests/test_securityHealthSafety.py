"""Test Security Health and Saftey devices."""
import asyncio

from insteonplm.constants import (COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  MESSAGE_FLAG_BROADCAST_0X80,
                                  MESSAGE_TYPE_ALL_LINK_CLEANUP)
from insteonplm.devices.securityHealthSafety import (
    SecurityHealthSafety, SecurityHealthSafety_2842_222,
    SecurityHealthSafety_2845_222, SecurityHealthSafety_2852_222,
    SecurityHealthSafety_2982_222)
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks


@asyncio.coroutine
def _onOffSenorTest(onOffClass, loop):
    """Test on/off sensor."""
    plm = MockPLM()
    address = '1a2b3c'
    target = '4d5e6f'
    cmd2 = 0x04

    cat = 0x10
    subcat = 0x00
    product_key = 0x00
    description = 'Generic Security, Heath and Safety Device'
    model = ''

    callbacks = MockCallbacks()

    device = onOffClass.create(plm, address, cat, subcat, product_key,
                               description, model)
    device.states[0x01].register_updates(callbacks.callbackmethod1)
    msg = StandardReceive(
        address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2,
        flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
    plm.message_received(msg)
    yield from asyncio.sleep(.1, loop=loop)
    assert callbacks.callbackvalue1 == 1

    device = onOffClass.create(plm, address, cat, subcat, product_key,
                               description, model)
    device.states[0x01].register_updates(callbacks.callbackmethod1)
    msg = StandardReceive(
        address, target, COMMAND_LIGHT_OFF_0X13_0X00,
        flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
    plm.message_received(msg)
    yield from asyncio.sleep(.1, loop=loop)
    assert callbacks.callbackvalue1 == 0


def test_securityhealthsafety():
    """Test generic Securityhealthsafety devices."""
    @asyncio.coroutine
    def run_test(loop):
        """Asyncio coroutine to actually run the test."""
        class sensorState(object):
            """Callback class to caputure sensor value changes."""

            sensor = None

            def sensor_status_callback(self, device_id, state, value):
                """Callback method to update sensor value."""
                self.sensor = value

        plm = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'
        cmd2 = 0x04

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = SecurityHealthSafety.create(plm, address, cat, subcat,
                                             product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(
            address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        plm.message_received(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == cmd2

        device = SecurityHealthSafety.create(plm, address, cat, subcat,
                                             product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(
            address, target, COMMAND_LIGHT_OFF_0X13_0X00,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_CLEANUP, 0, 3, 3))
        plm.message_received(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))


def test_securityhealthsafety_2982_222():
    """Test device 2982-222."""
    plm = MockPLM()
    address = '1a2b3c'
    target = '4d5e6f'
    cmd2 = 0x04

    cat = 0x10
    subcat = 0x00
    product_key = 0x00
    description = 'Generic Security, Heath and Safety Device'
    model = ''

    callbacks = MockCallbacks()

    device = SecurityHealthSafety_2982_222.create(
        plm, address, cat, subcat, product_key, description, model)
    device.states[0x01].register_updates(callbacks.callbackmethod1)
    msg = StandardReceive(
        address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2,
        flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 0, 0))
    plm.message_received(msg)
    # target hiByte
    assert callbacks.callbackvalue1 == 0x6f


def test_securityHealthSafety_2842_222():
    """Test 2842-222."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _onOffSenorTest(SecurityHealthSafety_2842_222, loop))


def test_securityHealthSafety_2845_2222():
    """Test device 2845-222."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _onOffSenorTest(SecurityHealthSafety_2845_222, loop))


def test_securityHealthSafety_2852_222():
    """Test device 2852-222."""
    def _run_test(loop):
        """Test on/off sensor."""
        plm = MockPLM()
        address = '1a2b3c'
        target = '4d5e6f'
        cmd2 = 0x04

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = SecurityHealthSafety_2852_222.create(plm, address, cat, subcat, product_key,
                                   description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)
        device.states[0x04].register_updates(callbacks.callbackmethod4)

        # Test Dry message received
        msg = StandardReceive(
            address=address, 
            target=bytearray([0x00, 0x00, 0x01]), 
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x01,
            flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 3, 3))
        plm.message_received(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 1
        assert callbacks.callbackvalue2 == 0
        assert callbacks.callbackvalue4 == 0x11

        # Test wet message received
        msg = StandardReceive(
            address=address, 
            target=bytearray([0x00, 0x00, 0x02]), 
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x02,
            flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 3, 3))
        plm.message_received(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0
        assert callbacks.callbackvalue2 == 1
        assert callbacks.callbackvalue4 == 0x13
        
        # Test dry heartbeat received
        msg = StandardReceive(
            address=address, 
            target=bytearray([0x00, 0x00, 0x04]), 
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x04,
            flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 3, 3))
        plm.message_received(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 1
        assert callbacks.callbackvalue2 == 0
        
        # Test wet heartbeat received
        msg = StandardReceive(
            address=address, 
            target=bytearray([0x00, 0x00, 0x04]), 
            commandtuple={'cmd1': 0x13, 'cmd2': 0x04},
            flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 3, 3))
        plm.message_received(msg)
        yield from asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0
        assert callbacks.callbackvalue2 == 1
        assert callbacks.callbackvalue4 == 0x13

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _run_test(loop))
