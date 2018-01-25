import logging
import binascii
from insteonplm.address import Address
from insteonplm.constants import *
from .messageFlags import MessageFlags
from .userdata import Userdata

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

    def __str__(self):
        props = self._message_properties()
        msgstr = "{'code': 0x" + binascii.hexlify(bytes([self._code])).decode()
        first = True
        for prop in props:
            msgstr = msgstr + ', '
            if isinstance(props[prop], Address):
                msgstr = msgstr + "'" + prop + "': " + props[prop].human
            elif isinstance(props[prop], MessageFlags):
                msgstr = msgstr + "'" + prop + "': 0x" + props[prop].to_hex()
            elif isinstance(props[prop], int):
                msgstr = msgstr + "'" + prop + "': 0x" + binascii.hexlify(bytes([props[prop]])).decode()
            elif isinstance(props[prop], bytearray):
                msgstr = msgstr + "'" + prop + "': 0x" + binascii.hexlify(props[prop]).decode()
            elif isinstance(props[prop], bytes):
                msgstr = msgstr + "'" + prop + "': 0x" + binascii.hexlify(props[prop]).decode()
            else:
                msgstr = msgstr + "'" + prop + "': " + str(props[prop])
        msgstr = msgstr + '}'
        return msgstr

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
        props = self._message_properties()
        msg = bytearray([MESSAGE_START_CODE_0X02, self._code])
        i = 0
        for key in props:
            val = props[key]
            if val is None:
                pass
            elif isinstance(val,int):
                msg.append(val)
            elif isinstance(val, Address):
                if val.addr == None:
                    pass
                else:
                    msg.extend(val.bytes)
            elif isinstance(val, MessageFlags):
                print('got a MessageFlags object: ', val)
                msg.extend(val.to_byte())
            elif isinstance(val, bytearray):
                msg.extend(val)
            elif isinstance(val, bytes):
                msg.extend(val)
            elif isinstance(val, Userdata):
                msg.extend(val.bytes)
            
        return binascii.hexlify(msg).decode()

    def to_bytes(self):
        return binascii.unhexlify(self.to_hex())

    def matches_pattern(self, other):
        properties = self._message_properties()
        ismatch = False
        if isinstance(other, MessageBase) and self.code == other.code:
            for property in properties:
                p = properties[property]
                if hasattr(other, property):    
                    k =  getattr(other, property)
                    if k is not None:
                        if isinstance(p, MessageFlags):
                            ismatch = p.matches_pattern(k)
                        elif isinstance(p, Address):
                            ismatch = p.matches_pattern(k)
                        elif p == k:
                            ismatch = True
                        else:
                            ismatch = False
                            break
                else:
                    ismatch = False
                    break
        return ismatch
    
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

    def _message_properties(self):
        raise NotImplementedError


