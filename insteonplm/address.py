
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
        return self.hex

    def __str__(self):
        return self.hex

    def __eq__(self, other):
        if hasattr(other, 'addr'):
            return self.addr == other.addr
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, 'addr'):
            return self.addr != other.addr
        else:
            return true

    def __lt__(self, other):
        if isinstance(other, Address):
            return str(self) < str(other)
        else:
            return TypeError

    def __gt__(self, other):
        if isinstance(other, Address):
            return str(self) > str(other)
        else:
            return TypeError

    def __hash__(self):
        return hash(self.hex)

    def matches_pattern(self, other):
        if hasattr(other, 'addr'):
            if self.addr == None or other.addr == None:
                return True
            else:
                return self.addr == other.addr
        else:
            return False

    def normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        if isinstance(addr, Address):
            return addr.addr

        if isinstance(addr, bytearray):
            return binascii.unhexlify(binascii.hexlify(addr).decode())

        if isinstance(addr, bytes):
            return addr

        if isinstance(addr, str):
            addr.replace('.', '')
            addr = addr[0:6]
            return binascii.unhexlify(addr.lower())

        if addr is None:
            return None

        else:
            self.log.warning('Address class init with unknown type %s: %r',
                             type(addr), addr)
            return None

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        if self.addr is not None:
            addrstr = self.hex[0:2]+'.'+self.hex[2:4]+'.'+self.hex[4:6]
            return addrstr.upper()
        return '00.00.00'

    @property
    def hex(self):
        """Emit the address in bare hex format (aabbcc)."""
        if self.addr is not None:
            return binascii.hexlify(self.addr).decode()
        else:
            return '000000'

    @property
    def bytes(self):
        """Emit the address in bytes format (b'\xaabbcc')."""
        if self.addr is not None:
            return self.addr
        else:
            return b'\x00\x00\x00'
