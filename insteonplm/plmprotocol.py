"""Helper objects for maintaining PLM state and interfaces."""
import logging
import insteonplm
from .plmcode import PLMCode
import binascii

__all__ = ('PLMProtocol')

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
        self.add(0x60, name='Get IM Info', size=2, receivedSize=9)
        self.add(0x61, name='Send ALL-Link Command', size=5, receivedSize=6)
        self.add(0x62, name='INSTEON Fragmented Message', size=8, receivedSize=9)
        self.add(0x64, name='Start ALL-Linking', size=4, receivedSize=5)
        self.add(0x65, name='Cancel ALL-Linking', size=4)
        self.add(0x67, name='Reset the IM', size=2, receivedSize=3)
        self.add(0x69, name='Get First ALL-Link Record', size=2)
        self.add(0x6a, name='Get Next ALL-Link Record', size=2)
        self.add(0x73, name='Get IM Configuration', size=2, receivedSize=6)


    def __len__(self):
        """Return the number of PLMCodes in the Protocol."""
        return len(self._codelist)

    def __iter__(self):
        for x in self._codelist:
            yield x.code

    def add(self, code, name=None, size=None, receivedSize=None):
        """Add a new PLMCode to the Protocol."""
        self._codelist.append(PLMCode(code, name=name, size=size, receivedSize=receivedSize))

    def lookup(self, code, fullmessage=None):
        """Return the PLMCode from a byte and optional stream buffer."""
        for x in self._codelist:
            if x.code == code:
                if code == 0x62 and fullmessage:
                    x.name = 'INSTEON Fragmented Message'
                    x.size = 8
                    x.receivedSize = 9
                    if len(fullmessage) >= 6:
                        flags = fullmessage[5]
                        if flags == 0x00:
                            x.name = 'INSTEON Standard Message'
                        else:
                            x.name = 'INSTEON Extended Message'
                            x.size = 22
                            x.receivedSize = 23

                return x
