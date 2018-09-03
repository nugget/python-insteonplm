"""Message callback handler matching message pattern to inbound messages."""

import logging

_LOGGER = logging.getLogger(__name__)


class MessageCallback():
    """Message callback handler.

    Message patterns or templates are used as the key to a message/callback
    tuple. For example, a message with the following attributes:

    {'code': 0x50, 'address': 1A.2B.3C, 'target': None,
    'flags': None, 'cmd1': 0x11, 'cmd2': None}

    Would match any message with:
        code == 0x50
        address == 1A.2B.3C
        target == any value
        flags == any value
        cmd1 == 0x11
        cmd2 == any value

    The above example is an inbound Standard Receive message (0x50)
    with the "Light On" message and any light level value in cmd2.
    """

    def __init__(self):
        """Init the MessageCallback class."""
        self._dict = {}

    def __len__(self):
        """Return the number of callbacks in the list."""
        return len(self._dict)

    def __iter__(self):
        """Iterate through the callback list."""
        for itm in self._dict:
            yield itm

    def __getitem__(self, key):
        """Return an item from the callback list.

        Accepts any message type as a key and returns the callbacks
        associated with that message template.
        """
        return self._dict.get(key, [])

    def __setitem__(self, key, value):
        """Set a callback method to a message key.

        Key: any message template.
        Value: callback method.
        """
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
        override: True - replace all existing callbacks for that template
                  False - append the list of callbacks for that message
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
            self._dict[msg] = cb

    def remove(self, msg, callback):
        """Remove a callback from the callback list.

        msg: Message template
        callback: Callback method to remove.

        If callback is None, all callbacks for the message template are
        removed.
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
                _LOGGER.debug('%d callbacks for message: %s', len(cb), msg)
                self.add(msg, cb, True)
            else:
                self._dict.pop(msg, None)
                _LOGGER.debug('Removed all callbacks for message: %s', msg)

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
