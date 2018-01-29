from insteonplm.constants import *
from insteonplm.address import Address
from .messageBase import MessageBase
from .messageFlags import MessageFlags
from .userdata import Userdata

class ExtendedReceive(MessageBase):
    """Insteon Extended Length Message Received 0x51"""
    
    _code = MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51
    _sendSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    _receivedSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Extended Message Received'


    def __init__(self, address, target, commandtuple, userdata, cmd2=None, flags=0x10):
        
        if commandtuple.get('cmd1', None) is not None:
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError

        if cmd2 is not None:
            cmd2out = cmd2

        if cmd2out is None:
            raise ValueError

        self._address = Address(address)
        self._target = Address(target)
        self._messageFlags = MessageFlags(flags)
        # self._messageFlags.extended = 1
        self._cmd1 = cmd1
        self._cmd2 = cmd2out
        self._userdata = Userdata(userdata)

    @classmethod
    def from_raw_message(cls, rawmessage):
        userdata = Userdata.from_raw_message(rawmessage[11:25])
        return ExtendedReceive(rawmessage[2:5], 
                               rawmessage[5:8],
                               {'cmd1':rawmessage[9],
                                'cmd2':rawmessage[10]},
                               userdata,
                               flags=rawmessage[8])

    @classmethod
    def template(cls, address=None, target=None, commandtuple={}, userdata=None, cmd2=-1, flags=None,  acknak = None):
        msgraw = bytearray([0x02, cls._code])
        msgraw.extend(bytes(cls._receivedSize))
        msg = ExtendedReceive.from_raw_message(msgraw)
        
        cmd1 = commandtuple.get('cmd1', None)
        cmd2out = commandtuple.get('cmd2', None)

        if cmd2 is not -1:
            cmd2out = cmd2

        msg._address = Address(address)
        msg._target = Address(target)
        msg._messageFlags = MessageFlags(flags)
        msg._cmd1 = cmd1
        msg._cmd2 = cmd2out
        msg._userdata = Userdata(userdata)
        msg._acknak = acknak
        return msg

    @property
    def address(self):
        return self._address

    @property
    def target(self):
        return self._target

    @property
    def cmd1(self):
        return self._cmd1

    @property
    def cmd2(self):
        return self._cmd2

    @property
    def userdata(self):
        return self._userdata

    @property
    def flags(self):
        return self._messageFlags

    @property
    def targetLow(self):
        if self.target is not None and self._messageFlags.isBroadcast:
            return self.target.bytes[0]
        else:
            return None

    @property
    def targetMed(self):
        if self.target is not None and self._messageFlags.isBroadcast:
            return self.target.bytes[1]
        else:
            return None

    @property
    def targetHi(self):
        if self.target is not None and self._messageFlags.isBroadcast:
            return self.target.bytes[2]
        else:
            return None

    def _message_properties(self):
        return [{'address': self._address}, 
                {'target': self._target}, 
                {'flags': self._messageFlags},
                {'cmd1': self._cmd1},
                {'cmd2': self._cmd2},
                {'userdata': self._userdata}]