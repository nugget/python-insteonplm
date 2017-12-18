import insteonplm
from insteonplm.constants import *
from insteonplm.address import Address
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.extendedSend import ExtendedSend 
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl_2663_222 

class MockPLM(object):
    def __init__(self):
        self.sentmessage = ''

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
    assert device.product_key == product_key
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
    assert device.product_key == product_key
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
    product_key = None
    description = 'ToggleLinc Relay'
    model = '2466S'
    groupbutton = 0x02
    devices = SwitchedLightingControl_2663_222.create(plm, address, cat, subcat, product_key,description, model)
    assert isinstance(devices, list)
