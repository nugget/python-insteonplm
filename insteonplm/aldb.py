"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import binascii
import time

from .address import Address
from .devices.device import Device
from .devices.devicebase import DeviceBase

__all__ = ('ALDB')


class ALDB(object):
    """Class holds and maintains the ALL-Link Database from the PLM device."""

    def __init__(self):
        """Instantiate the ALL-Link Database object."""
        self.log = logging.getLogger(__name__)
        self.state = 'empty'
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

        if not isinstance(device, DeviceBase):
            raise ValueError

        self._devices[key] = device

        self.log.debug('New INSTEON Device %r: %s (%02x:%02x)',
                        key, device.description, device.cat,
                        device.subcat)

        for callback in self._cb_new_device:
            callback(device)

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def add_device_callback(self, callback):
        """Register a callback to be invoked when a new device appears."""
        self.log.debug('Added new callback %s ',
                      callback)
        self._cb_new_device.append(callback)

    def add_override(self, addr, key, value):
        """Register an attribute override for a device."""
        address = Address(str(addr)).hex
        self.log.info('New override for %s %s is %s', address, key, value)
        device_override = self._overrides.get(address, {})
        device_override[key] = value
        self._overrides[address] = device_override

    def add_saved_device_info(self, **kwarg):
        addr = kwarg.get('address', None)
        info = {}
        if addr is not None:
            info['cat'] = kwarg.get('cat', None)
            info['subcat'] = kwarg.get('subcat', None)
            info['product_key'] = kwarg.get('product_key', None)
        self._saved_devices[addr] = info

    def create_device_from_category(self, plm, addr, cat, subcat, product_key=0x00):
        saved_device = self._saved_devices.get(Address(addr).hex, {})
        cat = saved_device.get('cat', cat)
        subcat = saved_device.get('subcat', subcat)
        product_key = saved_device.get('product_key', product_key)

        device_override = self._overrides.get(Address(addr).hex, {})
        cat = device_override.get('cat', cat)
        subcat = device_override.get('subcat', subcat)
        product_key = device_override.get('firmware' , product_key)
        product_key = device_override.get('product_key', product_key)
        
        return Device.create(plm, addr, cat, subcat, product_key)

    def has_saved(self, addr):
        if self._saved_devices.get(addr, None) is not None:
            return True
        else:
            return False

    def has_override(self, addr):
        if self._overrides.get(addr, None) is not None:
            return True
        else:
            return False
