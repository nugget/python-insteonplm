from insteonplm.constants import *
from insteonplm.address import Address
from .messageBase import MessageBase
from .messageFlags import MessageFlags

class ExtendedReceive(MessageBase):
    """Insteon Extended Length Message Received 0x51"""
    
    _code = MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51
    _sendSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    _receivedSize = MESSAGE_EXTENDED_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Extended Message Received'


    def __init__(self, address, target, flags, cmd1, cmd2, **kwarg):
        self._address = Address(address)
        self._target = Address(target)
        self._messageFlags = MessageFlags(flags)
        self._cmd1 = cmd1
        self._cmd2 = cmd2
        self._userdata = bytearray()

        userdata_array = {}
        for i in range(1,15):
            key = 'd' + str(i)
            userdata_array.update({key:0x00})

        for key in kwarg:
            if key in ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9','d10', 'd11','d12','d13', 'd14']:
                userdata_array[key] = kwarg[key]
        for i in range(1,15):
            key = 'd' + str(i)
            self._userdata.append(userdata_array[key])

    @classmethod
    def from_raw_message(cls, rawmessage):
        userdata = cls._userdata_to_dict(rawmessage[11:25])
        return ExtendedReceive(rawmessage[2:5], 
                               rawmessage[5:8],
                               rawmessage[8],
                               rawmessage[9],
                               rawmessage[10],
                               **userdata)

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
        return {'address': self.address, 
                'target': self.target, 
                'flags': self.flags,
                'cmd1': self.cmd1,
                'cmd2': self.cmd2,
                'userdata': self.userdata}

    @classmethod
    def _userdata_to_dict(cls, userdata):
        userdata_dict = {}
        for i in range(1,15):
            key = 'd' + str(i)
            userdata_dict.update({key:0x00})

        if isinstance(userdata, dict):
            for key in kwarg:
                if key in ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9','d10', 'd11','d12','d13', 'd14']:
                    userdata_dict[key] = kwarg[key]
        elif isinstance(userdata, bytes) or isinstance(userdata, bytearray):
            if len(userdata) == 14:
                for i in range(1, 15):
                    key = 'd' + str(i)
                    userdata_dict[key] = userdata[i-1]
            else:
                raise ValueError

        return userdata_dict