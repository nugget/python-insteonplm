"""Provides a raw console to test module and demonstrate usage."""
import argparse
import asyncio
import logging

import insteonplm

__all__ = ('console', 'monitor')


@asyncio.coroutine
def console(loop, log, devicelist):
    """Connect to receiver and show events as they occur.

    Pulls the following arguments from the command line (not method arguments):

    :param device:
        Unix device where the PLM is attached
    :param verbose:
        Show debug logging.
    """
    parser = argparse.ArgumentParser(description=console.__doc__)
    parser.add_argument('--device', default='/dev/ttyUSB0', help='Device')
    parser.add_argument('--verbose', '-v', action='count')

    args = parser.parse_args()

    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)

    device = args.device

    log.info('Connecting to Insteon PLM at %s', device)

    conn = yield from insteonplm.Connection.create(device=device, loop=loop, userdefined=devicelist)

    def async_insteonplm_add_device_callback(device):
        """Log that our new device callback worked."""
        log.warn('New Device: %s %02x %02x %s, %s', device.id, device.cat, device.subcat, device.description, device.model)
        for state in device.states:
            device.states[state].register_updates(async_state_change_callback)

    def async_state_change_callback(id, state, value):
        log.info('Device %s state %s value is changed to %02x', id, state, value)

    criteria = {}
    conn.protocol.add_device_callback(async_insteonplm_add_device_callback)

    plm = conn.protocol

    yield from asyncio.sleep(240, loop=loop)

    if 1 == 1:
        device = plm.devices['14627a']
        device.states[0x01].off()

        log.debug('Sent office light off request')
        log.debug('----------------------')
        yield from asyncio.sleep(5, loop=loop)

        device.states[0x01].on()
        log.debug('Sent office light on request')
        log.debug('----------------------')

    if 1 == 0:
        for key in plm.devices:
            log.debug('Address: %s', key)
        yield from asyncio.sleep(5, loop=loop)

    if 1 == 1:
        # Test Top Outlet
        device = plm.devices['4189cf']
        device.states[0x01].off()

        log.debug('Sent top outlet off request')
        log.debug('----------------------')
        yield from asyncio.sleep(5, loop=loop)

        device.states[0x01].on()
        log.debug('Sent top outlet on request')
        log.debug('----------------------')
        
        # Test Bottom Outlet
        device.states[0x02].off()

        log.debug('Sent bottom outlet off request')
        log.debug('----------------------')
        yield from asyncio.sleep(5, loop=loop)
        
        device.states[0x02].on()
        log.debug('Sent bottom outlet on request')
        log.debug('----------------------')

    if 1 == 1:
        # Test Status Request message
        state1 = plm.devices['4189cf'].states[0x01]
        state2 = plm.devices['4189cf'].states[0x02]

        log.debug('Setting top outlet off and bottom outlet on')
        log.debug('----------------------')
        state1.off()
        state2.on()
        yield from asyncio.sleep(5, loop=loop)
        
        log.debug('Sent top outlet status request')
        log.debug('----------------------')
        state1.async_refresh_state()
        yield from asyncio.sleep(5, loop=loop)
        
        log.debug('Sent top and bottom outlet status request')
        log.debug('----------------------')
        state2.async_refresh_state()
        yield from asyncio.sleep(5, loop=loop)

        log.debug('Turn Bottom outlet off')
        log.debug('----------------------')
        state2.off()
        yield from asyncio.sleep(5, loop=loop)

        
        log.debug('Sent light status request')
        log.debug('----------------------')
        state2.async_refresh_state()

        yield from asyncio.sleep(5, loop=loop)


        log.debug('Turn Bottom outlet on')
        log.debug('----------------------')
        state2.on()


def monitor():
    """Wrapper to call console with a loop."""
    devicelist = (
        {
            "address": "3c4fc5",
            "cat": 0x05,
            "subcat": 0x0b,
            "firmware": 0x00
        },
        {
            "address": "43af9b",
            "cat": 0x02,
            "subcat": 0x1a,
            "firmware": 0x00
        }
    )
    log = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    asyncio.async(console(loop, log, devicelist))
    loop.run_forever()
