"""Insteon Powerline Modem Interface Module.

This module provides a unified asyncio network handler for interacting with
Insteon Powerline modems like the 2413U and 2412S.
"""
import aiohttp
import asyncio
import binascii
import logging
import serial
import serial.aio

from insteonplm.plm import PLM, Hub

__all__ = ('Connection')
_LOGGER = logging.getLogger()

# pylint: disable=invalid-name,no-member
try:
    ensure_future = asyncio.ensure_future
except AttributeError:
    ensure_future = asyncio.async


@asyncio.coroutine
def create_http_connection(loop, protocol_factory, host, port=25105,
                           auth=None, connector=None):
    _LOGGER.debug("auth: %s", auth)
    session = aiohttp.ClientSession(auth=auth, connector=connector)
    protocol = protocol_factory()
    transport = HttpTransport(loop, protocol, session, host, port)
    return (transport, protocol)


class Connection:
    """Handler to maintain the Powerline device connection."""

    @classmethod
    @asyncio.coroutine
    def create(cls, device='/dev/ttyUSB0', host=None,
               username=None, password=None, port=25010,
               auto_reconnect=True, loop=None, workdir=None,
               poll_devices=True):
        """Initiate a connection to a specific device.

        Here is where we supply the device and callback callables we
        expect for this PLM class object.

        :param device:
            Unix device where the PLM is attached
        :param address:
            IP Address of the Hub
        :param username:
            User name for connecting to the Hub
        :param password:
            Password for connecting to the Hub
        :param auto_reconnect:
            Should the Connection try to automatically reconnect if needed?
        :param loop:
            asyncio.loop for async operation

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
        conn.host = host
        conn.username = username
        conn.password = password
        conn.port = port
        conn._loop = loop or asyncio.get_event_loop()
        conn._retry_interval = 1
        conn._closed = False
        conn._closing = False
        conn._halted = False
        conn._auto_reconnect = auto_reconnect

        def connection_lost():
            """Function callback for Protocol when connection is lost."""
            if conn._auto_reconnect and not conn._closing:
                ensure_future(conn._reconnect(), loop=conn._loop)

        protocol_class = PLM
        if conn.host:
            protocol_class = Hub
        conn.protocol = protocol_class(
            connection_lost_callback=connection_lost,
            loop=conn._loop,
            workdir=workdir,
            poll_devices=poll_devices)

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

    # TODO:
    # This code need to change to handle serial or HTTP connections.
    @asyncio.coroutine
    def _reconnect(self):
        while True:
            try:
                if self._halted:
                    yield from asyncio.sleep(2, loop=self._loop)
                else:
                    if self.host:
                        _LOGGER.info('Connecting to Hub on %s', self.host)
                        hub_loop = asyncio.new_event_loop()
                        auth = aiohttp.BasicAuth(self.username, self.password)
                        connector = aiohttp.TCPConnector(
                            limit=1, loop=self._loop, keepalive_timeout=10)
                        yield from create_http_connection(
                            self._loop, lambda: self.protocol,
                            self.host, port=self.port,
                            auth=auth, connector=connector)
                    else:
                        _LOGGER.info('Connecting to PLM on %s', self.device)
                        yield from serial.aio.create_serial_connection(
                            self._loop, lambda: self.protocol,
                            self.device, baudrate=19200)
                        self._reset_retry_interval()
                    return

            except OSError:
                self._increase_retry_interval()
                interval = self._get_retry_interval()
                _LOGGER.warning('Connecting failed, retry in %i seconds: %s',
                                 interval, self.device)
                yield from asyncio.sleep(interval, loop=self._loop)

    def close(self):
        """Close the PLM device connection and don't try to reconnect."""
        _LOGGER.warning('Closing connection to PLM')
        self._closing = True
        if self.protocol.transport:
            self.protocol.transport.close()

    def halt(self):
        """Close the PLM device connection and wait for a resume() request."""
        _LOGGER.warning('Halting connection to PLM')
        self._halted = True
        if self.protocol.transport:
            self.protocol.transport.close()

    def resume(self):
        """Resume the PLM device connection if we have been halted."""
        _LOGGER.warning('Resuming connection to PLM')
        self._halted = False

    @property
    def dump_conndata(self):
        """Developer tool for debugging forensics."""
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())


class HttpTransport(asyncio.Transport):
    """An asyncio transport model of an HTTP communication channel.

    A transport class is an abstraction of a communication channel.
    This allows protocol implementations to be developed against the
    transport abstraction without needing to know the details of the
    underlying channel, such as whether it is a pipe, a socket, or
    indeed an HTTP connection.


    You generally won’t instantiate a transport yourself; instead, you
    will call `create_http_connection` which will create the
    transport and try to initiate the underlying communication channel,
    calling you back when it succeeds.
    """

    def __init__(self, loop, protocol, session, host, port=25105):
        """Initialize the HttpTransport class."""
        super().__init__()
        self._loop = loop
        self._protocol = protocol
        self._session = session
        self._host = host
        self._port = port

        self._closing = False
        self._protocol_paused = False
        self._max_read_size = 1024
        self._write_buffer = []
        self._has_reader = False
        self._has_writer = False
        self._poll_wait_time = 0.0005
        self._read_write_lock = asyncio.Lock(loop=self._loop)
        self._last_read = asyncio.Queue(loop=self._loop)

        asyncio.ensure_future(self.ensure_reader(), loop=self._loop)
        

    def abort(self):
        self._session.close()

    def can_write_eof(self):
        return False

    def close(self):
        asyncio.wait(self._close(), loop=self._loop)

    @asyncio.coroutine
    def _close(self):
        _LOGGER.debug("Closing session")
        yield from self._session.close()
        self._closing = True
        _LOGGER.debug("Session closed")

    def get_write_buffer_size(self):
        return 0

    def pause_reading(self):
        self._loop.call_soon(self._lock_read, True)

    def resume_reading(self):
        self._loop.call_soon(self._lock_read, False)

    def set_write_buffer_limits(self, high=None, low=None):
        raise NotImplementedError(
            "HTTP connections do not support write buffer limits")

    def write(self, data):
        _LOGGER.debug("..................Writing a message..............")
        hex_data = binascii.hexlify(data).decode()
        url = 'http://{:s}:{:d}/3?{:s}=I=3'.format(self._host, self._port,
                                                   hex_data)
        coro_write = self._async_write(url)
        asyncio.ensure_future(coro_write, loop=self._loop)

    @asyncio.coroutine
    def _async_write(self, url):
        _LOGGER.debug("Writing message: %s", url)
        yield from self._read_write_lock
        yield from self._session.post(url)
        self._write_last_read(0)
        if self._read_write_lock.locked():
            self._read_write_lock.release()

    def write_eof(self):
        raise NotImplementedError(
            "HTTP connections do not support end-of-file")

    def writelines(self, list_of_data):
        raise NotImplementedError(
            "HTTP connections do not support writelines")

    def clear_buffer(self):
        asyncio.wait(self._clear_buffer())

    @asyncio.coroutine
    def _clear_buffer(self):
        _LOGGER.debug("..................Clearing the buffer..............")
        url = 'http://{:s}:{:d}/1?XB=M=1'.format(self._host, self._port)
        yield from self._async_write(url)

    @asyncio.coroutine
    def ensure_reader(self):
        yield from self._clear_buffer()
        self._write_last_read(0)
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        self._loop.call_soon(self._protocol.connection_made(self))
        while True:
            yield from self._read_write_lock
            last_stop = 0
            if not self._last_read.empty():
                last_stop = self._last_read.get_nowait()
            response = yield from self._session.get(url)
            html = yield from response.text()
            last_stop, buffer = self._parse_buffer(html, last_stop)
            self._write_last_read(last_stop)
            if self._read_write_lock.locked():
                self._read_write_lock.release()
            if buffer:
                _LOGGER.debug('New buffer: %s', buffer)
                bin_buffer = binascii.unhexlify(buffer)
                self._protocol.data_received(bin_buffer)
            yield from asyncio.sleep(1, loop=self._loop)

    def _parse_buffer(self, html, last_stop):
        buffer = ''
        raw_text = html.replace('<response><BS>', '')
        raw_text = raw_text.replace('</BS></response>', '')
        raw_text = raw_text.strip()
        this_stop = int(raw_text[-2:], 16)
        if this_stop > last_stop:
            _LOGGER.debug('Buffer from %d to %d', last_stop, this_stop)
            buffer = raw_text[last_stop:this_stop]
        elif this_stop < last_stop:
            _LOGGER.debug('Buffer from %d to 200 and 0 to %d',
                          last_stop, this_stop)
            buffer_hi = raw_text[last_stop:200]
            buffer_low = raw_text[0:this_stop]
            buffer = '{:s}{:s}'.format(buffer_hi, buffer_low)
        else:
            buffer = None
        yield this_stop
        yield buffer

    def _write_last_read(self, val):
        while not self._last_read.empty():
            not_used = self._last_read.get_nowait()
        self._last_read.put_nowait(val)
