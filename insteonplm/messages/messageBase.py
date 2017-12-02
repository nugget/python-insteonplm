import logging
import binascii
from insteonplm.address import Address
from .messageConstants import *
#from .message import Message

class MessageBase(object):

    def __init__(self):
        self.code = None
        self.sendSize = None
        self.receivedSize = None
        self.description = "Empty message"
        self._messageFlags = 0x00

#    def __repr__(self):
#        attrs = vars(self)
#        return ', '.join("%s: %r" % item for item in attrs.items())

    @property
    def isbroadcastflag(self):
        return (self._messageFlags & MESSAGE_FLAG_BROADCAST) == MESSAGE_FLAG_BROADCAST

    @isbroadcastflag.setter
    def isbroadcastflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_BROADCAST
        else:
            self._messageFlags = self._messageFlags & ~MESSAGE_FLAG_BROADCAST

    @property
    def isgroupflag(self):
        return (self._messageFlags & MESSAGE_FLAG_GROUP) == MESSAGE_FLAG_GROUP

    @isgroupflag.setter
    def isgroupflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_GROUP
        else:
            self._messageFlags = self._messageFlags & ~MESSAGE_FLAG_GROUP

    @property
    def isnakflag(self):
        return (self._messageFlags & MESSAGE_FLAG_NAK) == MESSAGE_FLAG_NAK

    @isnakflag.setter
    def isnakflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_NAK
        else:
            self._messageFlags = self._messageFlags & ~MESSAGE_FLAG_NAK

    @property
    def isextendedflag(self):
        return (self._messageFlags & MESSAGE_FLAG_EXTENDED) == MESSAGE_FLAG_EXTENDED

    @isextendedflag.setter
    def isextendedflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_EXTENDED
        else:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_EXTENDED

    @property
    def hopsflag(self):
        return (self._messageFlags & MESSAGE_FLAG_HOPS_LEFT) >> 2

    @property
    def maxhopsflag(self):
        return (self._messageFlags & MESSAGE_FLAG_MAX_HOPS)

    
    def fromDevice(self, devices):
        try:
            device = devices[self.address.hex]
        except:
            device = None
        return device

    def toDevice(self, devices):
        try:
            device = devices[self.target.hex]
        except:
            device = None
        return device

    def _setacknak(self, acknak):
        if isinstance(acknak, bytearray) and len(acknak) > 0:
            return acknak[0]
        else:
            return acknak

    def _messageToHex(self, *arg):
        msg = bytearray([MESSAGE_START_CODE, self.code])
        i = 0
        for b in arg:
            if b is None:
                pass
            elif isinstance(b,int):
                msg.append(b)
            elif isinstance(b, Address):
                msg.extend(b.bytes)
            elif isinstance(b, bytearray):
                msg.extend(b)
            elif isinstance(b, bytes):
                msg.extend(b)
            
        return binascii.hexlify(msg).decode()