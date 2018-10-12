"""Insteon Powerline Modem Interface Module.

This module provides a unified asyncio network handler for interacting with
Insteon Powerline modems like the 2413U and 2412S.
"""
import asyncio
import binascii
from contextlib import suppress
import logging
import os

import aiohttp
from serial_asyncio import create_serial_connection

from insteonplm.plm import PLM, Hub

__all__ = ('Connection')
_LOGGER = logging.getLogger(__name__)


async def create_http_connection(loop, protocol_factory, host, port=25105,
                                 auth=None):
    """Create an HTTP session used to connect to the Insteon Hub."""
    protocol = protocol_factory()
    transport = HttpTransport(loop, protocol, host, port, auth)
    _LOGGER.debug("create_http_connection Finished creating connection")
    return (transport, protocol)


# pylint: disable=too-many-instance-attributes
class Connection:
    """Handler to maintain the Powerline device connection."""

    # pylint: disable=too-many-arguments
    def __init__(self, device=None, host=None, username=None, password=None,
                 port=25105, hub_version=2, loop=None, retry_interval=1,
                 auto_reconnect=True):
        """Init the Connecton class."""
        if os.name == 'nt':
            self._device = device.upper()
        else:
            self._device = device
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._hub_version = hub_version
        self._loop = loop if loop else asyncio.get_event_loop()
        self._retry_interval = retry_interval
        self._closed = True
        self._closing = False
        self._halted = False
        self._auto_reconnect = auto_reconnect
        self._protocol = None

    @property
    def protocol(self):
        """Return the connection protocol."""
        return self._protocol

    @protocol.setter
    def protocol(self, val):
        """Set the connection protocol."""
        self._protocol = val

    @property
    def device(self):
        """Return the PLM device."""
        return self._device

    @property
    def host(self):
        """Return the Hub host or IP address."""
        return self._host

    @property
    def username(self):
        """Return the Hub username."""
        return self._username

    @property
    def password(self):
        """Return the Hub password."""
        return self._password

    @property
    def port(self):
        """Return the Hub IP port."""
        return self._port

    @property
    def hub_version(self):
        """Return the version of the Insteon Hub."""
        return self._hub_version

    @property
    def auto_reconnect(self):
        """Return the connection protocol."""
        return self._auto_reconnect

    @property
    def closing(self):
        """Return the connection protocol."""
        return self._closing

    @property
    def loop(self):
        """Return the connection loop."""
        return self._loop

    # pylint: disable=too-many-arguments
    @classmethod
    async def create(cls, device='/dev/ttyUSB0', host=None,
                     username=None, password=None, port=25010, hub_version=2,
                     auto_reconnect=True, loop=None, workdir=None,
                     poll_devices=True, load_aldb=True):
        """Create a connection to a specific device.

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
        :param load_aldb:
            Should the ALDB be loaded on connect

        :type device:
            str
        :type auto_reconnect:
            boolean
        :type loop:
            asyncio.loop
        :type update_callback:
            callable
        """
        _LOGGER.debug("Starting Modified Connection.create")
        conn = cls(device=device, host=host, username=username,
                   password=password, port=port, hub_version=hub_version,
                   loop=loop, retry_interval=1, auto_reconnect=auto_reconnect)

        def connection_lost():
            """Respond to Protocol connection lost."""
            if conn.auto_reconnect and not conn.closing:
                _LOGGER.debug("Reconnecting to transport")
                asyncio.ensure_future(conn.reconnect(), loop=conn.loop)

        protocol_class = PLM
        if conn.host and conn.hub_version == 2:
            protocol_class = Hub
        conn.protocol = protocol_class(
            connection_lost_callback=connection_lost,
            loop=conn.loop,
            workdir=workdir,
            poll_devices=poll_devices,
            load_aldb=load_aldb)

        await conn.reconnect()

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

    async def reconnect(self):
        """Reconnect to the modem."""
        _LOGGER.debug('starting Connection.reconnect')
        await self._connect()
        while self._closed:
            await self._retry_connection()
        _LOGGER.debug('ending Connection.reconnect')

    # pylint: disable=unused-argument
    async def close(self, event):
        """Close the PLM device connection and don't try to reconnect."""
        _LOGGER.info('Closing connection to Insteon Modem')
        self._closing = True
        self._auto_reconnect = False
        await self.protocol.close()
        if self.protocol.transport:
            self.protocol.transport.close()
        await asyncio.sleep(0, loop=self._loop)
        _LOGGER.info('Insteon Modem connection closed')

    def halt(self):
        """Close the PLM device connection and wait for a resume() request."""
        _LOGGER.warning('Halting connection to Insteon Modem')
        self._halted = True
        if self.protocol.transport:
            self.protocol.transport.close()

    def resume(self):
        """Resume the PLM device connection if we have been halted."""
        _LOGGER.warning('Resuming connection to Insteon Modem')
        self._halted = False

    @property
    def dump_conndata(self):
        """Developer tool for debugging forensics."""
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())

    async def _retry_connection(self):
        _LOGGER.debug('starting Connection._retry_connection')
        device = self.host if self.host else self.device
        self._increase_retry_interval()
        _LOGGER.warning('Connection failed, retry in %i seconds: %s',
                        self._retry_interval, device)
        await asyncio.sleep(self._retry_interval, loop=self._loop)
        _LOGGER.debug('Starting _connect')
        await self._connect()
        _LOGGER.debug('ending Connection._retry_connection')

    async def _connect(self):
        _LOGGER.debug('starting Connection._connect')
        if self.host and self._hub_version == 2:
            connected = await self._connect_http()
        else:
            connected = await self._connect_serial()
        _LOGGER.debug('ending Connection._connect')
        return connected

    async def _connect_http(self):
        _LOGGER.info('Connecting to Insteon Hub on %s', self.host)
        auth = aiohttp.BasicAuth(self.username, self.password)
        _LOGGER.debug('Creating http connection')
        # pylint: disable=unused-variable
        transport, protocol = await create_http_connection(
            self._loop, lambda: self.protocol,
            self.host, port=self.port, auth=auth)
        connected = await transport.test_connection()
        if connected:
            transport.resume_reading()
        self._closed = not connected
        return connected

    async def _connect_serial(self):
        try:
            if self._hub_version == 1:
                url = 'socket://{}:{}'.format(self._host, self._port)
                _LOGGER.info('Connecting to Insteon Hub v1 on %s', url)
                # pylint: disable=unused-variable
                transport, protocol = await create_serial_connection(
                    self._loop, lambda: self.protocol,
                    url, baudrate=19200)
            else:
                _LOGGER.info('Connecting to PLM on %s', self._device)
                # pylint: disable=unused-variable
                transport, protocol = await create_serial_connection(
                    self._loop, lambda: self.protocol,
                    self._device, baudrate=19200)
            self._closed = False
        except OSError:
            self._closed = True
        return not self._closed


# Hub version 1 (2242) is untested using the HTTP Transport.
# It is tested using the PLM socket interface on port 9761.
# pylint: disable=too-many-instance-attributes
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

    def __init__(self, loop, protocol, host, port=25105, auth=None):
        """Init the HttpTransport class."""
        super().__init__()
        self._loop = loop
        self._protocol = protocol
        self._host = host
        self._port = port
        self._auth = auth

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
        self.close()

    def can_write_eof(self):
        return False

    def is_closing(self):
        return self._closing

    def close(self):
        _LOGGER.debug("Closing Hub session")
        asyncio.ensure_future(self._close(), loop=self._loop)

    async def _close(self):
        self._closing = True
        self._restart_reader = False
        _LOGGER.info("Insteon Hub session closed")

    def get_write_buffer_size(self):
        return 0

    def pause_reading(self):
        asyncio.ensure_future(self._stop_reader(False), loop=self._loop)

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
        asyncio.ensure_future(self._async_write(url), loop=self._loop)

    async def test_connection(self):
        """Test the connection to the hub."""
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        response_status = 999
        try:
            async with aiohttp.ClientSession(loop=self._loop,
                                             auth=self._auth) as session:
                async with session.get(url, timeout=10) as response:
                    if response:
                        response_status = response.status
                        if response.status == 200:
                            _LOGGER.debug('Test connection status is %d',
                                          response.status)
                            return True
                        self._log_error(response.status)
                        _LOGGER.debug('Connection test failed')
                        return False

        # pylint: disable=broad-except
        except Exception as e:
            _LOGGER.error('An aiohttp error occurred: %s with status %s',
                          str(e), response_status)
        _LOGGER.debug('Connection test failed')
        self.close()
        return False

    async def _async_write(self, url):
        return_status = 500
        # if self._session.closed:
        #     _LOGGER.warning("Session closed, cannot write to Hub")
        #     return 999
        _LOGGER.debug("Writing message: %s", url)
        try:
            await self._read_write_lock
            async with aiohttp.ClientSession(loop=self._loop,
                                             auth=self._auth) as session:
                async with session.post(url, timeout=10) as response:
                    return_status = response.status
                    _LOGGER.debug("Post status: %s", response.status)
                    if response.status == 200:
                        self._write_last_read(0)
                    else:
                        self._log_error(response.status)
                        await self._stop_reader(False)
        except aiohttp.client_exceptions.ServerDisconnectedError:
            _LOGGER.error('Reconnect to Hub (ServerDisconnectedError)')
            await self._stop_reader(True)
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error('Reconnect to Hub (ClientConnectorError)')
            await self._stop_reader(True)
        except asyncio.TimeoutError:
            _LOGGER.error('Reconnect to Hub (TimeoutError)')
            await self._stop_reader(True)

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

    async def _clear_buffer(self):
        _LOGGER.debug("..................Clearing the buffer..............")
        url = 'http://{:s}:{:d}/1?XB=M=1'.format(self._host, self._port)
        await self._async_write(url)

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    # pylint: disable=broad-except
    async def _ensure_reader(self):
        _LOGGER.info('Insteon Hub reader started')
        await self._clear_buffer()
        self._write_last_read(0)
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        _LOGGER.debug('Calling connection made')
        _LOGGER.debug('Protocol: %s', self._protocol)
        self._protocol.connection_made(self)
        while self._restart_reader and not self._closing:
            try:
                await self._read_write_lock
                async with aiohttp.ClientSession(loop=self._loop,
                                                 auth=self._auth) as session:
                    async with session.get(url, timeout=10) as response:
                        buffer = None
                        # _LOGGER.debug("Reader status: %d", response.status)
                        if response.status == 200:
                            html = await response.text()
                            if len(html) == 234:
                                # pylint: disable=no-value-for-parameter
                                buffer = await self._parse_buffer(html)
                            else:
                                buffer = self._parse_buffer_v1(html)
                        else:
                            self._log_error(response.status)
                            await self._stop_reader(False)
                if self._read_write_lock.locked():
                    self._read_write_lock.release()
                if buffer:
                    _LOGGER.debug('New buffer: %s', buffer)
                    bin_buffer = binascii.unhexlify(buffer)
                    self._protocol.data_received(bin_buffer)
                await asyncio.sleep(1, loop=self._loop)

            except asyncio.CancelledError:
                _LOGGER.debug('Stop connection to Hub (loop stopped)')
                await self._stop_reader(False)
            except GeneratorExit:
                _LOGGER.debug('Stop connection to Hub (GeneratorExit)')
                await self._stop_reader(False)
            except aiohttp.client_exceptions.ServerDisconnectedError:
                _LOGGER.debug('Reconnect to Hub (ServerDisconnectedError)')
                await self._stop_reader(True)
            except aiohttp.client_exceptions.ClientConnectorError:
                _LOGGER.debug('Reconnect to Hub (ClientConnectorError)')
                await self._stop_reader(True)
            except asyncio.TimeoutError:
                _LOGGER.error('Reconnect to Hub (TimeoutError)')
                await self._stop_reader(True)
            except Exception as e:
                _LOGGER.debug('Stop reading due to %s', str(e))
                await self._stop_reader(False)
        _LOGGER.info('Insteon Hub reader stopped')
        return

    async def _parse_buffer(self, html):
        last_stop = 0
        if not self._last_read.empty():
            last_stop = self._last_read.get_nowait()
        buffer = ''
        raw_text = html.replace('<response><BS>', '')
        raw_text = raw_text.replace('</BS></response>', '')
        raw_text = raw_text.strip()
        if raw_text[:199] == '0' * 200:
            # Likely the buffer was cleared
            return None
        this_stop = int(raw_text[-2:], 16)
        if this_stop > last_stop:
            _LOGGER.debug('Buffer from %d to %d', last_stop, this_stop)
            buffer = raw_text[last_stop:this_stop]
        elif this_stop < last_stop:
            _LOGGER.debug('Buffer from %d to 200 and 0 to %d',
                          last_stop, this_stop)
            buffer_hi = raw_text[last_stop:200]
            if buffer_hi == '0' * len(buffer_hi):
                # The buffer was probably reset since the last read
                buffer_hi = ''
            buffer_low = raw_text[0:this_stop]
            buffer = '{:s}{:s}'.format(buffer_hi, buffer_low)
        else:
            buffer = None
        self._write_last_read(this_stop)
        return buffer

    def _parse_buffer_v1(self, html):
        # I think this is a good idea but who knows.
        # Risk is we may be loosing the next message
        # If we do this than this method must be a coroutine
        # await self._clear_buffer()
        raw_text = html.replace('<response><BS>', '')
        raw_text = raw_text.replace('</BS></response>', '')
        raw_text = raw_text.strip()
        buffer = ''
        while raw_text:
            msg, raw_text = self._find_message(raw_text)
            if msg:
                buffer = '{}{}'.format(buffer, msg)
        return buffer

    @staticmethod
    def _find_message(raw_text):
        from insteonplm.messages import iscomplete
        len_raw_text = len(raw_text)
        pos = -2
        msg_len = 4   # set to 5 because the min msg len is 4 chars or 2 bytes
        msg = None
        if raw_text == '0' * len_raw_text:
            print('Likely the buffer was cleared')
            return msg, None, False
        while pos < (len_raw_text - 2) and raw_text[pos: pos + 2] != '02':
            pos = pos + 2
        print('pos is: ', pos)
        print('len_raw_text is: ', len_raw_text)
        if pos == len_raw_text - 2:
            print('02 not found')
            return msg, None, False
        if pos > 0:
            raw_text = raw_text[pos:] + raw_text[0:pos]
        while (msg_len < len_raw_text and
               not iscomplete(binascii.unhexlify(raw_text[0:msg_len]))):
            msg_len = msg_len + 2
        if msg_len == len_raw_text:
            print('must not be a message')
            return msg, None, False
        msg = raw_text[0:msg_len]
        raw_text = raw_text[msg_len:]
        if msg_len > len_raw_text - pos:
            # We have wrapped so there cannot be another messasge
            raw_text = None
        else:
            if pos > 0 and raw_text:
                raw_text = raw_text[len(raw_text) - pos:] + raw_text[:-pos]
        return (msg, raw_text)

    def _write_last_read(self, val):
        while not self._last_read.empty():
            self._last_read.get_nowait()
        self._last_read.put_nowait(val)

    # pylint: disable=unused-argument
    def _start_reader(self, future=None):
        if self._restart_reader:
            _LOGGER.debug("Starting the buffer reader")
            self._reader_task = asyncio.ensure_future(self._ensure_reader(),
                                                      loop=self._loop)
            self._reader_task.add_done_callback(self._start_reader)

    async def _stop_reader(self, reconnect=False):
        _LOGGER.debug('Stopping the reader and reconnect is %s', reconnect)
        self._restart_reader = False
        if self._reader_task:
            self._reader_task.remove_done_callback(self._start_reader)
            self._reader_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reader_task
                await asyncio.sleep(0, loop=self._loop)
        await self._protocol.pause_writing()
        # if not self._session.closed:
        #     _LOGGER.debug('Session is open so we close it')
        #     await self._close()
        if reconnect:
            _LOGGER.debug("We want to reconnect so we do...")
            self._protocol.connection_lost(True)

    def _log_error(self, status):
        if status == 401:
            _LOGGER.error('Athentication error, check your configuration')
            _LOGGER.error('If configuration is correct and restart the Hub')
            _LOGGER.error('System must be restared to reconnect to hub')
        elif status == 404:
            _LOGGER.error('Hub not found at http://%s:%d, check configuration',
                          self._host, self._port)
        elif status in range(500, 600):
            _LOGGER.error('Hub returned a server error')
            _LOGGER.error('Restart the Hub and try again')
        else:
            _LOGGER.error('An unknown error has occured')
            _LOGGER.error('Check the configuration and restart the Hub and '
                          'the application')
