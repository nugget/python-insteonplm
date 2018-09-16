"""INSTEON Messages Module."""

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
                                  MESSAGE_X10_MESSAGE_SEND_0X63,
                                  MESSAGE_SET_IM_CONFIGURATION_0X6B,
                                  MESSAGE_MANAGE_ALL_LINK_RECORD_0X6F)
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.x10received import X10Received
from insteonplm.messages.allLinkComplete import AllLinkComplete
from insteonplm.messages.buttonEventReport import ButtonEventReport
from insteonplm.messages.userReset import UserReset
from insteonplm.messages.allLinkCleanupFailureReport import (
    AllLinkCleanupFailureReport)
from insteonplm.messages.allLinkRecordResponse import AllLinkRecordResponse
from insteonplm.messages.allLinkCleanupStatusReport import (
    AllLinkCleanupStatusReport)
from insteonplm.messages.getIMInfo import GetImInfo
from insteonplm.messages.sendAlllinkCommand import SendAllLinkCommand
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.x10send import X10Send
from insteonplm.messages.startAllLinking import StartAllLinking
from insteonplm.messages.cancelAllLinking import CancelAllLinking
from insteonplm.messages.resetIM import ResetIM
from insteonplm.messages.setImConfiguration import SetIMConfiguration
from insteonplm.messages.getFirstAllLinkRecord import GetFirstAllLinkRecord
from insteonplm.messages.getNextAllLinkRecord import GetNextAllLinkRecord
from insteonplm.messages.getImConfiguration import GetImConfiguration
from insteonplm.messages.manageAllLinkRecord import ManageAllLinkRecord


_LOGGER = logging.getLogger(__name__)


def create(rawmessage):
    """Return an INSTEON message class based on a raw byte stream."""
    rawmessage = _trim_buffer_garbage(rawmessage)

    if len(rawmessage) < 2:
        return (None, rawmessage)

    code = rawmessage[1]
    msgclass = _get_msg_class(code)

    msg = None

    remaining_data = rawmessage
    if msgclass is None:
        _LOGGER.debug('Did not find message class 0x%02x', rawmessage[1])
        rawmessage = rawmessage[1:]
        rawmessage = _trim_buffer_garbage(rawmessage, False)
        if rawmessage:
            _LOGGER.debug('Create: %s', create)
            _LOGGER.debug('rawmessage: %s', binascii.hexlify(rawmessage))
            msg, remaining_data = create(rawmessage)
        else:
            remaining_data = rawmessage
    else:
        if iscomplete(rawmessage):
            msg = msgclass.from_raw_message(rawmessage)
            if msg:
                remaining_data = rawmessage[len(msg.bytes):]
    # _LOGGER.debug("Returning msg: %s", msg)
    # _LOGGER.debug('Returning buffer: %s', binascii.hexlify(remaining_data))
    return (msg, remaining_data)


def iscomplete(rawmessage):
    """Test if the raw message is a complete message."""
    if len(rawmessage) < 2:
        return False

    if rawmessage[0] != 0x02:
        raise ValueError('message does not start with 0x02')

    messageBuffer = bytearray()
    filler = bytearray(30)
    messageBuffer.extend(rawmessage)
    messageBuffer.extend(filler)

    msg = _get_msg_class(rawmessage[1])

    if hasattr(msg, 'receivedSize') and msg.receivedSize:
        expectedSize = msg.receivedSize
    else:
        _LOGGER.error('Unable to find a receivedSize for code 0x%x',
                      rawmessage[1])
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
                                 MESSAGE_MANAGE_ALL_LINK_RECORD_0X6F,
                                 ManageAllLinkRecord)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_SET_IM_CONFIGURATION_0X6B,
                                 SetIMConfiguration)
    msg_classes = _add_msg_class(msg_classes,
                                 MESSAGE_GET_IM_CONFIGURATION_0X73,
                                 GetImConfiguration)

    return msg_classes.get(code, None)


def _add_msg_class(msg_list, code, msg_class):
    msg_list[code] = msg_class
    return msg_list


def _trim_buffer_garbage(rawmessage, debug=True):
    """Remove leading bytes from a byte stream.

    A proper message byte stream begins with 0x02.
    """
    while rawmessage and rawmessage[0] != MESSAGE_START_CODE_0X02:
        if debug:
            _LOGGER.debug('Buffer content: %s', binascii.hexlify(rawmessage))
            _LOGGER.debug('Trimming leading buffer garbage')
        rawmessage = rawmessage[1:]
    return rawmessage
