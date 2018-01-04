import insteonplm
from insteonplm.constants import *
from insteonplm.aldb import ALDB
from insteonplm.address import Address
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedSend import ExtendedSend 
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl_2663_222 
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl_2475F
from insteonplm.devices.securityHealthSafety import SecurityHealthSafety 
from insteonplm.devices.securityHealthSafety import SecurityHealthSafety_2982_222
from insteonplm.devices.sensorsActuators import SensorsActuators_2450 

class MockPLM(object):
    def __init__(self):
        self.sentmessage = ''
        self.devices = ALDB()

    def send_standard(self, device, command, cmd2=None, flags=None):
        """Send an INSTEON Standard message to the PLM.
        
        device: A device hex address in any form.
        command: An insteon command tuple {'cmd1':value, 'cmd2': value'}
                Found in insteonplm.constants
                if 'cmd2' is None then 'cmd2' must be passed as an argument
        cmd2: Ignored if command['cmd2'] has a value. 
                Required if command['cmd2'] is None
        flags: Message flags

        """
        txtcommand2 = 'None'
        txtcmd2 = 'None'
        if command['cmd2'] is not None:
            txtcmd2 = '{:02x}'.format(command['cmd2'])
        if cmd2 is not None:
            txtcmd2 = '{:02x}'.format(cmd2)

        addr = Address(device)
        command1 = command['cmd1']
        command2 = command['cmd2']
        if flags is None:
            flags = 0x00

        if command2 is None:
            if cmd2 is None:
                return ValueError
            else:
                command2 = cmd2
        msg = StandardSend(addr, command1, command2, flags)
        self.sentmessage = msg.hex


    def send_extended(self, target, commandtuple, cmd2=None, flags=0x10, acknak=None, **userdata):
        if commandtuple.get('cmd1', False):
            cmd1 = commandtuple['cmd1']
            cmd2out = commandtuple['cmd2']
        else:
            raise ValueError
        if cmd2out is None:
           if cmd2 is not None:
               cmd2out = cmd2
           else:
                raise ValueError

        msg = ExtendedSend(target, cmd1, cmd2out, flags,  acknak, **userdata)
        self.sentmessage = msg.hex

def test_switchedLightingControl():
    plm = MockPLM()
    address = '1a2b3c'
    cat = 0x02
    subcat = 0x0d
    product_key = None
    description = 'ToggleLinc Relay'
    model = '2466S'
    groupbutton = 0x01

    device = SwitchedLightingControl(plm, address, cat, subcat, product_key, description, model, groupbutton)

    assert device.address.hex == address
    assert device.cat == cat
    assert device.subcat == subcat
    assert device.product_key == 0x00 # Product key should not be None
    assert device.description == description
    assert device.model == model
    #assert device.groupbutton == groupbutton
    assert device.id == address

    device.light_on()
    assert plm.sentmessage == '02621a2b3c0011ff'

def test_switchedLightingControl_group():
    plm = MockPLM()
    address = '1a2b3c'
    cat = 0x02
    subcat = 0x0d
    product_key = None
    description = 'ToggleLinc Relay'
    model = '2466S'
    groupbutton = 0x02

    device = SwitchedLightingControl(plm, address, cat, subcat, product_key, description, model, groupbutton)

    assert device.address.hex == address
    assert device.cat == cat
    assert device.subcat == subcat
    assert device.product_key == 0x00 # Product key should not be None
    assert device.description == description
    assert device.model == model
    #assert device.groupbutton == groupbutton
    assert device.id == address+'_2'

    device.light_on()
    assert plm.sentmessage == '02621a2b3c1011ff0200000000000000000000000000'

def test_switchedLightingControl_2663_222():
    plm = MockPLM()
    address = '1a2b3c'
    cat = 0x02
    subcat = 0x0d
    product_key = 0x00
    description = 'ToggleLinc Relay'
    model = '2466S'
    groupbutton = 0x02
    devices = SwitchedLightingControl_2663_222.create(plm, address, cat, subcat, product_key,description, model)
    assert isinstance(devices, list)

def test_switchedLightingControl_2663_222_status():

    class lightStatus(object):
        light1OnLevel = None
        light2OnLevel = None

        def device1_status_callback(self, id, state, value):
            print('Called device 1 callback')
            self.light1OnLevel = value
    
        def device2_status_callback(self, id, state, value):
            print('Called device 2 callback')
            self.light2OnLevel = value

    mockPLM = MockPLM()
    address = '1a2b3c'
    id1 = '1a2b3c'
    id2 = '1a2b3c_2'

    cat = 0x02
    subcat = 0x0d
    product_key = None
    description = 'ToggleLinc Relay'
    model = '2466S'

    callbacks = lightStatus()

    devices = SwitchedLightingControl_2663_222.create(mockPLM, address, cat, subcat, product_key, description, model)
    
    assert devices[0].id == id1
    assert devices[1].id == id2

    for device in devices:
        mockPLM.devices[device.id] = device
    mockPLM.devices[id1].lightOnLevel.connect(callbacks.device1_status_callback)
    mockPLM.devices[id2].lightOnLevel.connect(callbacks.device2_status_callback)

    ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd1'], COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd2'], 0x01, MESSAGE_ACK)
    statusmsg = StandardSend(address, 0x03, 0x01)

    mockPLM.devices[address].receive_message(ackmsg)
    mockPLM.devices[address].receive_message(statusmsg)
    assert callbacks.light1OnLevel == 0xff
    assert callbacks.light2OnLevel == 0x00

def test_switchedLightingControl_2663_222_status():

    class fanLincStatus(object):
        lightOnLevel = None
        fanOnLevel = None

        def device1_status_callback(self, id, state, value):
            print('Called device 1 callback')
            self.lightOnLevel = value
    
        def device2_status_callback(self, id, state, value):
            print('Called device 2 callback')
            self.fanOnLevel = value

    mockPLM = MockPLM()
    address = '1a2b3c'
    id1 = '1a2b3c'
    id2 = '1a2b3c_2'

    cat = 0x01
    subcat = 0x2e
    product_key = 0x00
    description = 'FanLinc Dual Band'
    model = '2475F'

    callbacks = fanLincStatus()

    devices = DimmableLightingControl_2475F.create(mockPLM, address, cat, subcat, product_key, description, model)
    
    assert devices[0].id == id1
    assert devices[1].id == id2

    for device in devices:
        mockPLM.devices[device.id] = device
    mockPLM.devices[id1].lightOnLevel.connect(callbacks.device1_status_callback)
    mockPLM.devices[id2].fanSpeed.connect(callbacks.device2_status_callback)

    ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd1'], COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd2'], None, MESSAGE_ACK)
    statusmsg = StandardSend(address, 0x03, 0x55)
    mockPLM.devices[address].receive_message(ackmsg)
    mockPLM.devices[address].receive_message(statusmsg)

    assert callbacks.lightOnLevel == 0x55
    
    ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd1'], 0x03, None, MESSAGE_ACK)
    statusmsg = StandardSend(address, 0x03, 0x77)
    mockPLM.devices[address].receive_message(ackmsg)
    mockPLM.devices[address].receive_message(statusmsg)

    assert callbacks.lightOnLevel == 0x55
    assert callbacks.fanOnLevel == 0x77


def test_securityhealthsafety():
    
    class sensorState(object):
        sensor = None

        def sensor_status_callback(self, id, state, value):
            print('Called sensor callback')
            self.sensor = value

    mockPLM = MockPLM()
    address = '1a2b3c'
    target = '4d5e6f'
    id1 = '1a2b3c'
    id2 = '1a2b3c_2'
    cmd1 = 0x11
    cmd2 = 0x04

    cat = 0x10
    subcat = 0x00
    product_key = 0x00
    description = 'Generic Security, Heath and Safety Device'
    model = ''

    callbacks = sensorState()

    device = SecurityHealthSafety.create(mockPLM, address, cat, subcat, product_key, description, model)
    device.sensor.connect(callbacks.sensor_status_callback)
    msg = StandardReceive(address, target, 0x00, cmd1, cmd2)
    device.receive_message(msg)
    assert callbacks.sensor == cmd2


def test_securityhealthsafety_2982_222():
    
    class sensorState(object):
        sensor = None

        def sensor_status_callback(self, id, state, value):
            print('Called sensor callback')
            self.sensor = value

    mockPLM = MockPLM()
    address = '1a2b3c'
    target = '4d5e6f'
    id1 = '1a2b3c'
    id2 = '1a2b3c_2'
    cmd1 = 0x11
    cmd2 = 0x04

    cat = 0x10
    subcat = 0x00
    product_key = 0x00
    description = 'Generic Security, Heath and Safety Device'
    model = ''

    callbacks = sensorState()

    device = SecurityHealthSafety_2982_222.create(mockPLM, address, cat, subcat, product_key, description, model)
    device.sensor.connect(callbacks.sensor_status_callback)
    msg = StandardReceive(address, target, 0x80, cmd1, cmd2)
    device.receive_message(msg)
    assert callbacks.sensor == 0x6f

def test_SensorsActuators_2450():

    class IOLincStatus(object):
        relayOnLevel = None
        sensorOnLevel = None

        def device1_status_callback(self, id, state, value):
            print('Called device 1 callback')
            self.relayOnLevel = value
    
        def device2_status_callback(self, id, state, value):
            print('Called device 2 callback')
            self.sensorOnLevel = value

    mockPLM = MockPLM()
    address = '1a2b3c'
    id1 = '1a2b3c'
    id2 = '1a2b3c_2'

    cat = 0x07
    subcat = 0x00
    product_key = 0x00
    description = 'I/O Linc'
    model = '2450'

    callbacks = IOLincStatus()

    devices = SensorsActuators_2450.create(mockPLM, address, cat, subcat, product_key, description, model)
    
    assert devices[0].id == id1
    assert devices[1].id == id2

    for device in devices:
        mockPLM.devices[device.id] = device
    mockPLM.devices[id1].relay.connect(callbacks.device1_status_callback)
    mockPLM.devices[id2].sensor.connect(callbacks.device2_status_callback)

    mockPLM.devices[id1].relay_status_request()
    ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd1'], 0x55, None, MESSAGE_ACK)
    mockPLM.devices[address].receive_message(ackmsg)
    assert callbacks.relayOnLevel == 0x55
    
    mockPLM.devices[id2].sensor_status_request()
    ackmsg = StandardSend(address, COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00['cmd1'], 0x77, None, MESSAGE_ACK)
    statusmsg = StandardSend(address, 0x03, 0x77)
    mockPLM.devices[address].receive_message(ackmsg)

    assert callbacks.relayOnLevel == 0x55
    assert callbacks.sensorOnLevel == 0x77
