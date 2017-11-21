import logging
import binascii

from .messageBase import MessageBase
from .messageConstants import *
from insteonplm.address import Address

from .standardReceive import StandardReceive


class Message(object):
    """Unroll a raw message string into a class with attributes."""


    def __init__(self):
        self.log = logging.getLogger(__name__)
        
    @staticmethod
    def create(rawmessage):
        log = logging.getLogger(__name__)

        if len(rawmessage) < 2:
            raise ValueError('Message is less than 2 bytes.')
        elif rawmessage[0] != 0x02: 
            raise ValueError('Message does not start with 0x02 and therefore is not a valid message.')
            
        code = rawmessage[1]
        __messageFlags = 0x00

        if code == MESSAGE_STANDARD_MESSAGE_RECEIVED:
            return StandardReceive(rawmessage[2:5], 
                                   rawmessage[5:8], 
                                   rawmessage[8],
                                   rawmessage[9],
                                   rawmessage[10])

        elif code == MESSAGE_EXTENDED_MESSAGE_RECEIVED:
            return ExtendedReceive(rawmessage[2:5], 
                                   rawmessage[5:8],
                                   rawmessage[8],
                                   rawmessage[9],
                                   rawmessage[10],
                                   rawmessage[11:25])

        elif code == MESSAGE_ALL_LINKING_COMPLETED:
            return AllLinkComplete(rawmessage[2],
                                   rawmessage[3],
                                   rawmessage[4:7],
                                   rawmessage[7],
                                   rawmessage[8],
                                   rawmessage[9])

        elif code == MESSAGE_BUTTON_EVENT_REPORT:
            return ButtonEventReport(rawmessage[2])

        elif code == MESSAGE_ALL_LINK_RECORD_RESPONSE:
            return AllLinkRecordResponse(rawmessage[2],
                                         rawmessage[3],
                                         rawmessage[4:7],
                                         rawmessage[7],
                                         rawmessage[8],
                                         rawmessage[9])

        elif code == MESSAGE_GET_IM_INFO:
            return GetImInfo(rawmessage[2:5],
                             rawmessage[5],
                             rawmessage[6],
                             rawmessage[7])


        elif code == MESSAGE_SEND_STANDARD_MESSAGE:
            # Could be a standard message or an extended message
            # Need to check the Extended Message Flag
            msg = StandardSend(rawmessage[2:5],
                               rawmessage[5],
                               rawmessage[6],
                               rawmessage[7],
                               rawmessage[8])
            if msg.isextendedflag:
                msg = ExtendedSend(rawmessage[2:5],
                                   rawmessage[5],
                                   rawmessage[6],
                                   rawmessage[7],
                                   rawmessage[8:22],
                                   rawmessage[22])
            return msg

        elif self.code == MESSAGE_GET_IM_CONFIGURATION:
            return GetImConfiguration(rawmessage[2],
                                      rawmessage[5])

    
    @staticmethod
    def iscomplete(rawmessage):
        log = logging.getLogger(__name__)

        if len(rawmessage) < 2:
            return False

        elif rawmessage[0] != 0x02:
            raise ValueError('message does not start with 0x02')

        messageBuffer = bytearray()
        filler = bytearray(30)
        messageBuffer.extend(rawmessage)
        messageBuffer.extend(filler)

        msg = Message.create(messageBuffer)

        expectedSize = 9999
        if hasattr(msg, 'receivedSize') and msg.receivedSize:
            log.debug('Found a code 0x%x message which returns %d bytes',rawmessage[1], msg.receivedSize)
            expectedSize = msg.receivedSize
        else:
            log.debug('Unable to find an receivedSize for code 0x%x', rawmessage[1])
            expectedSize = msg.sendSize

        print('Expected size: ', expectedSize)
        print('msg length: ', len(rawmessage))
        if len(rawmessage) >= expectedSize:
            return True
        else:
            log.debug('Expected %r bytes but received %r bytes. Need more bytes to process message.', expectedSize, len(rawmessage))
            return False
