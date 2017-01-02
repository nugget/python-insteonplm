#!/usr/bin/env python3

import asyncio
import unittest
import logging

import insteonplm

@asyncio.coroutine
def test():
    log = logging.getLogger(__name__)

    def log_callback(message):
        log.info('Callback invoked: %s' % message)

    device = '/dev/ttyUSB0'

    log.info('Connecting to PLM on %s', device)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
