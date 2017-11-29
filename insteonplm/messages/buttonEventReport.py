from .messageBase import MessageBase
from .messageConstants import *

class ButtonEventReport(MessageBase):
    """Insteon Button Event Report Message Received 0x54"""

    def __init__(self, event):
        self.code = MESSAGE_BUTTON_EVENT_REPORT
        self.sendSize = MESSAGE_BUTTON_EVENT_REPORT_SIZE
        self.returnSize = MESSAGE_BUTTON_EVENT_REPORT_SIZE
        self.name = 'INSTEON Standard Message Received'

        self._events = {0x02: 'SET button tapped',
                         0x03: 'SET button press and hold',
                         0x04: 'SET button released',
                         0x12: 'Button 2 tapped',
                         0x13: 'Button 2 press and hold',
                         0x14: 'Button 2 released',
                         0x22: 'Button 3 tapped',
                         0x23: 'Button 3 press and hold',
                         0x24: 'Button 3 released'}

        self.event = event
        
    @property
    def description(self):
        return self._events.get(self.event, None)

    @property
    def message(self):
        return bytearray([0x02,
                          self.code,
                          self.event])