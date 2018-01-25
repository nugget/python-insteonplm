import binascii
from insteonplm.constants import *
from insteonplm.address import Address
from .messageBase import MessageBase
from .messageFlags import MessageFlags
from .userdata import Userdata

class ExtendedSend(MessageBase):

    """Send an INSTEON Extended message.
        
        address: A device hex address in any form.
        cmd1: Requred command in the cmd1 field
        cmd2: Requred command in the cmd2 field
        **kwarg: otional userdata dictionary with the following keys:
                'd1' - User data byte 0 as byte or int
                'd2' - user data byte 1 as byte or int
                ...
                'd14' - user data byte 14 as byte or int
                'd1' to 'd14' are assumed to equal 0x00 unless explicitly set
    """
    
    _code = MESSAGE_SEND_EXTENDED_MESSAGE_0X62
    _sendSize = MESSAGE_SEND_EXTENDED_MESSAGE_SIZE
    _receivedSize = MESSAGE_SEND_EXTENDED_MESSAGE_RECEIVED_SIZE
    _description = 'INSTEON Standard Message Send'


    def __init__(self, address, cmd1, cmd2, userdata, flags=0x10, acknak=None):
        self._address = Address(address)
        self._messageFlags = MessageFlags(flags)
        self._messageFlags.extended = 1
        self._cmd1 = cmd1
        self._cmd2 = cmd2
        self._userdata = Userdata(userdata)
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        userdata_dict = Userdata(rawmessage[8:22])
        return ExtendedSend(rawmessage[2:5],
                            rawmessage[6],
                            rawmessage[7],
                            userdata_dict,
                            rawmessage[5],
                            rawmessage[22:23])

    @property
    def address(self):
        return self._address

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
    def acknak(self):
        return self._acknak

    @property
    def isack(self):
        if (self._acknak is not None and self._acknak == MESSAGE_ACK):
            return True
        else:
            return False

    @property
    def isnak(self):
        if (self._acknak is not None and self._acknak == MESSAGE_NAK):
            return True
        else:
            return False

    def _message_properties(self):
        return {'address': self.address,
                'flags': self.flags,
                'cmd1': self.cmd1,
                'cmd2': self.cmd2,
                'userdata': self.userdata,
                'acknak': self.acknak}