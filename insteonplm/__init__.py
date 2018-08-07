"""Insteon Powerline Modem Interface Module.

This module provides a unified asyncio network handler for interacting with
Insteon Powerline modems like the 2413U and 2412S.
"""
import aiohttp
import asyncio
import binascii
from contextlib import suppress
import logging
import serial
from serial.aio import create_serial_connection

from insteonplm.plm import PLM, Hub

__all__ = ('Connection')
_LOGGER = logging.getLogger(__name__)

# pylint: disable=invalid-name,no-member
try:
    ensure_future = asyncio.ensure_future
except AttributeError:
    ensure_future = asyncio.async


@asyncio.coroutine
def create_http_connection(loop, protocol_factory, host, port=25105,
                           auth=None, connector=None):
    session = aiohttp.ClientSession(auth=auth, connector=connector)
    protocol = protocol_factory()
    transport = HttpTransport(loop, protocol, session, host, port)
    _LOGGER.debug("create_http_connection Finished creating connection")
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
        _LOGGER.debug("Starting Connection.create")
        conn = cls()

        conn.device = device
        conn.host = host
        conn.username = username
        conn.password = password
        conn.port = port
        conn._loop = loop or asyncio.get_event_loop()
        conn._retry_interval = 1
        conn._closed = True
        conn._closing = False
        conn._halted = False
        conn._auto_reconnect = auto_reconnect

        def connection_lost():
            """Function callback for Protocol when connection is lost."""
            if conn._auto_reconnect and not conn._closing:
                _LOGGER.debug("Reconnecting to transport")
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

        _LOGGER.debug("Ending Connection.create")
        return conn

    @property
    def transport(self):
        """Return pointer to the transport object.

        Use this property to obtain passthrough access to the underlying
        Protocol properties and methods.
        """
        return self.protocol.transport

    def _reset_retry_interval(self):
        self._retry_interval = 1

    def _increase_retry_interval(self):
        self._retry_interval = min(300, 1.5 * self._retry_interval)

    @asyncio.coroutine
    def _reconnect(self):
        _LOGGER.debug('starting Connection._reconnect')
        yield from self._connect()
        while self._closed:
            yield from self._retry_connection()
        _LOGGER.debug('ending Connection._reconnect')

    @asyncio.coroutine
    def close(self, event):
        """Close the PLM device connection and don't try to reconnect."""
        print('Will this show up???')
        _LOGGER.warning('Closing connection to PLM')
        self._closing = True
        self._auto_reconnect = False
        yield from self.protocol.close()
        if self.protocol.transport:
            self.protocol.transport.close()
        yield from asyncio.sleep(0, loop=self._loop)
        _LOGGER.warning('PLM Closed...')

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

    @asyncio.coroutine
    def _retry_connection(self):
        _LOGGER.debug('starting Connection._retry_connection')
        device = self.host if self.host else self.device
        self._increase_retry_interval()
        _LOGGER.warning('Connection failed, retry in %i seconds: %s',
                        self._retry_interval, device)
        yield from asyncio.sleep(self._retry_interval, loop=self._loop)
        _LOGGER.debug('Starting _connect')
        yield from self._connect()
        _LOGGER.debug('ending Connection._retry_connection')

    @asyncio.coroutine
    def _connect(self):
        _LOGGER.debug('starting Connection._connect')
        if self.host:
            connected = yield from self._connect_http()
        else:
            connected =  yield from self._connect_serial()
        _LOGGER.debug('ending Connection._connect')
        return connected

    @asyncio.coroutine
    def _connect_http(self):
        _LOGGER.info('Connecting to Hub on %s', self.host)
        auth = aiohttp.BasicAuth(self.username, self.password)
        connector = aiohttp.TCPConnector(
            limit=1, loop=self._loop, keepalive_timeout=10)
        _LOGGER.debug('Creating http connection')
        transport, protocol = yield from create_http_connection(
            self._loop, lambda: self.protocol,
            self.host, port=self.port,
            auth=auth, connector=connector)
        connected = yield from transport.test_connection()
        if connected:
            transport.resume_reading()
        self._closed = not connected
        return connected

    @asyncio.coroutine
    def _connect_serial(self):
        _LOGGER.info('Connecting to PLM on %s', self.device)
        try:
            transport, protocol = yield from create_serial_connection(
                self._loop, lambda: self.protocol,
                self.device, baudrate=19200)
            self._closed = False
        except OSError:
            self._closed = True
        return not self._closed


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
        self._restart_reader = True
        _LOGGER.debug("Starting the reader in HttpTrasnport __init__")
        self._reader_task = None

    def abort(self):
        self._session.close()

    def can_write_eof(self):
        return False

    def is_closing(self):
        return self._closing

    def close(self):
        _LOGGER.debug("Closing Hub session")
        asyncio.ensure_future(self._close(), loop=self._loop)

    @asyncio.coroutine
    def _close(self):
        self._closing = True
        yield from self._session.close()
        yield from asyncio.sleep(0, loop=self._loop)
        _LOGGER.info("Hub Session closed")

    def get_write_buffer_size(self):
        return 0

    def pause_reading(self):
        asycnio.ensure_future(self._stop_reader(False), loop=self._loop)

    def resume_reading(self):
        self._restart_reader = True
        self._start_reader()

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
    def test_connection(self):
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        try:
            response = yield from self._session.get(url, timeout=5)
            if response and response.status == 200:
                _LOGGER.debug('Test connection status is %d', response.status)
                return True
            else:
                self._log_error(response.status)
        except Exception as e:
            _LOGGER.error('An unknown error occured: %s', str(e))
        _LOGGER.debug('Connection test failed')
        self.close()
        return False

    @asyncio.coroutine
    def _async_write(self, url):
        return_status = 500
        if self._session.closed:
            _LOGGER.warning("Session closed, cannot write to Hub")
            return
        _LOGGER.debug("Writing message: %s", url)
        try:
            yield from self._read_write_lock
            response = yield from self._session.post(url, timeout=5)
            return_status = response.status
            _LOGGER.debug("Post status: %s", response.status)
            if response.status == 200:
                self._write_last_read(0)
            else:
                self._log_error(response.status)
                yield from self._stop_reader(False)
        except aiohttp.client_exceptions.ServerDisconnectedError:
            _LOGGER.error('Reconnect to Hub (ServerDisconnectedError)')
            yield from self._stop_reader(True)
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error('Reconnect to Hub (ClientConnectorError)')
            yield from self._stop_reader(True)
        except asyncio.TimeoutError:
            _LOGGER.error('Reconnect to Hub (TimeoutError)')
            yield from self._stop_reader(True)


        if self._read_write_lock.locked():
            self._read_write_lock.release()
        return return_status

    def write_eof(self):
        raise NotImplementedError(
            "HTTP connections do not support end-of-file")

    def writelines(self, list_of_data):
        raise NotImplementedError(
            "HTTP connections do not support writelines")

    def clear_buffer(self):
        """Clear the Hub read buffer."""
        asyncio.wait(self._clear_buffer())

    @asyncio.coroutine
    def _clear_buffer(self):
        _LOGGER.debug("..................Clearing the buffer..............")
        url = 'http://{:s}:{:d}/1?XB=M=1'.format(self._host, self._port)
        yield from self._async_write(url)

    @asyncio.coroutine
    def _ensure_reader(self):
        _LOGGER.info('Hub reader started')
        yield from self._clear_buffer()
        self._write_last_read(0)
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        _LOGGER.debug('Calling connection made')
        self._loop.call_soon(self._protocol.connection_made(self))
        while self._restart_reader:
            try:
                if self._session.closed:
                    yield from self._stop_reader(False)
                    return
                yield from self._read_write_lock
                last_stop = 0
                if not self._last_read.empty():
                    last_stop = self._last_read.get_nowait()
                response = yield from self._session.get(url, timeout=5)
                buffer = None
                # _LOGGER.debug("Reader status: %d", response.status)
                if response.status == 200:
                    html = yield from response.text()
                    last_stop, buffer = self._parse_buffer(html, last_stop)
                    self._write_last_read(last_stop)
                else:
                    self._log_error(response.status)
                    yield from self._stop_reader(False)
                # TODO: handle other status codes
                if self._read_write_lock.locked():
                    self._read_write_lock.release()
                if buffer:
                    _LOGGER.debug('New buffer: %s', buffer)
                    bin_buffer = binascii.unhexlify(buffer)
                    self._protocol.data_received(bin_buffer)
                yield from asyncio.sleep(1, loop=self._loop)
            
            except asyncio.CancelledError:
                _LOGGER.debug('Stop connection to Hub (loop stopped)')
                yield from self._stop_reader(False)
            except GeneratorExit:
                _LOGGER.debug('Stop connection to Hub (GeneratorExit)')
                yield from self._stop_reader(False)
            except aiohttp.client_exceptions.ServerDisconnectedError:
                _LOGGER.debug('Reconnect to Hub (ServerDisconnectedError)')
                yield from self._stop_reader(True)
            except aiohttp.client_exceptions.ClientConnectorError:
                _LOGGER.debug('Reconnect to Hub (ClientConnectorError)')
                yield from self._stop_reader(True)
            except asyncio.TimeoutError:
                _LOGGER.error('Reconnect to Hub (TimeoutError)')
                yield from self._stop_reader(True)
            except Exception as e:
                _LOGGER.debug('Stop reading due to %s', str(e))
                yield from self._stop_reader(False)
        _LOGGER.info('Hub reader stopped')
        return

    def _parse_buffer(self, html, last_stop):
        buffer = ''
        raw_text = html.replace('<response><BS>', '')
        raw_text = raw_text.replace('</BS></response>', '')
        raw_text = raw_text.strip()
        if raw_text[:200] == '0'*200:
            # Likely the buffer was cleared
            return (0, None)
        this_stop = int(raw_text[-2:], 16)
        if this_stop > last_stop:
            _LOGGER.debug('Buffer from %d to %d', last_stop, this_stop)
            buffer = raw_text[last_stop:this_stop]
        elif this_stop < last_stop:
            _LOGGER.debug('Buffer from %d to 200 and 0 to %d',
                          last_stop, this_stop)
            buffer_hi = raw_text[last_stop:200]
            if buffer_hi == '0'*len(buffer_hi):
                # The buffer was probably reset since the last read
                buffer_hi = ''
            buffer_low = raw_text[0:this_stop]
            buffer = '{:s}{:s}'.format(buffer_hi, buffer_low)
        else:
            buffer = None
        return (this_stop, buffer)

    def _write_last_read(self, val):
        while not self._last_read.empty():
            self._last_read.get_nowait()
        self._last_read.put_nowait(val)

    def _start_reader(self, future=None):
        if self._restart_reader:
            _LOGGER.debug("Starting the buffer reader")
            self._reader_task = asyncio.ensure_future(self._ensure_reader(),
                                                      loop=self._loop)
            self._reader_task.add_done_callback(self._start_reader)

    @asyncio.coroutine
    def _stop_reader(self, reconnect=False):
        _LOGGER.debug('Stopping the reader and reconnect is %s', reconnect)
        self._restart_reader = False
        if self._reader_task:
            self._reader_task.remove_done_callback(self._start_reader)
            self._reader_task.cancel()
            with suppress(asyncio.CancelledError):
                yield from self._reader_task
                yield from ascynio.sleep(0, loop=self._loop)
        self._protocol.pause_writing()
        if not self._session.closed:
            _LOGGER.debug('Session is open so we close it')
            yield from self._close()
        if reconnect:
            _LOGGER.debug("We want to reconnect so we do...")
            self._protocol.connection_lost(True)

    def _log_error(self, error):
        # TODO: handle other status codes
        if response.status == 401:
            _LOGGER.error('Athentication error, check your configuration')
            _LOGGER.error('If configuration is correct and restart the Hub')
            _LOGGER.error('System must be restared to reconnect to hub')
        elif response.status == 404:
            _LOGGER.error('Hub not found at http://%s:%d, check configuration',
                          self._host, self._port)
        elif response.status in range(500, 600):
            _LOGGER.error('Hub returned a server error')
            _LOGGER.error('Restart the Hub and try again')
        else:
            _LOGGER.error('An unknown error has occured')
            _LOGGER.error('Check the configuration and restart the Hub and '
                          'the application')
