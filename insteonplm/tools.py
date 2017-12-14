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
        log.warn('New Device: %s', device)

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

    if 1 == 1:
        device = conn.protocol.devices.get_device('14627a')
        device.Light_Turn_On()
        yield from asyncio.sleep(5, loop=loop)
        device.Light_Turn_Off()

    if 1 == 0:
        conn.protocol.turn_on('4095e6', ramprate=2)
        yield from asyncio.sleep(5, loop=loop)


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
