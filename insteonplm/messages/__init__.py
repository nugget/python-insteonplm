"""Factory module to create INSTEON Message based on the byte representation."""

import logging
import binascii

from insteonplm.constants import (MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_0X56,
                                  MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58,
                                  MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57,
                                  MESSAGE_ALL_LINKING_COMPLETED_0X53,
                                  MESSAGE_BUTTON_EVENT_REPORT_0X54,
                                  MESSAGE_CANCEL_ALL_LINKING_0X65,
                                  MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51,
                                  MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69,
                                  MESSAGE_GET_IM_CONFIGURATION_0X73,
                                  MESSAGE_GET_IM_INFO_0X60,
                                  MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A,
                                  MESSAGE_RESET_IM_0X67,
                                  MESSAGE_SEND_ALL_LINK_COMMAND_0X61,
                                  MESSAGE_SEND_STANDARD_MESSAGE_0X62,
                                  MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50,
                                  MESSAGE_START_ALL_LINKING_0X64,
                                  MESSAGE_START_CODE_0X02,
                                  MESSAGE_USER_RESET_DETECTED_0X55,
                                  MESSAGE_X10_MESSAGE_RECEIVED_0X52,
                                  MESSAGE_X10_MESSAGE_SEND_0X63)
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.x10received import X10Received
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.buttonEventReport import ButtonEventReport
from insteonplm.messages.userReset import UserReset
from insteonplm.messages.allLinkCleanupFailureReport import AllLinkCleanupFailureReport
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.allLinkCleanupStatusReport import AllLinkCleanupStatusReport
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.sendAlllinkCommand import SendAllLinkCommand
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.x10send import X10Send
from insteonplm.messages.startAllLinking import StartAllLinking
from insteonplm.messages.cancelAllLinking import CancelAllLinking
from insteonplm.messages.resetIM import ResetIM
from insteonplm.messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.getImConfiguration import GetImConfiguration


def create(rawmessage):
    """Return an INSTEON message class based on a raw byte stream."""
    rawmessage = _trim_buffer_garbage(rawmessage)

    if len(rawmessage) < 2:
        return None

    code = rawmessage[1]
    msgclass = _get_msg_class(code)

    msg = None

    if msgclass is None:
        rawmessage = rawmessage[1:]
        msg = create(rawmessage)
    else:
        if iscomplete(rawmessage):
            msg = msgclass.from_raw_message(rawmessage)

    return msg


def iscomplete(rawmessage):
    """Test if the raw message is a complete message."""
    log = logging.getLogger(__name__)

    if len(rawmessage) < 2:
        return False

    elif rawmessage[0] != 0x02:
        raise ValueError('message does not start with 0x02')

    messageBuffer = bytearray()
    filler = bytearray(30)
    messageBuffer.extend(rawmessage)
    messageBuffer.extend(filler)

    msg = _get_msg_class(rawmessage[1])

    if hasattr(msg, 'receivedSize') and msg.receivedSize:
        expectedSize = msg.receivedSize
    else:
        log.error('Unable to find an receivedSize for code 0x%x', rawmessage[1])
        return ValueError

    is_expected_size = False
    if len(rawmessage) >= expectedSize:
        is_expected_size = True

    return is_expected_size


def _get_msg_class(code):
    """Get the message class based on the message code."""
    msg_classes = {}
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_STANDARD_MESSAGE_RECEIVED_0X50,
                                 StandardReceive)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_EXTENDED_MESSAGE_RECEIVED_0X51,
                                 ExtendedReceive)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_X10_MESSAGE_RECEIVED_0X52,
                                 X10Received)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_ALL_LINKING_COMPLETED_0X53,
                                 AllLinkComplete)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_BUTTON_EVENT_REPORT_0X54,
                                 ButtonEventReport)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_USER_RESET_DETECTED_0X55,
                                 UserReset)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_ALL_LINK_CEANUP_FAILURE_REPORT_0X56,
                                 AllLinkCleanupFailureReport)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_ALL_LINK_RECORD_RESPONSE_0X57,
                                 AllLinkRecordResponse)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_ALL_LINK_CLEANUP_STATUS_REPORT_0X58,
                                 AllLinkCleanupStatusReport)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_GET_IM_INFO_0X60,
                                 GetImInfo)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_SEND_ALL_LINK_COMMAND_0X61,
                                 SendAllLinkCommand)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_SEND_STANDARD_MESSAGE_0X62,
                                 StandardSend)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_X10_MESSAGE_SEND_0X63,
                                 X10Send)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_START_ALL_LINKING_0X64,
                                 StartAllLinking)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_CANCEL_ALL_LINKING_0X65,
                                 CancelAllLinking)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_RESET_IM_0X67,
                                 ResetIM)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_GET_FIRST_ALL_LINK_RECORD_0X69,
                                 GetFirstAllLinkRecord)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_GET_NEXT_ALL_LINK_RECORD_0X6A,
                                 GetNextAllLinkRecord)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_GET_IM_CONFIGURATION_0X73,
                                 GetImConfiguration)

    return msg_classes.get(code, None)

def _add_msg_class(msg_list, code, msg_class):
    msg_list[code] = msg_class
    return msg_list


def _trim_buffer_garbage(rawmessage):
    """Remove leading bytes from a byte stream.

    A proper message byte stream begins with 0x02.
    """
    log = logging.getLogger(__name__)
    while rawmessage and rawmessage[0] != MESSAGE_START_CODE_0X02:
        log.debug('Buffer content: %s', binascii.hexlify(rawmessage))
        rawmessage = rawmessage[1:]
        log.debug('Trimming leading buffer garbage')
    return rawmessage
