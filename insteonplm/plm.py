import asyncio
import logging
import binascii
import collections

__all__ = ('Address', 'PLMProtocol')

class Address(bytearray):
    """Datatype definition for INSTEON device address handling."""

    def __init__(self, addr):
        """Create an Address object."""
        self.log = logging.getLogger(__name__)
        self.addr = self.normalize(addr)

    def __repr__(self):
        return self.human

    def normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        if isinstance(addr, Address):
            return addr.hex
        if isinstance(addr, bytearray):
            return addr.hex()
        if isinstance(addr, bytes):
            return binascii.hexlify(addr).decode()
        if isinstance(addr, str):
            addr.replace('.', '')
            addr = addr[0:6]
            return addr.lower()
        else:
            self.log.warn('Address class initialized with unknown type %s', type(addr))
            return 'aabbcc'

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        addrstr = self.addr[0:2]+'.'+self.addr[2:4]+'.'+self.addr[4:6]
        return addrstr.upper()

    @property
    def hex(self):
        """Emit the address in bare hex format (aabbcc)."""
        return self.addr

    @property
    def bytes(self):
        r"""Emit the address in bytes format (b'\xaabbcc')."""
        return binascii.hexlify(self.addr)


class PLMCode(object):
    """Class to store PLM code definitions and attributes."""

    def __init__(self, code, name=None, size=None, rsize=None):
        """Create a new PLM code object."""
        self.code = code
        self.size = size
        self.rsize = rsize
        self.name = name


class PLMProtocol(object):
    """Class container to store PLMCode objects as a Protocol."""

    def __init__(self, version=1):
        """Create the Protocol object."""
        self.log = logging.getLogger(__name__)
        self._codelist = []
        self.add(0x50, name='INSTEON Standard Message Received', size=11)
        self.add(0x51, name='INSTEON Extended Message Received', size=25)
        self.add(0x52, name='X10 Message Received', size=4)
        self.add(0x53, name='ALL-Linking Completed', size=10)
        self.add(0x54, name='Button Event Report', size=3)
        self.add(0x55, name='User Reset Detected', size=2)
        self.add(0x56, name='ALL-Link CLeanup Failure Report', size=2)
        self.add(0x57, name='ALL-Link Record Response', size=10)
        self.add(0x58, name='ALL-Link Cleanup Status Report', size=3)
        self.add(0x60, name='Get IM Info', size=2, rsize=9)
        self.add(0x61, name='Send ALL-Link Command', size=5, rsize=6)
        self.add(0x62, name='INSTEON Fragmented Message', size=8, rsize=9)
        self.add(0x69, name='Get First ALL-Link Record', size=2)
        self.add(0x6a, name='Get Next ALL-Link Record', size=2)
        self.add(0x73, name='Get IM Configuration', size=2, rsize=6)


    def __len__(self):
        """Return the number of PLMCodes in the Protocol."""
        return len(self._codelist)

    def __iter__(self):
        for x in self._codelist:
            yield x.code

    def add(self, code, name=None, size=None, rsize=None):
        """Add a new PLMCode to the Protocol."""
        self._codelist.append(PLMCode(code, name=name, size=size, rsize=rsize))

    def lookup(self, code, fullmessage=None):
        """Return the PLMCode from a byte and optional stream buffer."""
        for x in self._codelist:
            if x.code == code:
                if code == 0x62 and fullmessage:
                    x.name = 'INSTEON Fragmented Message'
                    x.size = 8
                    x.rsize = 9
                    if len(fullmessage) >= 6:
                        flags = fullmessage[5]
                        if flags == 0x00:
                            x.name = 'INSTEON Standard Message'
                        else:
                            x.name = 'INSTEON Extended Message'
                            x.size = 22
                            x.rsize = 23

                return x

class Message(object):
    def __init__(self, rawmessage):
        self.log = logging.getLogger(__name__)
        self.code = rawmessage[1]

        if self.code == 0x50 or self.code == 0x51:
            self.address = Address(rawmessage[2:5])
            self.target = Address(rawmessage[5:8])
            self.flagsval = rawmessage[8]
            self.cmd1 = rawmessage[9]
            self.cmd2 = rawmessage[10]
            self.flags = self.decode_flags(self.flagsval)
            self.userdata = rawmessage[11:25]

    def decode_flags(self, flags):
        retval = {}
        if flags is not None:
            retval['broadcast'] = (flags & 128) > 0
            retval['group'] = (flags & 64) > 0
            retval['ack'] = (flags & 32) > 0
            retval['extended'] = (flags & 16) > 0
            retval['hops'] = (flags & 12 >> 2)
            retval['maxhops'] = (flags & 3)
        return retval

