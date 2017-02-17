"""Helper objects for maintaining PLM state and interfaces."""
import logging
import binascii

__all__ = ('Address', 'PLMProtocol')

class Address(object):
    """Datatype definition for INSTEON device address handling."""

    def __init__(self, addr):
        """Create an Address object."""
        self.log = logging.getLogger(__name__)
        self.addr = self.normalize(addr)

    def __repr__(self):
        return self.human

    def __str__(self):
        return self.hex

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
        else:
            self.log.warning('Address class init with unknown type %s: %r',
                             type(addr), addr)
            return '000000'

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

    def __init__(self):
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
    """Unroll a raw message string into a class with attributes."""
    def __init__(self, rawmessage):
        self.log = logging.getLogger(__name__)
        self.code = rawmessage[1]
        self.rawmessage = rawmessage

        if self.code == 0x50 or self.code == 0x51:
            # INSTEON Standard and Extended Message
            self.address = Address(rawmessage[2:5])
            self.target = Address(rawmessage[5:8])
            self.flagsval = rawmessage[8]
            self.cmd1 = rawmessage[9]
            self.cmd2 = rawmessage[10]
            self.flags = self.decode_flags(self.flagsval)
            self.userdata = rawmessage[11:25]

        elif self.code == 0x53:
            # ALL-Linking Complete
            self.linkcode = rawmessage[2]
            self.group = rawmessage[3]
            self.address = Address(rawmessage[4:7])
            self.category = rawmessage[7]
            self.subcategory = rawmessage[8]
            self.firmware = rawmessage[9]

        elif self.code == 0x54:
            events = {0x02: 'SET button tapped',
                      0x03: 'SET button press and hold',
                      0x04: 'SET button released',
                      0x12: 'Button 2 tapped',
                      0x13: 'Button 2 press and hold',
                      0x14: 'Button 2 released',
                      0x22: 'Button 3 tapped',
                      0x23: 'Button 3 press and hold',
                      0x24: 'Button 3 released'}

            self.event = rawmessage[2]
            self.description = events.get(self.event, None)

        elif self.code == 0x57:
            # ALL-Link Record Response
            self.flagsval = rawmessage[2]
            self.group = rawmessage[3]
            self.address = Address(rawmessage[4:7])
            self.linkdata1 = rawmessage[7]
            self.linkdata2 = rawmessage[8]
            self.linkdata3 = rawmessage[9]

        elif self.code == 0x60:
            self.address = Address(rawmessage[2:5])
            self.category = rawmessage[5]
            self.subcategory = rawmessage[6]
            self.firmware = rawmessage[7]

        elif self.code == 0x62:
            # 0262395fa4001900
            self.address = Address(rawmessage[2:5])
            self.flagsval = rawmessage[5]

        elif self.code == 0x73:
            self.flagsval = rawmessage[2]
            self.spare1 = rawmessage[3]
            self.spare2 = rawmessage[4]

    def __repr__(self):
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def decode_flags(self, flags):
        """Turn INSTEON message flags into a dict."""
        retval = {}
        if flags is not None:
            retval['broadcast'] = (flags & 128) > 0
            retval['group'] = (flags & 64) > 0
            retval['ack'] = (flags & 32) > 0
            retval['extended'] = (flags & 16) > 0
            retval['hops'] = (flags & 12 >> 2)
            retval['maxhops'] = (flags & 3)
        return retval
