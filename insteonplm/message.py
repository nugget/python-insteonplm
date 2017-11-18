"""Helper objects for maintaining PLM state and interfaces."""
import logging
import binascii

class Message(object):
    """Unroll a raw message string into a class with attributes."""
    def __init__(self, rawmessage):
        self.log = logging.getLogger(__name__)
        self.code = rawmessage[1]
        self.rawmessage = rawmessage

        if self.code == 0x50 or self.code == 0x51:
            # INSTEON Standard and Extended Message
            self.address = Address(rawmessage[2:5])
            self.target = Address(rawmessage[5:8])
            self.flagsval = rawmessage[8]
            self.cmd1 = rawmessage[9]
            self.cmd2 = rawmessage[10]
            self.flags = self.decode_flags(self.flagsval)
            self.userdata = rawmessage[11:25]

        elif self.code == 0x53:
            # ALL-Linking Complete
            self.linkcode = rawmessage[2]
            self.group = rawmessage[3]
            self.address = Address(rawmessage[4:7])
            self.category = rawmessage[7]
            self.subcategory = rawmessage[8]
            self.firmware = rawmessage[9]

        elif self.code == 0x54:
            events = {0x02: 'SET button tapped',
                      0x03: 'SET button press and hold',
                      0x04: 'SET button released',
                      0x12: 'Button 2 tapped',
                      0x13: 'Button 2 press and hold',
                      0x14: 'Button 2 released',
                      0x22: 'Button 3 tapped',
                      0x23: 'Button 3 press and hold',
                      0x24: 'Button 3 released'}

            self.event = rawmessage[2]
            self.description = events.get(self.event, None)

        elif self.code == 0x57:
            # ALL-Link Record Response
            self.flagsval = rawmessage[2]
            self.group = rawmessage[3]
            self.address = Address(rawmessage[4:7])
            self.linkdata1 = rawmessage[7]
            self.linkdata2 = rawmessage[8]
            self.linkdata3 = rawmessage[9]

        elif self.code == 0x60:
            self.address = Address(rawmessage[2:5])
            self.category = rawmessage[5]
            self.subcategory = rawmessage[6]
            self.firmware = rawmessage[7]

        elif self.code == 0x62:
            # 0262395fa4001900
            self.address = Address(rawmessage[2:5])
            self.flagsval = rawmessage[5]

        elif self.code == 0x73:
            self.flagsval = rawmessage[2]
            self.spare1 = rawmessage[3]
            self.spare2 = rawmessage[4]

    def __repr__(self):
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    def decode_flags(self, flags):
        """Turn INSTEON message flags into a dict."""
        retval = {}
        if flags is not None:
            retval['broadcast'] = (flags & 128) > 0
            retval['group'] = (flags & 64) > 0
            retval['ack'] = (flags & 32) > 0
            retval['extended'] = (flags & 16) > 0
            retval['hops'] = (flags & 12 >> 2)
            retval['maxhops'] = (flags & 3)
        return retval
