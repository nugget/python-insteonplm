
"""Helper objects for maintaining PLM state and interfaces."""
import logging
import binascii
import insteonplm.utils

__all__ = ('Address')


class Address(object):
    """Datatype definition for INSTEON device address handling."""

    def __init__(self, addr):
        """Create an Address object."""
        self.log = logging.getLogger(__name__)
        self._is_x10 = False
        self.addr = self._normalize(addr)

    def __repr__(self):
        """Representation of the Address object."""
        return self.id

    def __str__(self):
        """String representation of the Address object."""
        return self.id

    def __eq__(self, other):
        """Test for equality."""
        equals = False
        if hasattr(other, 'addr'):
            equals = self.addr == other.addr
        return equals

    def __ne__(self, other):
        """Test for not equals."""
        not_equals = True
        if hasattr(other, 'addr'):
            not_equals = self.addr != other.addr
        return not_equals

    def __lt__(self, other):
        """Test for less than."""
        if isinstance(other, Address):
            return str(self) < str(other)
        else:
            raise TypeError

    def __gt__(self, other):
        """Test for greater than."""
        if isinstance(other, Address):
            return str(self) > str(other)
        else:
            raise TypeError

    def __hash__(self):
        """Create a hash code for the Address object."""
        return hash(self.id)

    def matches_pattern(self, other):
        """Test Address object matches the pattern of another  object."""
        matches = False
        if hasattr(other, 'addr'):
            if self.addr is None or other.addr is None:
                matches = True
            else:
                matches = self.addr == other.addr
        return matches

    def _normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        normalize = None
        if isinstance(addr, Address):
            normalize = addr.addr
            self._is_x10 = addr.is_x10

        elif isinstance(addr, bytearray):
            normalize = binascii.unhexlify(binascii.hexlify(addr).decode())

        elif isinstance(addr, bytes):
            normalize = addr

        elif isinstance(addr, str):
            addr = addr.replace('.', '')
            addr = addr[0:6]
            if addr[0:3].lower() == 'x10':
                x10_addr = Address.x10(addr[3:4], int(addr[4:6]))
                normalize = x10_addr.addr
                self._is_x10 = True
            else:
                normalize = binascii.unhexlify(addr.lower())

        elif addr is None:
            normalize = None

        else:
            self.log.warning('Address class init with unknown type %s: %r',
                             type(addr), addr)
        return normalize

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        addrstr = '00.00.00'
        if self.addr:
            if self._is_x10:
                housecode_byte = self.addr[1]
                housecode = insteonplm.utils.byte_to_housecode(housecode_byte)
                unitcode_byte = self.addr[2]
                unitcode = insteonplm.utils.byte_to_unitcode(unitcode_byte)
                addrstr = 'X10.{}.{:02d}'.format(housecode.upper(), unitcode)
            else:
                addrstr = '{}.{}.{}'.format(self.hex[0:2],
                                            self.hex[2:4],
                                            self.hex[4:6]).upper()
        return addrstr

    @property
    def hex(self):
        """Emit the address in bare hex format (aabbcc)."""
        addrstr = '000000'
        if self.addr is not None:
            addrstr = binascii.hexlify(self.addr).decode()
        return addrstr

    @property
    def bytes(self):
        """Emit the address in bytes format."""
        addrbyte = b'\x00\x00\x00'
        if self.addr is not None:
            addrbyte = self.addr
        return addrbyte

    @property
    def id(self):
        """Return the ID of the device address."""
        id = ''
        if self._is_x10:
            id = 'x10{}{:02d}'.format(self.x10_housecode, self.x10_unitcode)
        else:
            id = self.hex
        return id

    @property
    def is_x10(self):
        """Test if this is an X10 address."""
        return self._is_x10

    @is_x10.setter
    def is_x10(self, val:bool):
        """Set if this is an X10 address."""
        self._is_x10 = val

    @property
    def x10_housecode_byte(self):
        """Emit the X10 house code byte value."""
        housecode = None
        if self.is_x10:
            housecode = self.addr[1]
        return housecode

    @property
    def x10_unitcode_byte(self):
        """Emit the X10 unit code byte value."""
        unitcode = None
        if self.is_x10:
            unitcode = self.addr[2]
        return unitcode

    @property
    def x10_housecode(self):
        """Emit the X10 house code."""
        housecode = None
        if self.is_x10:
            housecode = insteonplm.utils.byte_to_housecode(self.addr[1])
        return housecode

    @property
    def x10_unitcode(self):
        """Emit the X10 unit code."""
        unitcode = None
        if self.is_x10:
            unitcode = insteonplm.utils.byte_to_unitcode(self.addr[2])
        return unitcode

    @staticmethod
    def x10(housecode, unitcode):
        """Create an X10 device address."""
        if housecode.lower() in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']:
            byte_housecode = insteonplm.utils.housecode_to_byte(housecode)
        else:
            if isinstance(housecode, str):
                self.log.error('X10 house code error: %s', housecode)
            else:
                self.log.error('X10 house code is not a string')
            raise ValueError

        if unitcode in range(1, 17):
            byte_unitcode = insteonplm.utils.unitcode_to_byte(unitcode)
        else:
            if isinstance(unitcode, int):
                self.log.error('X10 unit code error: %d', unitcode)
            else:
                self.log.error('X10 unit code is not a integer 1 - 16')
            raise ValueError

        addr = Address(bytearray([0x00, byte_housecode, byte_unitcode]))
        addr.is_x10 = True
        return addr

