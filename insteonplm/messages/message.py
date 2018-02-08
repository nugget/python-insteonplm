import logging
import binascii

from .messageBase import MessageBase
from insteonplm.constants import *
from insteonplm.address import Address

from .standardReceive import StandardReceive
from .extendedReceive import ExtendedReceive
from .x10received import X10Received 
from .allLinkComplete import AllLinkComplete
from .buttonEventReport import ButtonEventReport
from .userReset import UserReset
from .allLinkFailureReport import AllLinkCleanupFailureReport 
from .allLinkRecordResponse import AllLinkRecordResponse
from .allLinkCleanupStatusReport import AllLinkCleanupStatusReport
from .getIMInfo import GetImInfo 
from .sendAlllinkCommand import SendAllLinkCommand
from .standardSend import StandardSend
from .extendedSend import ExtendedSend
from .x10send import X10Send 
from .startAllLinking import StartAllLinking
from .cancelAllLinking import CancelAllLinking
from .resetIM import ResetIM
from .getFirstAllLinkRecord import GetFirstAllLinkRecord
from .getNextAllLinkRecord import GetNextAllLinkRecord
from .getImConfiguration import GetImConfiguration
from .messageFlags import MessageFlags


class Message(object):
    """Unroll a raw message string into a class with attributes."""


    def __init__(self):
        self.log = logging.getLogger(__name__)
        
    @staticmethod
    def create(rawmessage):
        log = logging.getLogger(__name__)

        rawmessage = Message._trim_buffer_garbage(rawmessage)

        if len(rawmessage) < 2:
            return None

        code = rawmessage[1]
        msgclass = Message.get_message_class(code)

        msg = None

        if msgclass is None:
            rawmessage = rawmessage[1:]
            msg = Message.create(rawmessage)
        else:
            remainingBuffer = rawmessage
            if Message.iscomplete(rawmessage):
                msg = msgclass.from_raw_message(rawmessage)

        return msg

    @classmethod
    def _trim_buffer_garbage(cls, rawmessage):
        log = logging.getLogger(__name__)
        while len(rawmessage) > 0 and rawmessage[0] != MESSAGE_START_CODE_0X02: 
            log.debug('Buffer content: %s', binascii.hexlify(rawmessage))
            rawmessage = rawmessage[1:]
            log.debug('Trimming leading buffer garbage')
        return rawmessage

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
            expectedSize = msg.receivedSize
        else:
            log.error('Unable to find an receivedSize for code 0x%x', rawmessage[1])
            return ValueError

        if len(rawmessage) >= expectedSize:
            return True
        else:
            #log.debug('Expected %r bytes but received %r bytes. Need more bytes to process message.', expectedSize, len(rawmessage))
            return False

    @classmethod
    def get_message_class(cls, code):
        messageclasses = {}
        messageclasses[MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50] = StandardReceive
        messageclasses[MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51] = ExtendedReceive
        messageclasses[MESSAGE_X10_MESSAGE_RECEIVED_0X52] = X10Received
        messageclasses[MESSAGE_ALL_LINKING_COMPLETED_0X53] = AllLinkComplete
        messageclasses[MESSAGE_BUTTON_EVENT_REPORT_0X54] = ButtonEventReport
        messageclasses[MESSAGE_USER_RESET_DETECTED_0X55] = UserReset
        messageclasses[MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_0X56] = AllLinkCleanupFailureReport
        messageclasses[MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57] = AllLinkRecordResponse
        messageclasses[MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58] = AllLinkCleanupStatusReport
        messageclasses[MESSAGE_GET_IM_INFO_0X60] = GetImInfo
        messageclasses[MESSAGE_SEND_ALL_LINK_COMMAND_0X61] = SendAllLinkCommand
        messageclasses[MESSAGE_SEND_STANDARD_MESSAGE_0X62] = StandardSend
        messageclasses[MESSAGE_X10_MESSAGE_SEND_0X63] = X10Send
        messageclasses[MESSAGE_START_ALL_LINKING_0X64] = StartAllLinking
        messageclasses[MESSAGE_CANCEL_ALL_LINKING_0X65] = CancelAllLinking
        messageclasses[MESSAGE_RESET_IM_0X67] = ResetIM
        messageclasses[MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69] = GetFirstAllLinkRecord
        messageclasses[MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A] = GetNextAllLinkRecord
        messageclasses[MESSAGE_GET_IM_CONFIGURATION_0X73] = GetImConfiguration
        
        return messageclasses.get(code, None)