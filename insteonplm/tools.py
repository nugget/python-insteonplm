"""Provides a raw console to test module and demonstrate usage."""
import argparse
import asyncio
import logging

import insteonplm

__all__ = ('console', 'monitor')


@asyncio.coroutine
def console(loop, log):
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

    def log_callback(message):
        """Receives event callback from PLM Protocol class."""
        log.info('Callback invoked: %s', message)

    device = args.device

    log.info('Connecting to Insteon PLM at %s', device)

    conn = yield from insteonplm.Connection.create(
        device=device, loop=loop, update_callback=log_callback)

    yield from asyncio.sleep(2, loop=loop)


def monitor():
    """Wrapper to call console with a loop."""
    log = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    asyncio.async(console(loop, log))
    loop.run_forever()
