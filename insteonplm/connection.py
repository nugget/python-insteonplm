"""Module containing the connection wrapper for the PLM interface."""
import asyncio
import logging
import serial
import serial.aio

from .protocol import PLM

__all__ = ('Connection')

try:
    ensure_future = asyncio.ensure_future
except:
    ensure_future = asyncio.async


class Connection:
    """Handler to maintain the Powerline device connection."""

    def __init__(self):
        """Instantiate the Connection object."""
        self.log = logging.getLogger(__name__)

    @classmethod
    @asyncio.coroutine
    def create(cls, device='/dev/ttyUSB0',
               auto_reconnect=True, loop=None, protocol_class=PLM,
               update_callback=None):
        """Initiate a connection to a specific device.

        Here is where we supply the device and callback callables we
        expect for this PLM class object.

        :param device:
            Unix device where the PLM is attached
        :param auto_reconnect:
            Should the Connection try to automatically reconnect if needed?
        :param loop:
            asyncio.loop for async operation
        :param update_callback"
            This function is called whenever PLM state data changes

        :type device:
            str
        :type auto_reconnect:
            boolean
        :type loop:
            asyncio.loop
        :type update_callback:
            callable
        """
        conn = cls()

        conn.device = device
        conn._loop = loop or asyncio.get_event_loop()
        conn._retry_interval = 1
        conn._closed = False
        conn._closing = False
        conn._halted = False
        conn._auto_reconnect = auto_reconnect

        def connection_lost():
            """Function callback for Protocoal class when connection is lost."""
            if conn._auto_reconnect and not conn._closing:
                ensure_future(conn._reconnect(), loop=conn._loop)

        conn.protocol = protocol_class(
            connection_lost_callback=connection_lost, loop=conn._loop,
            update_callback=update_callback)

        yield from conn._reconnect()

        return conn

    @property
    def transport(self):
        """Return pointer to the transport object.

        Use this property to obtain passthrough access to the underlying
        Protocol properties and methods.
        """
        return self.protocol.transport

    def _get_retry_interval(self):
        return self._retry_interval

    def _reset_retry_interval(self):
        self._retry_interval = 1

    def _increase_retry_interval(self):
        self._retry_interval = min(300, 1.5 * self._retry_interval)

    @asyncio.coroutine
    def _reconnect(self):
        while True:
            try:
                if self._halted:
                    yield from asyncio.sleep(2, loop=self._loop)
                else:
                    self.log.info('Connecting to PLM on %s',
                                  self.device)
                    yield from serial.aio.create_serial_connection(self._loop,
                        lambda: self.protocol, self.device, baudrate=19200)
                    self._reset_retry_interval()
                    return

            except OSError as e:
                self._increase_retry_interval()
                interval = self._get_retry_interval()
                self.log.warning('Connecting failed, retry in %i seconds: %s',
                              interval, device)
                yield from asyncio.sleep(interval, loop=self._loop)

    def close(self):
        """Close the PLM device connection and don't try to reconnect."""
        self.log.warning('Closing connection to PLM')
        self._closing = True
        if self.protocol.transport:
            self.protocol.transport.close()

    def halt(self):
        """Close the PLM device connection and wait for a resume() request."""
        self.log.warning('Halting connection to PLM')
        self._halted = True
        if self.protocol.transport:
            self.protocol.transport.close()

    def resume(self):
        """Resume the PLM device connection if we have been halted."""
        self.log.warning('Resuming connection to PLM')
        self._halted = False

    @property
    def dump_conndata(self):
        """Developer tool for debugging forensics."""
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())
