from .constants import *

class MessageCallback(object):
    def __init__(self):
        self._dict = {}

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
        keystr = ''
        if isinstance(key, dict):
            keystr = self._dict_to_key(key)
        elif isinstance(key, str):
            keystr = key
            key = self._key_to_dict(key)
        else:
            raise KeyError

        try:
            for itm in self._dict:
                return self._dict[keystr]
        except KeyError:
            key['cmd2'] = None
            keystr = self._dict_to_key(key)
            try:
                for itm in self._dict:
                    return self._dict[keystr]
            except:
                key['cmd1'] = None
                keystr = self._dict_to_key(key)
                try:
                    for itm in self._dict:
                        return self._dict[keystr]
                except:
                    key['acknak'] = None
                    keystr = self._dict_to_key(key)
                    try:
                        for itm in self._dict:
                            return self._dict[keystr]
                    except:
                        return None
        raise KeyError

    def __setitem__(self, key, value):
        keystr = self._dict_to_key(key)
        self._dict[keystr] = value

    def add_message_callback(self, code, commandtuple, callback, acknak=None):
        key = {'code':code}
        if isinstance(commandtuple, dict):
            key.update(commandtuple)
        key.update({'acknak':acknak})
        self[key] = callback

    def get_callback_from_message(self, msg):
        key = {'code': msg.code}
        cmd1 = None
        cmd2 = None
        acknak = None
        if hasattr(msg, 'cmd1'):
            cmd1 = msg.cmd1
            cmd2 = msg.cmd2
        if msg.isack:
            acknak = MESSAGE_ACK
        elif msg.isnak:
            acknak = MESSAGE_NAK
        key.update({'cmd1':cmd1, 'cmd2':cmd2, 'acknak':acknak})
        return self[key]

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
