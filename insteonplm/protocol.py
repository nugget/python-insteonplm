"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import binascii

from .ipdb import IPDB
from .plm import Address, PLMProtocol, Message

__all__ = ('PLM', 'ALDB')

PP = PLMProtocol()


class ALDB(object):
    """Class holds and maintains the ALL-Link Database from the PLM device."""

    ipdb = IPDB()

    def __init__(self):
        """Instantiate the ALL-Link Database object."""
        self.log = logging.getLogger(__name__)
        self.state = 'empty'
        self._devices = {}
        self._cb_new_device = []
        self._overrides = {}

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return len(self._devices)

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for device in self._devices:
            yield device

    def __getitem__(self, address):
        """Fetch a device from the ALDB."""
        if address in self._devices:
            return self._devices[address]
        raise KeyError

    def __setitem__(self, key, value):
        """Add or Update a device in the ALDB."""
        if 'cat' not in value or value['cat'] == 0:
            self.log.debug('Ignoring device setitem with no cat: %s', value)
            return

        if key in self._devices:
            if 'firmware' in value and value['firmware'] < 255:
                self._devices[key].update(value)
        else:
            productdata = self.ipdb[value['cat'], value['subcat']]
            value.update(productdata._asdict())
            address = Address(key)
            value['address_hex'] = address.hex
            value['address'] = address.human
            self._devices[key] = value

            self.log.info('New INSTEON Device %r: %s (%02x:%02x)',
                          Address(key), value['description'], value['cat'],
                          value['subcat'])

            self._apply_overrides(key)

            for callback, criteria in self._cb_new_device:
                if self._device_matches_criteria(value, criteria):
                    callback(value)

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def add_device_callback(self, callback, criteria):
        """Register a callback to be invoked when a new device appears."""
        self.log.info('New callback %s with %s (%d items already in list)',
                      callback, criteria, len(self._devices.keys()))
        self._cb_new_device.append([callback, criteria])

        #
        # When a new device callback is added, we want to include all
        # previously-discovered devices as well as new devices.  So we
        # iterate through the existing device list and trigger the callback
        # for each of them
        #
        for device in self:
            value = self[device]
            if self._device_matches_criteria(value, criteria):
                self.log.info('retroactive callback device %s matching %s',
                              value['address'], criteria)
                callback(value)

    def add_override(self, addr, key, value):
        """Register an attribute override for a device."""
        address = Address(addr).hex
        self.log.info('New override for %s %s is %s', address, key, value)
        device_override = self._overrides.get(address, {})
        device_override[key] = value
        self._overrides[address] = device_override

        if address in self._devices:
            self._apply_overrides(address)

    def _apply_overrides(self, address):
        device_override = self._overrides.get(address, {})
        for key in device_override:
            oldval = self._devices[address].get(key, None)
            value = device_override[key]
            if value != oldval:
                self.log.debug('Override %s for %s: %s -> %s',
                               key, address, oldval, value)
                self._devices[address][key] = value

    def getattr(self, key, attr):
        """Return the requested attribute for device with address 'key'."""
        key = Address(key).hex
        if key in self._devices:
            return self._devices[key].get(attr, None)
        return None

    def setattr(self, key, attr, value):
        """Set supplied attribute on designated device in the ALDB."""
        key = Address(key).hex

        if key in self._devices:
            oldvalue = self._devices[key].get(attr, None)
            self._devices[key][attr] = value
            if value != oldvalue:
                self.log.info('Device %s.%s changed: %s->%s"',
                              key, attr, oldvalue, value)
                return True
            else:
                self.log.debug('Device %s.%s unchanged: %s->%s"',
                               key, attr, oldvalue, value)
                return False
        else:
            raise KeyError

    @staticmethod
    def _device_matches_criteria(device, criteria):
        match = True

        if 'address' in criteria:
            criteria['address'] = Address(criteria['address'])

        for key in criteria.keys():
            if key == 'capability':
                if criteria[key] not in device['capabilities']:
                    match = False
                    break
            elif key[0] != '_':
                if key not in device:
                    match = False
                    break
                elif criteria[key] != device[key]:
                    match = False
                    break
        return match


# pylint: disable=too-many-instance-attributes, too-many-public-methods
class PLM(asyncio.Protocol):
    """The Insteon PLM IP control protocol handler."""

    def __init__(self, loop=None, connection_lost_callback=None, userdefineddevices=()):
        """Protocol handler that handles all status and changes on PLM.

        This class is expected to be wrapped inside a Connection class object
        which will maintain the socket and handle auto-reconnects.

            :param connection_lost_callback:
                called when connection is lost to device (optional)
            :param loop:
                asyncio event loop (optional)

            :type: connection_lost_callback:
                callable
            :type loop:
                asyncio.loop
        """
        self._loop = loop

        self._connection_lost_callback = connection_lost_callback
        self._update_callbacks = []
        self._message_callbacks = []
        self._insteon_callbacks = []

        self._me = None
        self._buffer = bytearray()
        self._last_message = None
        self._last_command = None
        self._wait_for = {}
        self._recv_queue = []
        self._send_queue = []

        self.devices = ALDB()

        self.log = logging.getLogger(__name__)
        self.transport = None

        self._userdefineddevices = {}

        for userdevice in userdefineddevices:
            if 'cat' in userdevice and 'subcat' in userdevice and 'firmware' in userdevice:
                self._userdefineddevices[userdevice["address"]] = {
                    "cat": userdevice["cat"],
                    "subcat": userdevice["subcat"],
                    "firmware": userdevice["firmware"],
                    "status": "notfound"
                }
                self.devices[userdevice["address"]] = {'cat': userdevice["cat"],
                                            'subcat': userdevice["subcat"],
                                            'firmware': userdevice["firmware"]}

        self.add_message_callback(self._parse_insteon_standard, {'code': 0x50})
        self.add_message_callback(self._parse_insteon_extended, {'code': 0x51})
        self.add_message_callback(self._parse_all_link_completed, {'code': 0x53})
        self.add_message_callback(self._parse_button_event, {'code': 0x54})
        self.add_message_callback(self._parse_all_link_record, {'code': 0x57})
        self.add_message_callback(self._parse_get_plm_info, {'code': 0x60})
        self.add_message_callback(self._parse_get_plm_config, {'code': 0x73})

        self.add_insteon_callback(self._insteon_on, {'cmd1': 0x11})
        self.add_insteon_callback(self._insteon_on, {'cmd1': 0x12})
        self.add_insteon_callback(self._insteon_off, {'cmd1': 0x13})
        self.add_insteon_callback(self._insteon_off, {'cmd1': 0x14})
        self.add_insteon_callback(self._insteon_manual_change_stop, {'cmd1': 0x18})

    #
    # asyncio network functions
    #

    def connection_made(self, transport):
        """Called when asyncio.Protocol establishes the network connection."""
        self.log.info('Connection established to PLM')
        self.transport = transport

        # self.transport.set_write_buffer_limits(128)
        # limit = self.transport.get_write_buffer_size()
        # self.log.debug('Write buffer size is %d', limit)
        self.get_plm_info()
        self.load_all_link_database()

    def data_received(self, data):
        """Called when asyncio.Protocol detects received data from network."""
        self.log.debug('Received %d bytes from PLM: %s',
                       len(data), binascii.hexlify(data))

        self._buffer.extend(data)
        self._peel_messages_from_buffer()

        for message in self._recv_queue:
            self._process_message(message)
            self._recv_queue.remove(message)

    def connection_lost(self, exc):
        """Called when asyncio.Protocol loses the network connection."""
        if exc is None:
            self.log.warning('eof from modem?')
        else:
            self.log.warning('Lost connection to modem: %s', exc)

        self.transport = None

        if self._connection_lost_callback:
            self._connection_lost_callback()

    def _rsize(self, message):
        code = message[1]
        ppc = PP.lookup(code, fullmessage=message)

        if hasattr(ppc, 'rsize') and ppc.rsize:
            self.log.debug('Found a code 0x%x message which returns %d bytes',
                           code, ppc.rsize)
            return ppc.rsize
        else:
            self.log.debug('Unable to find an rsize for code 0x%x', code)
            return len(message) + 1

    def _timeout_reached(self):
        self.log.debug('_timeout_reached invoked')
        self._clear_wait()
        self._process_queue()

    def _clear_wait(self):
        self.log.debug('_clear_wait invoked')
        if '_thandle' in self._wait_for:
            self._wait_for['_thandle'].cancel()
        self._wait_for = {}

    def _schedule_wait(self, keys, timeout=1):
        if self._wait_for != {}:
            self.log.warning('Overwriting stale wait_for: %s', self._wait_for)
            self._clear_wait()

        self.log.debug('Waiting for %s timeout in %d seconds', keys, timeout)
        if timeout > 0:
            keys['_thandle'] = self._loop.call_later(timeout,
                                                     self._timeout_reached)

        self._wait_for = keys

    def _wait_for_last_command(self):
        sentmessage = self._last_command
        rsize = self._rsize(sentmessage)
        self.log.debug('Wait for ACK/NAK on sent: %s expecting rsize of %d',
                       binascii.hexlify(sentmessage), rsize)
        if self._buffer.find(sentmessage) == 0:
            if len(self._buffer) < rsize:
                self.log.debug('Waiting for all of message to arrive, %d/%d',
                               len(self._buffer), rsize)
                return

            code = self._buffer[1]
            message_length = len(sentmessage)
            response_length = rsize - message_length
            response = self._buffer[message_length:response_length]
            acknak = self._buffer[rsize-1]

            mla = self._buffer[:rsize-1]
            buffer = self._buffer[rsize:]

            data_in_ack = [0x19, 0x2e]
            msg = Message(mla)

            queue_ack = False

            if sentmessage != mla:
                self.log.debug('sent command and ACK response differ')
                queue_ack = True

            if hasattr(msg, 'cmd1') and msg.cmd1 in data_in_ack:
                self.log.debug('sent cmd1 is on queue_ack list')
                queue_ack = True

            if acknak == 0x06:
                if len(response) > 0 or queue_ack is True:
                    self.log.debug('Sent command %s OK with response %s',
                                  binascii.hexlify(sentmessage), response)
                    self._recv_queue.append(mla)
                else:
                    self.log.debug('Sent command %s OK',
                                   binascii.hexlify(sentmessage))

            else:
                if code == 0x6a:
                    self.log.info('ALL-Link database dump is complete')
                    self.devices.state = 'loaded'
                    for address in self.devices:
                        device = self.devices[address]
                        if 'cat' in device and device['cat'] > 0:
                            self.log.debug('I know the category for %s (0x%x)',
                                           address, device['cat'])
                        else:
                            self.product_data_request(device)
                    for userdevice in self._userdefineddevices:
                        if self._userdefineddevices[userdevice]["status"] == "notfound":
                            self.log.info("Failed to discover device %r.", userdevice)
                    self.poll_devices()
                else:
                    self.log.warning('Sent command %s UNsuccessful! (%02x)',
                                     binascii.hexlify(sentmessage), acknak)
            self._last_command = None
            self._buffer = buffer

    def _wait_for_recognized_message(self):
        code = self._buffer[1]

        for ppcode in PP:
            if ppcode == code or ppcode == bytes([code]):
                ppc = PP.lookup(code, fullmessage=self._buffer)

                self.log.debug('Found a code %02x message which is %d bytes',
                               code, ppc.size)

                if len(self._buffer) == ppc.size:
                    new_message = self._buffer[0:ppc.size]
                    self.log.debug('new message is: %s',
                                   binascii.hexlify(new_message))
                    self._recv_queue.append(new_message)
                    self._buffer = self._buffer[ppc.size:]
                else:
                    self.log.debug('Need more bytes to process message.')

    def _peel_messages_from_buffer(self):
        lastlooplen = 0
        worktodo = True

        while worktodo:
            if len(self._buffer) == 0:
                self.log.debug('Clean break!  There is no buffer left')
                worktodo = False
                break

            if len(self._buffer) < 2:
                worktodo = False
                break

            if self._buffer[0] != 2:
                self._buffer = self._buffer[1:]
                self.log.debug('Trimming leading buffer garbage')

            if len(self._buffer) == lastlooplen:
                # Buffer size did not change so we should wait for more data
                worktodo = False
                break

            lastlooplen = len(self._buffer)

            if self._buffer.find(2) < 0:
                self.log.debug('Buffer does not contain a 2, we should bail')
                worktodo = False
                break

            if self._last_command:
                self._wait_for_last_command()
            else:
                self._wait_for_recognized_message()

        self._process_queue()

    def _process_queue(self):
        self.log.debug('Send queue contains %d items', len(self._send_queue))
        if self._clear_to_send() is True:
            command, wait_for = self._send_queue[0]
            self._send_hex(command, wait_for=wait_for)
            self._send_queue.remove([command, wait_for])

    def _clear_to_send(self):
        if len(self._buffer) == 0:
            if len(self._send_queue) > 0:
                if self._last_command is None:
                    if self._wait_for == {}:
                        return True

    def _process_message(self, rawmessage):
        self.log.debug('Processing message: %s', binascii.hexlify(rawmessage))
        if rawmessage[0] != 2 or len(rawmessage) < 2:
            self.log.warning('process_message called with a malformed message')
            return

        if rawmessage == self._last_message:
            self.log.debug('ignoring duplicate message')
            return

        self._last_message = rawmessage

        msg = Message(rawmessage)

        # if hasattr(msg, 'target') and msg.target != self._me:
        #     self.log.info('Ignoring message that is not for me')
        #     return

        if self._message_matches_criteria(msg, self._wait_for):
            if '_callback' in self._wait_for:
                self._clear_wait()
                self._process_queue()
                return
            else:
                self._clear_wait()

        callbacked = False
        for callback, criteria in self._message_callbacks:
            if self._message_matches_criteria(msg, criteria):
                self.log.debug('message callback %s with criteria %s',
                               callback, criteria)
                self._loop.call_soon(callback, msg)
                callbacked = True

        if callbacked is False:
            ppc = PP.lookup(msg.code, fullmessage=rawmessage)
            if hasattr(ppc, 'name') and ppc.name:
                self.log.info('Unhandled event: %s (%s)', ppc.name,
                              binascii.hexlify(rawmessage))
            else:
                self.log.info('Unrecognized event: UNKNOWN (%s)',
                              binascii.hexlify(rawmessage))

        self._process_queue()

    def _message_matches_criteria(self, msg, criteria):
        match = True

        if criteria is None or criteria == {}:
            return True

        if 'address' in criteria:
            criteria['address'] = Address(criteria['address'])

        for key in criteria.keys():
            if key[0] != '_':
                mattr = getattr(msg, key, None)
                if mattr is None:
                    match = False
                    break
                elif criteria[key] != mattr:
                    match = False
                    break

        if match is True:
            if '_callback' in criteria:
                self.log.debug('Calback invoked from mmc criteria')
                criteria['_callback'](msg)

        return match

    def _parse_insteon_standard(self, msg):
        device = self.devices[msg.address.hex]

        self.log.info('INSTEON standard %r->%r: cmd1:%02x cmd2:%02x flags:%02x',
                      msg.address, msg.target,
                      msg.cmd1, msg.cmd2, msg.flagsval)
        self.log.debug('flags: %r', msg.flags)
        self.log.debug('device: %r', device)

        for callback, criteria in self._insteon_callbacks:
            if self._message_matches_criteria(msg, criteria):
                self.log.debug('insteon callback %s with criteria %s',
                               callback, criteria)
                self._loop.call_soon(callback, msg, device)

    def _parse_insteon_extended(self, msg):
        device = self.devices[msg.address.hex]

        self.log.info('INSTEON extended %r->%r: cmd1:%02x cmd2:%02x flags:%02x data:%s',
                      msg.address, msg.target, msg.cmd1, msg.cmd2, msg.flagsval,
                      binascii.hexlify(msg.userdata))
        self.log.debug('flags: %r', msg.flags)
        self.log.debug('device: %r', device)

        if msg.cmd1 == 0x03 and msg.cmd2 == 0x00:
            self._parse_product_data_response(msg.address, msg.userdata)

    def _parse_status_response(self, msg):
        onlevel = msg.cmd2

        self.log.info('INSTEON device status %r is at level %s',
                      msg.address, hex(onlevel))
        self.devices.setattr(msg.address, 'onlevel', onlevel)
        self._do_update_callback(msg)

    def _parse_sensor_response(self, msg):
        device = self.devices[msg.address.hex]

        sensorstate = msg.cmd2

        if device.get('model') == '2450':
            # Swap the values for a 2450 because it's opposite
            self.log.debug('Reversing sensorstate %s because 2450', sensorstate)
            if sensorstate:
                sensorstate = 0
            else:
                sensorstate = 1

        self.log.info('INSTEON sensor status %r is at level %s',
                      msg.address, hex(sensorstate))
        self.devices.setattr(msg.address, 'sensorstate', sensorstate)
        self._do_update_callback(msg)

    def _insteon_on(self, msg, device):
        self.log.info('INSTEON on event: %r, %r', msg, device)

        attribute = 'onlevel'

        if 'binary_sensor' in device.get('capabilities'):
            if msg.flags.get('group', False):
                #
                # If this is a group message from a sensor device, then we
                # treat it as sensorstate instead of onlevel.  This is vital
                # for I/O Linc 2450 devices, because it's the cleanest way
                # to differntiate between the sensor on/off notifications and
                # the relay on/off notifications that come in response to a
                # turn_on or turn_off command.  Those on/off messages are
                # direct (not group, not broadcast) and reflect the relay's
                # status and not the sensor's status.
                #
                attribute = 'sensorstate'

        if msg.cmd2 == 0x00:
            value = 255
        else:
            value = msg.cmd2

        if device.get('model') == '2477D':
            if msg.cmd2 == 0x00 or msg.cmd2 == 0x01:
                value = device.get('setlevel', 255)
                self.log.debug('ON report with no onlevel, using %02x', value)

        if self.devices.setattr(msg.address, attribute, value):
            self._do_update_callback(msg)

    def _insteon_off(self, msg, device):
        self.log.info('INSTEON off event: %r, %r', msg, device)

        attribute = 'onlevel'

        if 'binary_sensor' in device.get('capabilities'):
            if msg.flags.get('group', False):
                #
                # If this is a group message from a sensor device, then we
                # treat it as sensorstate instead of onlevel.  This is vital
                # for I/O Linc 2450 devices, because it's the cleanest way
                # to differntiate between the sensor on/off notifications and
                # the relay on/off notifications that come in response to a
                # turn_on or turn_off command.  Those on/off messages are
                # direct (not group, not broadcast) and reflect the relay's
                # status and not the sensor's status.
                #
                attribute = 'sensorstate'

        if self.devices.setattr(msg.address, attribute, 0):
            self._do_update_callback(msg)

    # pylint: disable=unused-argument
    def _insteon_manual_change_stop(self, msg, device):
        self.log.info('Light Stop Manual Change')
        self.status_request(msg.address)

    def _parse_extended_status_response(self, msg):
        device = self.devices[msg.address.hex]

        self.log.info('INSTEON extended device status %r', msg.address)
        if device.get('cat') == 0x01:
            self.devices.setattr(msg.address, 'ramprate', msg.userdata[6])
            self.devices.setattr(msg.address, 'setlevel', msg.userdata[7])

    def _do_update_callback(self, msg):
        for callback, criteria in self._update_callbacks:
            if self._message_matches_criteria(msg, criteria):
                self.log.debug('update callback %s with criteria %s',
                               callback, criteria)
                self._loop.call_soon(callback, msg)

    def _parse_product_data_response(self, address, userdata):
        category = userdata[4]
        subcategory = userdata[5]
        firmware = userdata[6]
        self.log.info('INSTEON Product Data Response from %r: cat:%s, subcat:%s',
                      address, hex(category), hex(subcategory))

        self.devices[address.hex] = {'cat': category, 'subcat': subcategory,
                                     'firmware': firmware}

    def _parse_button_event(self, msg):
        self.log.info('PLM button event: %02x (%s)', msg.event, msg.description)

    def _parse_get_plm_info(self, msg):
        self.log.info('PLM Info from %r: category:%02x subcat:%02x firmware:%02x',
                      msg.address, msg.category, msg.subcategory, msg.firmware)
        self._me = msg.address

    def _parse_get_plm_config(self, msg):
        self.log.info('PLM Config: flags:%02x spare:%02x spare:%02x',
                      msg.flagsval, msg.spare1, msg.spare2)

    def _parse_all_link_record(self, msg):
        self.log.info('ALL-Link Record for %r: flags:%02x group:%02x data:%02x/%02x/%02x',
                      msg.address, msg.flagsval, msg.group,
                      msg.linkdata1, msg.linkdata2, msg.linkdata3)
        
        if msg.address.hex in self.devices:
            self.log.info("Device %r is already added manually.", msg.address.hex)
            if msg.address.hex in self._userdefineddevices:
                self._userdefineddevices[msg.address.hex]["status"] = "found"
        else:
            self.log.info("Auto Discovering device %r.", msg.address.hex)
            self.devices[msg.address.hex] = {'cat': msg.linkdata1,
                                         'subcat': msg.linkdata2,
                                         'firmware': msg.linkdata3}

        if self.devices.state == 'loading':
            self.get_next_all_link_record()

    def _parse_all_link_completed(self, msg):
        self.log.info('ALL-Link Completed %r: group:%d cat:%02x subcat:%02x '
                      'firmware:%02x linkcode: %02x',
                      msg.address, msg.group, msg.category, msg.subcategory,
                      msg.firmware, msg.linkcode)

        if msg.address.hex in self.devices:
            self.log.info("Device %r is already added manually.", msg.address.hex)
            if msg.address.hex in self._userdefineddevices:
                self._userdefineddevices[msg.address.hex]["status"] = "found"
        else:
            self.log.info("Auto Discovering device %r.", msg.address.hex)
            self.devices[msg.address.hex] = {'cat': msg.category,
                                         'subcat': msg.subcategory,
                                         'firmware': msg.firmware}
        for userdevice in self._userdefineddevices:
            if self._userdefineddevices[userdevice]["status"] == "notfound":
                self.log.info("Finished all link, and failed to discover device %r.", userdevice)

    def _queue_hex(self, message, wait_for=None):
        if wait_for is None:
            wait_for = {}

        self.log.debug('Adding command to queue: %s', message)
        self._send_queue.append([message, wait_for])

    def _send_hex(self, message, wait_for=None):
        if wait_for is None:
            wait_for = {}

        if self._last_command or self._wait_for:
            self.log.debug('Still waiting on last_command.')
            self._queue_hex(message, wait_for)
        else:
            self._send_raw(binascii.unhexlify(message))
            self._schedule_wait(wait_for)

    def _send_raw(self, message):
        self.log.debug('Sending %d byte message: %s',
                      len(message), binascii.hexlify(message))
        self.transport.write(message)
        self._last_command = message

    def add_message_callback(self, callback, criteria):
        """Register a callback for when a matching message is seen."""
        self._message_callbacks.append([callback, criteria])
        self.log.debug('Added message callback to %s on %s', callback, criteria)

    def add_insteon_callback(self, callback, criteria):
        """Register a callback for when a matching INSTEON command is seen."""
        self._insteon_callbacks.append([callback, criteria])
        self.log.debug('Added INSTEON callback to %s on %s', callback, criteria)

    def add_update_callback(self, callback, criteria):
        """Register as callback for when a matching device attribute changes."""
        self._update_callbacks.append([callback, criteria])
        self.log.debug('Added update callback to %s on %s', callback, criteria)

    def add_device_callback(self, callback, criteria):
        """Register a callback for when a matching new device is seen."""
        self.devices.add_device_callback(callback, criteria)

    def send_insteon_standard(self, device, cmd1, cmd2, wait_for=None):
        """Send an INSTEON Standard message to the PLM."""
        if wait_for is None:
            wait_for = {}

        device = Address(device)
        rawstr = '0262'+device.hex+'00'+cmd1+cmd2
        self._send_hex(rawstr, wait_for)

    # pylint: disable=too-many-arguments
    def send_insteon_extended(self, device, cmd1, cmd2,
                              userdata='0000000000000000000000000000',
                              wait_for=None):
        """Send an INSTEON Extended message to the PLM."""
        if wait_for is None:
            wait_for = {}

        device = Address(device)
        rawstr = '0262'+device.hex+'10'+cmd1+cmd2+userdata
        self._send_hex(rawstr, wait_for)

    def get_plm_info(self):
        """Request PLM Info."""
        self.log.info('Requesting PLM Info')
        self._send_hex('0260')

    def get_plm_config(self):
        """Request PLM Config."""
        self.log.info('Requesting PLM Config')
        self._send_hex('0273')

    def get_first_all_link_record(self):
        """Request first ALL-Link record."""
        self.log.info('Requesting First ALL-Link Record')
        self._send_hex('0269', wait_for={'code': 0x57})

    def get_next_all_link_record(self):
        """Request next ALL-Link record."""
        self.log.info('Requesting Next ALL-Link Record')
        self._send_hex('026a', wait_for={'code': 0x57})

    def load_all_link_database(self):
        """Load the ALL-Link Database into object."""
        self.devices.state = 'loading'
        self.get_first_all_link_record()

    def product_data_request(self, addr):
        """Request Product Data Record for device."""
        device = Address(addr)
        self.log.info('Requesting product data for %s', device.human)
        self.send_insteon_standard(
            device, '03', '00',
            wait_for={'code': 0x51, 'cmd1': 0x03, 'cmd2': 0x00})

    def text_string_request(self, addr):
        """Request Device Text String."""
        device = Address(addr)
        self.log.info('Requesting text string for %s', device.human)
        self.send_insteon_standard(
            device, '03', '02',
            wait_for={'code': 0x51, 'cmd1': 0x03, 'cmd2': 0x02})

    def status_request(self, addr, cmd2='00'):
        """Request Device Status."""
        address = Address(addr)
        device = self.devices[address.hex]

        if 'no_requests' in device.get('capabilities'):
            self.log.debug('Skipping status_request for no_requests device %r (%s)',
                           address, device.get('model', 'Unknown Model'))
            return

        self.log.info('Requesting status for %r', address)

        callback = self._parse_status_response
        if device.get('model') == '2450':
            if cmd2 == '00':
                self._loop.call_later(1, self.status_request, address, '01')
            else:
                callback = self._parse_sensor_response

        elif 'binary_sensor' in device.get('capabilities'):
            callback = self._parse_sensor_response

        self.send_insteon_standard(
            address, '19', cmd2,
            wait_for={'code': 0x50, '_callback': callback})

    def extended_status_request(self, addr):
        """Request Operating Flags for device."""
        device = Address(addr)
        self.log.info('Requesting extended status for %s', device.human)
        self.send_insteon_extended(
            device, '2e', '00',
            wait_for={'code': 0x51, '_callback': self._parse_extended_status_response})

    def update_setlevel(self, addr, level):
        """Currently non-functional."""
        device = Address(addr)
        self.log.info('Changing setlevel on %s to %02x', device.human, level)
        self.send_insteon_extended(
            device, '2e', '00',
            userdata='00067f0000000000000000000000',
            wait_for={'code': 0x50})

    def update_ramprate(self, addr, level):
        """Currently non-functional."""
        device = Address(addr)
        self.log.info('Changing setlevel on %s to %02x', device.human, level)
        self.send_insteon_extended(
            device, '2e', '00',
            userdata='00051b0000000000000000000000',
            wait_for={'code': 0x50})

    def get_device_attr(self, addr, attr):
        """Return attribute on specified device."""
        return self.devices.getattr(addr, attr)

    def turn_off(self, addr):
        """Send command to device to turn off."""
        address = Address(addr)
        self.send_insteon_standard(address, '13', '00', {})

    def turn_on(self, addr, brightness=255, ramprate=None):
        """Send command to device to turn on."""
        address = Address(addr)
        device = self.devices[address.hex]
        self.log.debug('turn_on %r %s', addr, device.get('model'))

        if isinstance(ramprate, int):
            #
            # The specs say this should work, but I couldn't get my 2477D
            # switches to respond.  Leaving the code in place for future
            # hacking.  If you try to use ramprate it probably won't work.
            #
            bhex = 'fc'
            self.send_insteon_standard(address, '2e', bhex, {})
        else:
            bhex = str.format('{:02X}', int(brightness)).lower()
            self.send_insteon_standard(address, '11', bhex, {})

        if device.get('model') == '2450':
            #
            # Request status after two seconds so we can detect if the I/OLinc
            # is configured in 'momentary contact' mode and turned off right
            # after we sent the on.  We can't rely on regular INSTEON state
            # broadcasts with this device because the state broadcasts come
            # from the sensor and not the relay.
            #
            self._loop.call_later(2, self.status_request, address)

    def poll_devices(self):
        """Walk through ALDB and populate device information for each device."""
        self.log.info('Polling all devices in ALDB')
        for address in self.devices:
            self.status_request(address)

    def list_devices(self):
        """Debugging command to expose ALDB."""
        for address in self.devices:
            device = self.devices[address]
            print(address, ':', device)
