from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address
import binascii

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

    code = MESSAGE_SEND_EXTENDED_MESSAGE_0X62
    sendSize = MESSAGE_SEND_EXTENDED_MESSAGE_SIZE
    receivedSize = MESSAGE_SEND_EXTENDED_MESSAGE_RECEIVED_SIZE
    description = 'INSTEON Standard Message Send'

    def __init__(self, address, cmd1, cmd2, flags=0x10, acknak=None, **kwarg ):

        self.address = Address(address)

        self._messageFlags = flags | MESSAGE_FLAG_EXTENDED_0X10
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        self.userdata = bytearray()

        userdata_array = {}
        for i in range(1,15):
            key = 'd' + str(i)
            userdata_array.update({key:0x00})

        for key in kwarg:
            if key in ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9','d10', 'd11','d12','d13', 'd14']:
                userdata_array[key] = kwarg[key]
        for i in range(1,15):
            key = 'd' + str(i)
            self.userdata.append(userdata_array[key])
        self._acknak = self._setacknak(acknak)

    @classmethod
    def from_raw_message(cls, rawmessage):
        # TODO: Find a good way to return a StandardSend if it is not an extended message
        # Not a big deal since Device should be managing the raw message process anyway.
        userdataraw = rawmessage[8:22]
        userdata_dict = {}

        i = 1
        for val in userdataraw:
            key = 'd' + str(i)
            userdata_dict.update({key:val})
            i += 1
        return ExtendedSend(rawmessage[2:5],
                            rawmessage[6],
                            rawmessage[7],
                            rawmessage[5],
                            rawmessage[22:23],
                            **userdata_dict)

    @property
    def hex(self):
        return self._messageToHex(self.address,
                                  self._messageFlags,
                                  self.cmd1,
                                  self.cmd2,
                                  self.userdata,
                                  self._acknak)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

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