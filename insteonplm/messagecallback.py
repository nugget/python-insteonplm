"""Message callback handler to identify message pattern alignment to inbound messages."""

import logging
#from .constants import *
#from insteonplm.messages.messageBase import MessageBase
#from insteonplm.messages.messageFlags import MessageFlags

class MessageCallback(object):
    """Message callback handler to identify message pattern alignment to inbound messages."""
    def __init__(self):
        """Initialize the MessageCallback class."""
        self._dict = {}
        self.log = logging.getLogger(__name__)

    def __len__(self):
        """Return the number of callbacks in the list."""
        return len(self._dict)

    def __iter__(self):
        """Iterate through the callback list."""
        for itm in self._dict:
            yield itm

    def __getitem__(self, key):
        """Gets an item from the callback list.

        Accepts a string in the format of 'code:cmd1:cmd2:acknak.
        For example, '50:11:None:None' would mean
        a Standard Message (0x50) Light On (0x11) command with any On Level and
        any Ack/Nak value.

        If a direct match is not found the following order is used:
            1) Any cmd2 value
            2) Any cmd1 value
            3) Any Ack/Nak value
        For example, if the key is {'code':0x50, 'cmd1':None, 'cmd2': None, 'acknak':None}
        (i.e. any Standard Message (0x50)) and the message is
        {'code':0x50, 'cmd1': 0x11, 'cmd2:0xff, 'acknak':None}
        this will be a match.
        """
        return self._dict.get(key, [])

    def __setitem__(self, key, value):
        """Set a callback method where the key is a pattern and the value is a callback method."""
        callbacks = self._dict.get(key, [])
        if isinstance(value, list):
            for callback in value:
                callbacks.append(callback)
        else:
            callbacks.append(value)
        self._dict[key] = callbacks

    def add(self, msg, callback, override=False):
        """Add a callback to the callback list.

        msg: Message template.
        callback: Callback method
        override: True - replace all existing callbacks for that message template
                  False - append the callback to the list of callbacks for that message
                  Default is False
        """
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
        """Remove a callback from the callback list.

        msg: Message template
        callback: Callback method to remove.
                  If callback is None, all callbacks for the message template are removed.
        """
        if callback is None:
            self._dict.pop(msg, None)
        else:
            cb = self._dict.get(msg, [])
            try:
                cb.remove(callback)
            except ValueError:
                pass
            if cb:
                self.log.debug('%d callbacks for message: %s', len(cb), msg)
                self.add(msg, cb, True)
            else:
                self._dict.pop(msg, None)
                self.log.debug('Removed all callbacks for message: %s', msg)

    def get_callbacks_from_message(self, msg):
        """Return the callbacks associated with a message template."""
        callbacks = []
        for key in self._find_matching_keys(msg):
            for callback in self[key]:
                callbacks.append(callback)
        return callbacks

    def _find_matching_keys(self, msg):
        for key in self._dict:
            if key.matches_pattern(msg) and msg.matches_pattern(key):
                yield key
