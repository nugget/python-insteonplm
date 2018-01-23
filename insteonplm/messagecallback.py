import logging
from .constants import *
from insteonplm.messages.messageBase import MessageBase
from insteonplm.messages.messageFlags import MessageFlags

class MessageCallback(object):
    def __init__(self):
        self._dict = {}
        self.log = logging.getLogger(__name__)

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        for itm in self._dict:
            yield itm

    def __getitem__(self, key):
        """Gets an item from the callback list.  Accepts a string in the format of
           'code:cmd1:cmd2:acknak.  For example, '50:11:None:None' would mean
           a Standard Message (0x50) Light On (0x11) command with any On Level and 
           any Ack/Nak value.  
           
           If a direct match is not found the following order is used:
               1) Any cmd2 value
               2) Any cmd1 value
               3) Any Ack/Nak value
           For example, if the key is {'code':0x50, 'cmd1':None, 'cmd2':None, 'acknak':None} 
           (i.e. any Standard Message (0x50)) and the message is {'code':0x50, 'cmd1':0x11, 'cmd2:0xff, 'acknak':None}
           this will be a match.
        """
        foundKey = self._match_msg(key)
        return self._dict.get(foundKey, [])


    def __setitem__(self, key, value):
        self._dict[key] = value

    def add_message_callback(self, msg, callback, override=False):
        if override:
            print('Setting callback: ', callback)
            self[msg] = [callback]
        else:
            print('Appending callback: ', callback)
            cb = self[msg]
            cb.append(callback)
            print('Total callbacks for message: ', len(cb))
            self[msg] = cb


    def get_callbacks_from_message(self, msg):
        foundKey = self._match_msg(msg)
        if foundKey is not None:
            return self[foundKey]
        else:
            return []

    def _match_msg(self, msg):
        print('')
        print('Starting new message key search')
        properties = msg.get_properties()
        ismatch = False
        for key in self._dict:
            if key.code == msg.code:
                for property in properties:
                    print('Checking property: ', property)
                    p = getattr(msg, property)
                    if hasattr(key, property):   
                        k =  getattr(key, property)
                        if k is not None:
                            if p == k:
                                print(property, ' with value ', p, " is equal to ", k)
                                ismatch = True
                            else:
                                print(property, ' with value ', p, " is not equal ", k)
                                ismatch = False
                                break
                    else:
                        print('Properties do not match')
                        ismatch = False
                        break
                if ismatch:
                    print('Found key for message')
                    return key
        return None

    def _dict_to_key(self, dictkey):
        code = dictkey.get('code', None)
        cmd1 = dictkey.get('cmd1', None)
        cmd2 = dictkey.get('cmd2', None)
        acknak = dictkey.get('acknak', None)

        keystr = ''
        for val in [code, cmd1, cmd2, acknak]:
            if len(keystr) > 0:
                keystr += ":"
            if val == None:
                txtval = 'None'
            else:
                txtval = '{:02x}'.format(val)

            keystr += txtval
        return keystr

    def _key_to_dict(self, txtkey):
        keyarray = txtkey.split(':')
        if not len(keyarray) == 4:
            raise KeyError
        for i in [0,1,2,3]:
            if keyarray[i] == 'None':
                keyarray[i] = None
            else:
                keyarray[i] = int(keyarray[i], 16)
        key = {
            'code':keyarray[0],
            'cmd1':keyarray[1],
            'cmd2':keyarray[2],
            'acknak':keyarray[3]
            }
        return key

    def _match_flags(self, msg, key):
        return True

