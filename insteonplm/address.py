
"""Helper objects for maintaining PLM state and interfaces."""
import logging
import binascii

__all__ = ('Address')


class Address(object):
    """Datatype definition for INSTEON device address handling."""

    def __init__(self, addr):
        """Create an Address object."""
        self.log = logging.getLogger(__name__)
        self.addr = self.normalize(addr)
        self._is_x10 = False

    def __repr__(self):
        """Representation of the Address object."""
        return self.hex

    def __str__(self):
        """String representation of the Address object."""
        return self.hex

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
        return hash(self.hex)

    def matches_pattern(self, other):
        """Test Address object matches the pattern of another  object."""
        matches = False
        if hasattr(other, 'addr'):
            if self.addr is None or other.addr is None:
                matches = True
            else:
                matches = self.addr == other.addr
        return matches

    def normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        normalize = None
        if isinstance(addr, Address):
            normalize = addr.addr

        elif isinstance(addr, bytearray):
            normalize = binascii.unhexlify(binascii.hexlify(addr).decode())

        elif isinstance(addr, bytes):
            normalize = addr

        elif isinstance(addr, str):
            addr = addr.replace('.', '')
            addr = addr[0:6]
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
                housecode = self._byte_to_housecode(housecode_byte)
                unitcode_byte = self.addr[2]
                unitcode = self._byte_to_unitcode(unitcode_byte)
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
            housecode = self._byte_to_housecode(self.addr[1])
        return housecode

    @property
    def x10_unitcode(self):
        """Emit the X10 unit code."""
        unitcode = None
        if self.is_x10:
            unitcode = self._byte_to_unitcode(self.addr[2])
        return unitcode

    @classmethod
    def x10(cls, housecode, unitcode):
        """Create an X10 device address."""
        if housecode.lower() in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']:
            byte_housecode = cls._housecode_to_byte(housecode)
        else:
            raise ValueError

        if unitcode in range(1, 17):
            byte_unitcode = cls._unitcode_to_byte(unitcode)

        print('Housecode: ', housecode, ' is ', byte_housecode)
        addr = Address(bytearray([0x00, byte_housecode, byte_unitcode]))
        addr.is_x10 = True
        return addr

    HC_LOOKUP = {'a': 0x06,
                 'b': 0x0e,
                 'c': 0x02,
                 'd': 0x0a,
                 'e': 0x01,
                 'f': 0x09,
                 'g': 0x05,
                 'h': 0x0d,
                 'i': 0x07,
                 'j': 0x0f,
                 'k': 0x03,
                 'l': 0x0b,
                 'm': 0x00,
                 'n': 0x08,
                 'o': 0x04,
                 'p': 0x0c}

    DC_LOOKUP = {1: 0x06,
                 2: 0x0e,
                 3: 0x02,
                 4: 0x0a,
                 5: 0x01,
                 6: 0x09,
                 7: 0x05,
                 8: 0x0d,
                 9: 0x07,
                 10: 0x0f,
                 11: 0x03,
                 12: 0x0b,
                 13: 0x00,
                 14: 0x08,
                 15: 0x04,
                 16: 0x0c}

    @classmethod
    def _housecode_to_byte(cls, housecode):
        return cls.HC_LOOKUP.get(housecode.lower())

    @classmethod
    def _unitcode_to_byte(cls, unitcode):
        return cls.DC_LOOKUP.get(unitcode)

    @classmethod
    def _byte_to_housecode(cls, bytecode):
        rev_hc = dict([reversed(i) for i in cls.HC_LOOKUP.items()])
        return rev_hc.get(bytecode).upper()

    @classmethod
    def _byte_to_unitcode(cls, bytecode):
        rev_dc = dict([reversed(i) for i in cls.DC_LOOKUP.items()])
        return rev_dc.get(bytecode)

