import logging
import binascii
from insteonplm.address import Address
from insteonplm.constants import *
#from .message import Message

class ClassPropertyMetaClass(type):
    """This is meta class magic to allow class attributes to also appear as an instance property."""

    @property
    def code(cls):
        return cls._code

    @property
    def sendSize(cls):
        return cls._sendSize

    @property
    def receivedSize(cls):
        return cls._receivedSize

    @property
    def description(cls):
        return cls._description

class MessageBase(metaclass=ClassPropertyMetaClass):

    _code = None
    _sendSize = None
    _receivedSize = None
    _description = "Empty message"

    @classmethod
    def get_properties(cls):
        property_names=[p for p in dir(cls) if isinstance(getattr(cls,p),property)]
        return property_names

    @property
    def code(self):
        return self._code

    @property
    def sendSize(self):
        return self._sendSize

    @property
    def receivedSize(self):
        return self._receivedSize

    @property
    def description(self):
        return self._description

    def to_hex(self):
        return NotImplemented

    def to_bytes(self):
        return binascii.unhexlify(self.to_hex())
    
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
        msg = bytearray([MESSAGE_START_CODE_0X02, self._code])
        i = 0
        for b in arg:
            if b is None:
                pass
            elif isinstance(b,int):
                msg.append(b)
            elif isinstance(b, Address):
                if b.addr == None:
                    pass
                else:
                    msg.extend(b.bytes)
            elif isinstance(b, bytearray):
                msg.extend(b)
            elif isinstance(b, bytes):
                msg.extend(b)
            
        return binascii.hexlify(msg).decode()
