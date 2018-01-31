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
    log = logging.getLogger(__name__)

    def __str__(self):
        props = self._message_properties()
        msgstr = "{'code': 0x" + binascii.hexlify(bytes([self._code])).decode()
        first = True
        for prop in props:
            for key, val in prop.items():
                msgstr = msgstr + ', '
                if isinstance(val, Address):
                    msgstr = msgstr + "'" + key + "': " + val.human
                elif isinstance(val, MessageFlags):
                    msgstr = msgstr + "'" + key + "': 0x" + val.hex
                elif isinstance(val, int):
                    msgstr = msgstr + "'" + key + "': 0x" + binascii.hexlify(bytes([val])).decode()
                elif isinstance(val, bytearray):
                    msgstr = msgstr + "'" + key + "': 0x" + binascii.hexlify(val).decode()
                elif isinstance(val, bytes):
                    msgstr = msgstr + "'" + key + "': 0x" + binascii.hexlify(val).decode()
                else:
                    msgstr = msgstr + "'" + key + "': " + str(val)
        msgstr = msgstr + '}'
        return msgstr

    def __eq__(self, other):
        if isinstance(other, MessageBase) and other.code == self._code:
            return str(self) == str(other)
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, MessageBase) and other.code == self._code:
            return str(self) != str(other)
        else:
            return True

    def __lt__(self, other):
        if isinstance(other, MessageBase):
            return str(self) < str(other)
        else:
            return TypeError

    def __gt__(self, other):
        if isinstance(other, MessageBase):
            return str(self) > str(other)
        else:
            return TypeError

    def __hash__(self):
        return hash(str(self))

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

    @property
    def hex(self):
        props = self._message_properties()
        msg = bytearray([MESSAGE_START_CODE_0X02, self._code])
        i = 0
        cmd2 = 0
        for prop in props:
            for key, val in prop.items():
                if val is None:
                    pass
                elif isinstance(val, int):
                    msg.append(val)
                elif isinstance(val, Address):
                    if val.addr == None:
                        pass
                    else:
                        msg.extend(val.bytes)
                elif isinstance(val, MessageFlags):
                    msg.extend(val.bytes)
                elif isinstance(val, bytearray):
                    msg.extend(val)
                elif isinstance(val, bytes):
                    msg.extend(val)
                elif isinstance(val, Userdata):
                    msg.extend(val.bytes)
            
        return binascii.hexlify(msg).decode()

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

    def matches_pattern(self, other):
        properties = self._message_properties()
        ismatch = False
        if isinstance(other, MessageBase) and self.code == other.code:
            for property in properties:
                for key, p in property.items():
                    if hasattr(other, key):
                        k =  getattr(other, key)
                        if isinstance(p, MessageFlags):
                            ismatch = p.matches_pattern(k)
                        elif isinstance(p, Address):
                            ismatch = p.matches_pattern(k)
                        elif isinstance(p, Userdata):
                            ismatch = p.matches_pattern(k)
                        else:
                            if p is None or k is None:
                                ismatch = True
                            else:
                                ismatch = p == k
                    else:
                        ismatch = False
                    if not ismatch:
                        break
                if not ismatch:
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


