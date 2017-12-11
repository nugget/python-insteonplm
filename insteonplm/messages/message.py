import logging
import binascii

from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

from .standardReceive import StandardReceive
from .extendedReceive import ExtendedReceive
from .allLinkComplete import AllLinkComplete
from .buttonEventReport import ButtonEventReport
from .allLinkRecordResponse import AllLinkRecordResponse
from .getIMInfo import GetImInfo 
from .standardSend import StandardSend
from .extendedSend import ExtendedSend


class Message(object):
    """Unroll a raw message string into a class with attributes."""


    def __init__(self):
        self.log = logging.getLogger(__name__)
        
    @staticmethod
    def create(rawmessage):
        log = logging.getLogger(__name__)

        while len(rawmessage) > 0 and rawmessage[0] != MESSAGE_START_CODE: 
            rawmessage = rawmessage[1:]
            self.log.debug('Trimming leading buffer garbage')

        if len(rawmessage) < 2:
            return None

        code = rawmessage[1]
        _messageFlags = 0x00
        
        msgclass = Message.get_message_class(code)
        msg = None
        remainingBuffer = rawmessage

        if msgclass is not None:
            if Message.iscomplete(rawmessage):
                print('Message is complete')
                msg = msgclass.from_raw_message(rawmessage)

        return msg

    @classmethod
    def iscomplete(self, rawmessage):
        log = logging.getLogger(__name__)

        if len(rawmessage) < 2:
            return False

        elif rawmessage[0] != 0x02:
            raise ValueError('message does not start with 0x02')

        messageBuffer = bytearray()
        filler = bytearray(30)
        messageBuffer.extend(rawmessage)
        messageBuffer.extend(filler)

        msg = Message.get_message_class(rawmessage[1])

        if hasattr(msg, 'receivedSize') and msg.receivedSize:
            log.debug('Found a code 0x%x message which returns %d bytes',rawmessage[1], msg.receivedSize)
            expectedSize = msg.receivedSize
        else:
            log.debug('Unable to find an receivedSize for code 0x%x', rawmessage[1])
            return ValueError

        if len(rawmessage) >= expectedSize:
            return True
        else:
            log.debug('Expected %r bytes but received %r bytes. Need more bytes to process message.', expectedSize, len(rawmessage))
            return False

    @classmethod
    def get_message_class(cls, code):

        if code == MESSAGE_STANDARD_MESSAGE_RECEIVED:
            return StandardReceive

        elif code == MESSAGE_EXTENDED_MESSAGE_RECEIVED:
            return ExtendedReceive

        elif code == MESSAGE_ALL_LINKING_COMPLETED:
            return AllLinkComplete

        elif code == MESSAGE_BUTTON_EVENT_REPORT:
            return ButtonEventReport

        elif code == MESSAGE_ALL_LINK_RECORD_RESPONSE:
            return AllLinkRecordResponse

        elif code == MESSAGE_GET_IM_INFO:
            return GetImInfo

        elif code == MESSAGE_SEND_STANDARD_MESSAGE:
            print('Found standard send message')
            return StandardSend

        elif self.code == MESSAGE_GET_IM_CONFIGURATION:
            return MESSAGE_GET_IM_CONFIGURATION

        else:
            return None
