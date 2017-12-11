from .messageBase import MessageBase
from .messageConstants import *
import binascii

class ButtonEventReport(MessageBase):
    """Insteon Button Event Report Message Received 0x54"""

    code = MESSAGE_BUTTON_EVENT_REPORT
    sendSize = MESSAGE_BUTTON_EVENT_REPORT_SIZE
    receivedSize = MESSAGE_BUTTON_EVENT_REPORT_SIZE
    description = 'INSTEON Standard Message Received'

    _events = {0x02: 'SET button tapped',
               0x03: 'SET button press and hold',
               0x04: 'SET button released',
               0x12: 'Button 2 tapped',
               0x13: 'Button 2 press and hold',
               0x14: 'Button 2 released',
               0x22: 'Button 3 tapped',
               0x23: 'Button 3 press and hold',
               0x24: 'Button 3 released'}

    def __init__(self, event):

        self.event = event
        
    @classmethod
    def from_raw_message(cls, rawmessage):
            return ButtonEventReport(rawmessage[2])

    @property
    def hex(self):
        return self._messageToHex(self.event)

    @property
    def bytes(self):
        return binascii.unhexlify(self.hex)

    @property
    def description(self):
        return self._events.get(self.event, None)

    @property
    def message(self):
        return bytearray([0x02,
                          self.code,
                          self.event])