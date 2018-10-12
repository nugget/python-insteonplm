"""Module to maintain PLM state information and network interface."""

import asyncio
import json
import logging

from insteonplm.address import Address
import insteonplm.devices
from insteonplm.devices import Device, X10Device

__all__ = ('ALDB')
_LOGGER = logging.getLogger(__name__)
DEVICE_INFO_FILE = 'insteon_plm_device_info.dat'


# pylint: disable=too-many-instance-attributes
class LinkedDevices():
    """Class holds and maintains the ALL-Link Database from the PLM device."""

    def __init__(self, loop=None, workdir=None):
        """Instantiate the ALL-Link Database object."""
        self._loop = loop
        self._workdir = workdir

        self._state = 'empty'
        self._devices = {}
        self._cb_new_device = []
        self._overrides = {}
        self._saved_devices = {}

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return len(self._devices)

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for device in self._devices:
            yield device

    def __getitem__(self, address):
        """Fetch a device from the ALDB."""
        return self._devices.get(address, None)

    def __setitem__(self, key, device):
        """Add or Update a device in the ALDB."""
        if (not isinstance(device, Device) and
                not isinstance(device, X10Device)):
            raise ValueError

        self._devices[key] = device

        if device.address.is_x10:
            _LOGGER.debug('New X10 Device %r: %s', key, device.description)
        else:
            _LOGGER.debug('New INSTEON Device %r: %s (%02x:%02x)',
                          key, device.description, device.cat,
                          device.subcat)

        for callback in self._cb_new_device:
            callback(device)

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    @property
    def saved_devices(self):
        """Return the device info from the saved devices file."""
        return self._saved_devices

    @property
    def overrides(self):
        """Return the device overrides."""
        return self._overrides

    @property
    def state(self):
        """Return the state of the ALDB.

        Possible states:
            empty
            loading
            loaded
        """
        return self._state

    @state.setter
    def state(self, val):
        """Set the ALDB load state."""
        self._state = val

    def add_device_callback(self, callback):
        """Register a callback to be invoked when a new device appears."""
        _LOGGER.debug('Added new callback %s ', callback)
        self._cb_new_device.append(callback)

    def add_override(self, addr, key, value):
        """Register an attribute override for a device."""
        address = Address(str(addr)).id
        _LOGGER.debug('New override for %s %s is %s', address, key, value)
        device_override = self._overrides.get(address, {})
        device_override[key] = value
        self._overrides[address] = device_override

    def create_device_from_category(self, plm, addr, cat, subcat,
                                    product_key=0x00):
        """Create a new device from the cat, subcat and product_key data."""
        saved_device = self._saved_devices.get(Address(addr).id, {})
        cat = saved_device.get('cat', cat)
        subcat = saved_device.get('subcat', subcat)
        product_key = saved_device.get('product_key', product_key)

        device_override = self._overrides.get(Address(addr).id, {})
        cat = device_override.get('cat', cat)
        subcat = device_override.get('subcat', subcat)
        product_key = device_override.get('firmware', product_key)
        product_key = device_override.get('product_key', product_key)

        return insteonplm.devices.create(plm, addr, cat, subcat, product_key)

    def has_saved(self, addr):
        """Test if device has data from the saved data file."""
        saved = False
        if self._saved_devices.get(addr, None) is not None:
            saved = True
        return saved

    def has_override(self, addr):
        """Test if device has data from a device override setting."""
        override = False
        if self._overrides.get(addr, None) is not None:
            override = True
        return override

    def add_known_devices(self, plm):
        """Add devices from the saved devices or from the device overrides."""
        from insteonplm.devices import ALDBStatus
        for addr in self._saved_devices:
            if not self._devices.get(addr):
                saved_device = self._saved_devices.get(Address(addr).id, {})
                cat = saved_device.get('cat')
                subcat = saved_device.get('subcat')
                product_key = saved_device.get('firmware')
                product_key = saved_device.get('product_key', product_key)
                device = self.create_device_from_category(
                    plm, addr, cat, subcat, product_key)
                if device:
                    _LOGGER.debug('Device with id %s added to device list '
                                  'from saved device data.', addr)
                    aldb_status = saved_device.get('aldb_status', 0)
                    device.aldb.status = ALDBStatus(aldb_status)
                    aldb = saved_device.get('aldb', {})
                    device.aldb.load_saved_records(aldb_status, aldb)
                    self[addr] = device
        for addr in self._overrides:
            if not self._devices.get(addr):
                device_override = self._overrides.get(Address(addr).id, {})
                cat = device_override.get('cat')
                subcat = device_override.get('subcat')
                product_key = device_override.get('firmware')
                product_key = device_override.get('product_key', product_key)
                device = self.create_device_from_category(
                    plm, addr, cat, subcat, product_key)
                if device:
                    _LOGGER.debug('Device with id %s added to device list '
                                  'from device override data.', addr)
                    self[addr] = device

    # Save device information
    def save_device_info(self):
        """Save all device information to the device info file."""
        if self._workdir is not None:
            devices = []
            for addr in self._devices:
                device = self._devices.get(addr)
                if not device.address.is_x10:
                    aldb = {}
                    for mem in device.aldb:
                        rec = device.aldb[mem]
                        if rec:
                            aldbRec = {'memory': mem,
                                       'control_flags': rec.control_flags.byte,
                                       'group': rec.group,
                                       'address': rec.address.id,
                                       'data1': rec.data1,
                                       'data2': rec.data2,
                                       'data3': rec.data3}
                            aldb[mem] = aldbRec
                    deviceInfo = {'address': device.address.id,
                                  'cat': device.cat,
                                  'subcat': device.subcat,
                                  'product_key': device.product_key,
                                  'aldb_status': device.aldb.status.value,
                                  'aldb': aldb}
                    devices.append(deviceInfo)
            asyncio.ensure_future(self._write_saved_device_info(devices),
                                  loop=self._loop)

    def _add_saved_device_info(self, **kwarg):
        """Register device info from the saved data file."""
        addr = kwarg.get('address')
        _LOGGER.debug('Found saved device with address %s', addr)
        self._saved_devices[addr] = kwarg

    async def load_saved_device_info(self):
        """Load device information from the device info file."""
        _LOGGER.debug("Loading saved device info.")
        deviceinfo = []
        if self._workdir:
            _LOGGER.debug("Really Loading saved device info.")
            try:
                device_file = '{}/{}'.format(self._workdir, DEVICE_INFO_FILE)
                with open(device_file, 'r') as infile:
                    try:
                        deviceinfo = json.load(infile)
                        _LOGGER.debug("Saved device file loaded")
                    except json.decoder.JSONDecodeError:
                        _LOGGER.debug("Loading saved device file failed")
            except FileNotFoundError:
                _LOGGER.debug("Saved device file not found")
        for device in deviceinfo:
            self._add_saved_device_info(**device)

    async def _write_saved_device_info(self, devices):
        if self._workdir:
            _LOGGER.debug('Writing %d devices to save file', len(devices))
            device_file = '{}/{}'.format(self._workdir, DEVICE_INFO_FILE)
            try:
                with open(device_file, 'w') as outfile:
                    json.dump(devices, outfile)
            except FileNotFoundError:
                _LOGGER.error('Cannot write to file %s', device_file)
