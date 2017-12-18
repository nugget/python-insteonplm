import logging
import binascii
from insteonplm.address import Address
from insteonplm.constants import *
#from .message import Message

class MessageBase(object):

    code = None
    sendSize = None
    receivedSize = None
    description = "Empty message"

    def __init__(self):
        self._messageFlags = 0x00
        self.log = logging.getLogger(__name__)

#    def __repr__(self):
#        attrs = vars(self)
#        return ', '.join("%s: %r" % item for item in attrs.items())
   
    @property
    def hex(self):
        return NotImplemented

    @property
    def bytes(self):
        return NotImplemented

    @property
    def isbroadcastflag(self):
        return (self._messageFlags & MESSAGE_FLAG_BROADCAST_0X80) == MESSAGE_FLAG_BROADCAST_0X80

    @isbroadcastflag.setter
    def isbroadcastflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_BROADCAST_0X80
        else:
            self._messageFlags = self._messageFlags & ~MESSAGE_FLAG_BROADCAST_0X80

    @property
    def isgroupflag(self):
        return (self._messageFlags & MESSAGE_FLAG_GROUP_0X40) == MESSAGE_FLAG_GROUP_0X40

    @isgroupflag.setter
    def isgroupflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_GROUP_0X40
        else:
            self._messageFlags = self._messageFlags & ~MESSAGE_FLAG_GROUP_0X40

    @property
    def isnakflag(self):
        return (self._messageFlags & MESSAGE_FLAG_NAK) == MESSAGE_FLAG_NAK_0X20 

    @isnakflag.setter
    def isnakflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_NAK_0X20 
        else:
            self._messageFlags = self._messageFlags & ~MESSAGE_FLAG_NAK_0X20 

    @property
    def isextendedflag(self):
        return (self._messageFlags & MESSAGE_FLAG_EXTENDED_0X10) == MESSAGE_FLAG_EXTENDED_0X10

    @isextendedflag.setter
    def isextendedflag(self, value):
        if value:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_EXTENDED_0X10
        else:
            self._messageFlags = self._messageFlags | MESSAGE_FLAG_EXTENDED_0X10

    @property
    def hopsflag(self):
        return (self._messageFlags & MESSAGE_FLAG_HOPS_LEFT) >> 2

    @property
    def maxhopsflag(self):
        return (self._messageFlags & MESSAGE_FLAG_MAX_HOPS)

    @property 
    def acknak(self):
        if hasattr(self, '_acknak'):
            return self._acknak
        return None

    @property
    def isack(self):
        if hasattr(self, '_acknak'):
            if self._acknak == MESSAGE_ACK:
                return True
        return False

    @property
    def isnak(self):
        if hasattr(self, '_acknak'):
            if self._acknak == MESSAGE_NAK:
                return True
        return False

    
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
        msg = bytearray([MESSAGE_START_CODE_0X02, self.code])
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
