"""Module to maintain PLM state information and network interface."""
import asyncio
import logging
import binascii
import time

from .address import Address
from .devices.device import Device

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
        # TEH - Removing this since 0x00 is a valid device category
        #if 'cat' not in value or value['cat'] == 0:
        #    self.log.debug('Ignoring device setitem with no cat: %s', value)
        #    return

        if key in self._devices:
            if 'firmware' in value and value['firmware'] < 255:
                self._devices[key].update(value)
        else:
            #productdata = self.ipdb[value['cat'], value['subcat']]
            #value.update(productdata._asdict())
            device = value['device']
            address = Address(key)
            value['address_hex'] = device.address.hex
            value['address'] = device.address.human
            value['description'] = device.description
            value['model'] = device.model
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

    def get_device_from_categories(self, plm, addr, cat, subcat, firmware=None):
        return Device.create(plm, addr, cat, subcat, firmware)

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
