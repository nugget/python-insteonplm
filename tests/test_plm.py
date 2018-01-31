import sys
sys.path.append('../')
import insteonplm
from insteonplm.constants import *

import insteonplm
from insteonplm.plm import PLM
from insteonplm.address import Address
import asyncio
import logging
import binascii

class MockConnection():
    def __init__(self):
        """Instantiate the Connection object."""
        self.log = logging.getLogger(__name__)

    @classmethod
    @asyncio.coroutine
    def create(cls, loop=None):
        conn = cls()
        conn._loop = loop or asyncio.get_event_loop()
        conn.protocol = PLM(
            connection_lost_callback=None, 
            loop=conn._loop, 
            userdefineddevices=())

        class Serial:
            def __init__(self):
                self.log = logging.getLogger(__name__)
                self.write_timeout = 0
                self.timeout = 0

        class Transport:
            def __init__(self):
                self.log = logging.getLogger(__name__)
                self.serial = Serial()
                self.lastmessage = None

            def set_write_buffer_limits(self, num):
                pass

            def get_write_buffer_size(self):
                return 128

            def write(self, data):
                self.lastmessage = data
                self.log.info('Message sent: %s', binascii.hexlify(self.lastmessage))

        conn.transport = Transport()
        return conn

@asyncio.coroutine
def do_plm(loop, log, devicelist):
    
    log.info('Connecting to Insteon PLM')

    conn = yield from MockConnection.create(loop=loop)

    def async_insteonplm_light_callback(device):
        """Log that our new device callback worked."""
        log.warn('New Device: %s %02x %02x %s, %s', device.id, device.cat, device.subcat, device.description, device.model)

    def async_light_on_level_callback(id, state, value):
        log.info('Device %s state %s value is changed to %02x', id, state, value)

    criteria = {}
    conn.protocol.add_device_callback(async_insteonplm_light_callback)

    plm = conn.protocol
    plm.connection_made(conn.transport)

    log.info('Replying with IM Info')
    log.info('_____________________')
    msg = insteonplm.messages.getIMInfo.GetImInfo(address='1a2b3c', cat=0x03, subcat=0x20, firmware=0x00, acknak = 0x06)
    print('GetIMInfo message: ', msg.hex)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(10)
    try:
        assert plm.address == Address('1a2b3c')
        print('Address check passed')
    except:
        print('Address check failed')

    try:
        assert plm.cat == 0x03
        print('Category check passed')
    except:
        print('Category check failed')

    try:
        assert plm.subcat == 0x20
        print('Subcategory check passed')
    except:
        print('Subcategory check failed')

    try:
        assert plm.product_key == 0x00
        print('Firmware check passed')
    except:
        print('Firmware check failed.')

    log.info('Replying with an All-Link Record')
    log.info('________________________________')
    msg = insteonplm.messages.allLinkRecordResponse.AllLinkRecordResponse(flags=0x00, 
                                                                          group=0x01, 
                                                                          address='4d5e6f', 
                                                                          linkdata1=0x01, 
                                                                          linkdata2=0x0b, 
                                                                          linkdata3=0x000050)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(3)
    
    log.info('Replying with Last All-Link Record')
    log.info('__________________________________')
    msg = insteonplm.messages.getNextAllLinkRecord.GetNextAllLinkRecord(0x15)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(4)
    
    log.info('Replying with Device Info Record')
    log.info('________________________________')
    msg = insteonplm.messages.standardReceive.StandardReceive(address='4d5e6f', 
                                                              target='010b00', 
                                                              commandtuple={'cmd1':0x01,'cmd2':0x00}, 
                                                              flags=MESSAGE_FLAG_BROADCAST_0X80)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(14)
    for addr in plm.devices:
        print('Device: ', addr)
    log.info('Replying with Device Status Record')
    log.info('__________________________________')
    msg = insteonplm.messages.standardSend.StandardSend(address='4d5e6f', 
                                                        commandtuple={'cmd1':0x19, 'cmd2':0x00}, 
                                                        flags=0x00,
                                                        acknak=0x06)
    plm.data_received(msg.bytes)
    asyncio.sleep(.5)
    msg = insteonplm.messages.standardReceive.StandardReceive(address='4d5e6f', 
                                                              target='1a2b3c', 
                                                              commandtuple={'cmd1':0x17, 'cmd2':0xff}, 
                                                              flags=0x20)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(15)

    try:
        assert plm.devices['4d5e6f'].states[0x01].value == 0xff
        print('Light On Level test passed')
    except:
        print('Light On Level test failed ', plm.devices['4d5e6f'].states[0x01].value)

    msg = insteonplm.messages.standardSend.StandardSend(address='4d5e6f', commandtuple={'cmd1':0x011,'cmd2':0xff}, flags=0x00, acknak=0x15)
    plm.data_received(msg.bytes)
    yield from asyncio.sleep(8)

    try:
        assert plm.transport.lastmessage == msg.bytes[:-1]
        print('NAK test passed')
    except:
        print('NAK test failed: ', plm.transport.lastmessage)

    loop.stop()

def test_plm1():
    devicelist = (
        {
            "address": "3c4fc5",
            "cat": 0x01,
            "subcat": 0x0b,
            "product_key": 0x000050
        },
        {
            "address": "43af9b",
            "cat": 0x02,
            "subcat": 0x1a,
            "product_key": 0x00
        }
    )
    
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    asyncio.async(do_plm(loop, log, devicelist))
    loop.run_forever()
    loop.close()

if __name__ == "__main__":
    test_plm1()