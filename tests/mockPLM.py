from insteonplm.messagecallback import MessageCallback

class MockPLM(object):
    def __init__(self, loop=None):
        self.sentmessage = ''
        #self.devices = ALDB()
        self._message_callbacks = MessageCallback()
        self.loop = loop

    @property
    def message_callbacks(self):
        return self._message_callbacks

    def send_msg(self, msg):
        self.sentmessage = msg.hex

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

    def message_received(self, msg):
        #for key in self._message_callbacks:
        #    #print(len(self._message_callbacks[key]), ' callbacks in key ', key)
        #    for callback in self._message_callbacks[key]:
        #        print(key, callback.__name__)
        for callback in self._message_callbacks.get_callbacks_from_message(msg):
            print('PLM calling: ', callback)
            callback(msg)