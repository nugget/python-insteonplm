
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
        if self.addr is not None:
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
