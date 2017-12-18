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

    def async_insteonplm_light_callback(device):
        """Log that our new device callback worked."""
        log.warn('New Device: %s %02x %02x %s, %s', device.id, device.cat, device.subcat, device.description, device.model)

    def async_light_on_level_callback(addr, onlevel):
        log.info('Light %s turn on to level %02x', addr, onlevel)

    criteria = {}
    conn.protocol.add_device_callback(async_insteonplm_light_callback, criteria)

    plm = conn.protocol

    # yield from asyncio.sleep(5, loop=loop)
    #  Successfully turns off the light in my computer room (yay)
    #  conn.protocol._send_raw(binascii.unhexlify('02624095e6001300'))
    #
    # conn.protocol._send_raw(binascii.unhexlify('02624095e6000300'))
    # conn.protocol.product_data_request('15c3ab')
    # yield from asyncio.sleep(10, loop=loop)

    yield from asyncio.sleep(100, loop=loop)

    if 1 == 0:
        device = conn.protocol.devices['14627a']
        device.lightOnLevel.connect(async_light_on_level_callback)
        device.light_off()

        log.debug('Sent light off request')
        log.debug('----------------------')
        yield from asyncio.sleep(5, loop=loop)

        device.light_on()
        log.debug('Sent light on request')
        log.debug('----------------------')

    if 1 == 1:
        for key in conn.protocol.devices:
            log.debug('Address: %s', key)
        yield from asyncio.sleep(5, loop=loop)

    if 1 == 1:
        # Test Top Outlet
        device = conn.protocol.devices['4189cf']
        device.lightOnLevel.connect(async_light_on_level_callback)
        device.light_off()

        log.debug('Sent light off request')
        log.debug('----------------------')
        yield from asyncio.sleep(5, loop=loop)

        device.light_on()
        log.debug('Sent light on request')
        log.debug('----------------------')
        
        # Test Bottom Outlet
        device = conn.protocol.devices['4189cf_2']
        device.lightOnLevel.connect(async_light_on_level_callback)
        device.light_off()

        log.debug('Sent light off request')
        log.debug('----------------------')
        yield from asyncio.sleep(5, loop=loop)

        device.light_on()
        log.debug('Sent light on request')
        log.debug('----------------------')


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
