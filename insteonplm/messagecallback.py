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
        return self._dict.get(key, [])

    def __setitem__(self, key, value):
        callbacks = self._dict.get(key, [])
        if isinstance(value, list):
            for callback in value:
                callbacks.append(callback)
        else:
            callbacks.append(value)
        self._dict[key] = callbacks

    def add(self, msg, callback, override=False):
        if override:
            if isinstance(callback, list):
                self._dict[msg] = callback
            else:
                self._dict[msg] = [callback]
        else:
            cb = self[msg]
            cb.append(callback)
            #self.log.debug('%d total callbacks for template: %s', len(cb), str(msg))
            self._dict[msg] = cb

    def remove(self, msg, callback):
        if callback is None:
            removed = self._dict.pop(msg, None)
        else:
            cb = self._dict.get(msg, None)
            if cb is not None:
                try:
                    cb.remove(callback)
                except:
                    pass
            if len(cb) == 0:
                removed = self._dict.pop(msg, None)
                self.log.debug('Removed all callbacks for message: %s', msg)
            else:
                self.log.debug('%d callbacks for message: %s', len(cb), msg)
                self.add(msg, cb, True)

    def get_callbacks_from_message(self, msg):
        callbacks = []
        for key in self._find_matching_keys(msg):
            for callback in self[key]:
                callbacks.append(callback)
        return callbacks

    def _find_matching_keys(self, msg):
        for key in self._dict:
            print('Key ', key)
            print('Msg ', msg)
            if key.matches_pattern(msg) and msg.matches_pattern(key):
                print('Matches')
                yield key

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


