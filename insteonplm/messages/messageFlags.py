import logging
import binascii
from insteonplm.constants import *

class MessageFlags(object):
    def __init__(self, flags=0x00):
        self.log = logging.getLogger(__name__)
        self._flags = self._normalize(flags)
        
    def __repr__(self):
        return self.to_hex()

    def __str__(self):
        return self.to_hex()

    def __eq__(self, other):
        if hasattr(other, 'to_hex'):
            return self.to_hex() == other.to_hex()
        return False

    def __ne__(self, other):
        if hasattr(other, 'to_hex'):
            return self.to_hex() != other.to_hex()
        return True

    @classmethod
    def get_properties(cls):
        property_names=[p for p in dir(cls) if isinstance(getattr(cls,p),property)]
        return property_names

    @property
    def isBroadcast(self):
        return (self._flags & MESSAGE_FLAG_BROADCAST_0X80) == MESSAGE_FLAG_BROADCAST_0X80

    @property
    def isDirect(self):
        direct = (self._flags >> 5) << 5 == 0x00
        if self.isDirectACK or self.isDirectNAK:
            direct = True
        return direct

    @property
    def isDirectACK(self):
        return (self._flags >> 5) << 5 == MESSAGE_FLAG_DIRECT_MESSAGE_ACK_0X20

    @property
    def isDirectNAK(self):
        return (self._flags >> 5) << 5 == MESSAGE_FLAG_DIRECT_MESSAGE_NAK_0XA0

    @property
    def isAllLinkBroadcast(self):
        return (self._flags >> 5) << 5 == MESSAGE_FLAG_ALL_LINK_BROADCAST_0XC0

    @property
    def isAllLinkCleanup (self):
        return (self._flags >> 5) << 5 == MESSAGE_FLAG_ALL_LINK_CLEANUP_0X40

    @property
    def isAllLinkCleanupACK(self):
        return (self._flags >> 5) << 5 == MESSAGE_FLAG_ALL_LINK_CLEANUP_ACK_0X60

    @property
    def isAllLinkCleanupNAK(self):
        return (self._flags >> 5) << 5 == MESSAGE_FLAG_ALL_LINK_CLEANUP_NAK_0XE0

    @property
    def isExtended(self):
        return (self._flags & MESSAGE_FLAG_EXTENDED_0X10) == MESSAGE_FLAG_EXTENDED_0X10

    @property
    def hopsLeft(self):
        return self._hopsleft

    @property
    def maxHops(self):
        return self._maxhops

    @maxHops.setter
    def maxHops(self, val):
        self._maxhops = val

    def get_message_type(self):
        return self._flags >> 5

    @classmethod
    def create(cls, messageType, extended=False, hopsleft=0x00, maxhops=0x00):
        """Create message flags.
        messageType: integter 0 to 7:
                        MESSAGE_TYPE_DIRECT_MESSAGE = 0
                        MESSAGE_TYPE_DIRECT_MESSAGE_ACK = 1
                        MESSAGE_TYPE_ALL_LINK_CLEANUP = 2
                        MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK = 3
                        MESSAGE_TYPE_BROADCAST_MESSAGE = 4
                        MESSAGE_TYPE_DIRECT_MESSAGE_NAK = 5 
                        MESSAGE_TYPE_ALL_LINK_BROADCAST = 6 
                        MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK = 7   
        extended: bool
        hopsleft: int  0 - 3 default 0
        maxhops:  int  0 - 3 default 0
        """
        extendedflag = 0
        if extended:
            extendedflag = 1
        flags = (messageType << 5) | (extendedflag << 4) | (hopsleft << 2) | maxhops
        return MessageFlags(flags)

    def to_byte(self):
        return bytearray([self._flags])

    def to_hex(self):
        return binascii.hexlify(self.to_byte()).decode()

    def _normalize(self, flags):
        """Take any format of flags and turn it into a hex string."""
        if isinstance(flags, MessageFlags):
            return flags.to_byte()
        if isinstance(flags, bytearray):
            return binascii.hexlify(flags)
        if isinstance(flags, int):
            return flags
        if isinstance(flags, bytes):
            return binascii.hexlify(flags)
        if isinstance(flags, str):
            flags = flags[0:2]
            return binascii.unhexlify(flags.lower())
        else:
            self.log.warning('MessageFlags class init with unknown type %s: %r',
                             type(flags), flags)
            return '000000'
