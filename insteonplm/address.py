
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
        if self.human is not None:
            return self.human
        return ''

    def __str__(self):
        if self.hex is not None:
            return self.hex
        return ''

    def __eq__(self, other):
        return self.hex == other.hex

    def __ne__(self, other):
        return self.hex != other.hex

    def normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        if isinstance(addr, Address):
            return addr.hex
        if isinstance(addr, bytearray):
            return binascii.hexlify(addr).decode()
        if isinstance(addr, bytes):
            return binascii.hexlify(addr).decode()
        if isinstance(addr, str):
            addr.replace('.', '')
            addr = addr[0:6]
            return addr.lower()
        if addr is None:
            return None
        else:
            self.log.warning('Address class init with unknown type %s: %r',
                             type(addr), addr)
            return '000000'

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        if self.addr is not None:
            addrstr = self.addr[0:2]+'.'+self.addr[2:4]+'.'+self.addr[4:6]
            return addrstr.upper()
        return None

    @property
    def hex(self):
        """Emit the address in bare hex format (aabbcc)."""
        if self.addr is not None:
            return self.addr
        return None

    @property
    def bytes(self):
        r"""Emit the address in bytes format (b'\xaabbcc')."""
        if self.addr is not None:
            return binascii.unhexlify(self.addr)
        return None
