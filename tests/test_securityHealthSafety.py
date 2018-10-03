"""Test Security Health and Safety devices."""
import asyncio
import logging

from insteonplm.constants import (COMMAND_LIGHT_OFF_0X13_0X00,
                                  COMMAND_LIGHT_ON_0X11_NONE,
                                  MESSAGE_FLAG_BROADCAST_0X80,
                                  MESSAGE_TYPE_ALL_LINK_BROADCAST)
from insteonplm.devices.securityHealthSafety import (
    SecurityHealthSafety, SecurityHealthSafety_2842_222,
    SecurityHealthSafety_2845_222, SecurityHealthSafety_2852_222,
    SecurityHealthSafety_2982_222)
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from .mockPLM import MockPLM
from .mockCallbacks import MockCallbacks

_LOGGING = logging.getLogger(__name__)
_LOGGING.setLevel(logging.DEBUG)


async def _onOffSenorTest(onOffClass, loop):
    """Test on/off sensor."""
    plm = MockPLM(loop=loop)
    address = '1a2b3c'
    target = bytearray([0x00, 0x00, 0x01])

    cat = 0x10
    subcat = 0x00
    product_key = 0x00
    description = 'Generic Security, Heath and Safety Device'
    model = ''

    callbacks = MockCallbacks()

    device = onOffClass(plm, address, cat, subcat, product_key,
                        description, model)
    plm.devices[address] = device
    device.states[0x01].register_updates(callbacks.callbackmethod1)
    msg = StandardReceive(
        address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x01,
        flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 3, 3))
    plm.message_received(msg)
    await asyncio.sleep(.1, loop=loop)
    assert callbacks.callbackvalue1 == 1

    device = onOffClass(plm, address, cat, subcat, product_key,
                        description, model)
    device.states[0x01].register_updates(callbacks.callbackmethod1)
    msg = StandardReceive(
        address, target, COMMAND_LIGHT_OFF_0X13_0X00,
        flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST, 0, 3, 3))
    plm.message_received(msg)
    await asyncio.sleep(.1, loop=loop)
    assert callbacks.callbackvalue1 == 0


def test_securityhealthsafety():
    """Test generic Securityhealthsafety devices."""
    async def run_test(loop):
        """Asyncio coroutine to actually run the test."""
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = bytearray([0x00, 0x00, 0x01])
        cmd2 = 0x01

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = SecurityHealthSafety(plm, address, cat, subcat,
                                      product_key, description, model)
        plm.devices[address] = device
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(
            address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 3, 3))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == cmd2

        device = SecurityHealthSafety(plm, address, cat, subcat,
                                      product_key, description, model)
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(
            address, target, COMMAND_LIGHT_OFF_0X13_0X00,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 3, 3))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x00

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_securityhealthsafety_2982_222():
    """Test device 2982-222."""
    async def run_test(loop):
        plm = MockPLM(loop)
        address = '1a2b3c'
        target = '4d5e6f'
        cmd2 = 0x04

        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = SecurityHealthSafety_2982_222(plm, address, cat, subcat,
                                               product_key, description, model)
        plm.devices[address] = device
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        msg = StandardReceive(
            address, target, COMMAND_LIGHT_ON_0X11_NONE, cmd2=cmd2,
            flags=MessageFlags.create(MESSAGE_FLAG_BROADCAST_0X80, 0, 0, 0))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0x6f

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_securityHealthSafety_2842_222():
    """Test 2842-222."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _onOffSenorTest(SecurityHealthSafety_2842_222, loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_securityHealthSafety_2845_2222():
    """Test device 2845-222."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _onOffSenorTest(SecurityHealthSafety_2845_222, loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)


def test_securityHealthSafety_2852_222():
    """Test device 2852-222."""
    async def _run_test(loop):
        """Test on/off sensor."""
        plm = MockPLM(loop)

        address = '1a2b3c'
        cat = 0x10
        subcat = 0x00
        product_key = 0x00
        description = 'Generic Security, Heath and Safety Device'
        model = ''

        callbacks = MockCallbacks()

        device = SecurityHealthSafety_2852_222(plm, address, cat, subcat,
                                               product_key, description, model)
        plm.devices[address] = device
        device.states[0x01].register_updates(callbacks.callbackmethod1)
        device.states[0x02].register_updates(callbacks.callbackmethod2)
        device.states[0x04].register_updates(callbacks.callbackmethod4)

        # Test Dry message received
        msg = StandardReceive(
            address=address,
            target=bytearray([0x00, 0x00, 0x01]),
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x01,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 3, 3))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 1
        assert callbacks.callbackvalue2 == 0
        assert callbacks.callbackvalue4 == 0x11

        # Test wet message received
        msg = StandardReceive(
            address=address,
            target=bytearray([0x00, 0x00, 0x02]),
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x02,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 3, 3))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0
        assert callbacks.callbackvalue2 == 1
        assert callbacks.callbackvalue4 == 0x13

        # Test dry heartbeat received
        msg = StandardReceive(
            address=address,
            target=bytearray([0x00, 0x00, 0x04]),
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE, cmd2=0x04,
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 3, 3))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 1
        assert callbacks.callbackvalue2 == 0

        # Test wet heartbeat received
        msg = StandardReceive(
            address=address,
            target=bytearray([0x00, 0x00, 0x04]),
            commandtuple={'cmd1': 0x13, 'cmd2': 0x04},
            flags=MessageFlags.create(MESSAGE_TYPE_ALL_LINK_BROADCAST,
                                      0, 3, 3))
        plm.message_received(msg)
        await asyncio.sleep(.1, loop=loop)
        assert callbacks.callbackvalue1 == 0
        assert callbacks.callbackvalue2 == 1
        assert callbacks.callbackvalue4 == 0x13

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run_test(loop))
    open_tasks = asyncio.Task.all_tasks(loop=loop)

    for task in open_tasks:
        if hasattr(task, 'name'):
            _LOGGING.error('Device: %s Task: %s', task.name, task)
        else:
            _LOGGING.error('Task: %s', task)
        if not task.done():
            loop.run_until_complete(task)
