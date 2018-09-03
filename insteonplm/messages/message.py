"""INSTEON Message Class Module."""
import logging
import binascii
from insteonplm.address import Address
from insteonplm.constants import MESSAGE_START_CODE_0X02
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.userdata import Userdata

_LOGGER = logging.getLogger(__name__)


class ClassPropertyMetaClass(type):
    """Meta class for Message class.

    This is meta class magic to allow class attributes to also appear as an
    instance property.
    """

    @property
    def code(cls):
        """Message code used to determine message type."""
        return cls._code

    @property
    def sendSize(cls):
        """Size of the message sent in bytes."""
        return cls._sendSize

    @property
    def receivedSize(cls):
        """Size of the message received in bytes."""
        return cls._receivedSize

    @property
    def description(cls):
        """Return a description of the message type."""
        return cls._description


class Message(metaclass=ClassPropertyMetaClass):
    """Base message class for an INSTEON message."""

    _code = 0
    _sendSize = 0
    _receivedSize = 0
    _description = "Empty message"

    def __str__(self):
        """Return a string representation of an INSTEON message."""
        props = self._message_properties()
        msgstr = "{}'code': 0x{}".format(
            "{", binascii.hexlify(bytes([self._code])).decode())
        for prop in props:
            for key, val in prop.items():
                msgstr = msgstr + ', '
                if isinstance(val, Address):
                    msgstr = "{}'{}': {}".format(msgstr, key, val.human)
                elif isinstance(val, MessageFlags):
                    msgstr = "{}'{}': 0x{}".format(msgstr, key, val.hex)
                elif isinstance(val, int):
                    msgstr = "{}'{}': 0x{}".format(
                        msgstr, key, binascii.hexlify(bytes([val])).decode())
                elif isinstance(val, bytearray):
                    msgstr = "{}'{}': 0x{}".format(
                        msgstr, key, binascii.hexlify(val).decode())
                elif isinstance(val, bytes):
                    msgstr = "{}'{}': 0x{}".format(
                        msgstr, key, binascii.hexlify(val).decode())
                else:
                    msgstr = "{}'{}': 0x{}".format(msgstr, key, str(val))
        msgstr = "{}{}".format(msgstr, '}')
        return msgstr

    def __eq__(self, other):
        """Test for equality."""
        match = False
        if isinstance(other, Message) and other.code == self._code:
            match = str(self) == str(other)
        return match

    def __ne__(self, other):
        """Test for inequality."""
        match = True
        if isinstance(other, Message) and other.code == self._code:
            match = str(self) != str(other)
        return match

    def __lt__(self, other):
        """Test for less than."""
        less_than = False
        if isinstance(other, Message):
            less_than = str(self) < str(other)
        else:
            raise TypeError
        return less_than

    def __gt__(self, other):
        """Test for greater than."""
        greater_than = False
        if isinstance(other, Message):
            greater_than = str(self) > str(other)
        else:
            raise TypeError
        return greater_than

    def __hash__(self):
        """Create a has of the message."""
        return hash(str(self))

    @property
    def code(self):
        """Messasge code used to determine message type."""
        return self._code

    @property
    def sendSize(self):
        """Size of the sent messsage in bytes."""
        return self._sendSize

    @property
    def receivedSize(self):
        """Size of the received message in bytes."""
        return self._receivedSize

    @property
    def description(self):
        """Return the description of the message type."""
        return self._description

    @property
    def hex(self):
        """Hexideciaml representation of the message in bytes."""
        props = self._message_properties()
        msg = bytearray([MESSAGE_START_CODE_0X02, self._code])

        for prop in props:
            # pylint: disable=unused-variable
            for key, val in prop.items():
                if val is None:
                    pass
                elif isinstance(val, int):
                    msg.append(val)
                elif isinstance(val, Address):
                    if val.addr is None:
                        pass
                    else:
                        msg.extend(val.bytes)
                elif isinstance(val, MessageFlags):
                    msg.extend(val.bytes)
                elif isinstance(val, bytearray):
                    msg.extend(val)
                elif isinstance(val, bytes):
                    msg.extend(val)
                elif isinstance(val, Userdata):
                    msg.extend(val.bytes)

        return binascii.hexlify(msg).decode()

    @property
    def bytes(self):
        """Return the bytes representation of the message."""
        return binascii.unhexlify(self.hex)

    def matches_pattern(self, other):
        """Return if the current message matches a message template.

        Compare the current message to a template message to test matches
        to a pattern.
        """
        properties = self._message_properties()
        ismatch = False
        if isinstance(other, Message) and self.code == other.code:
            for prop in properties:
                for key, prop_val in prop.items():
                    if hasattr(other, key):
                        key_val = getattr(other, key)
                        ismatch = self._test_match(prop_val, key_val)
                    else:
                        ismatch = False
                    if not ismatch:
                        break
                if not ismatch:
                    break
        return ismatch

    @staticmethod
    def _setacknak(acknak):
        _acknak = acknak
        if isinstance(acknak, bytearray) and acknak:
            _acknak = acknak[0]
        return _acknak

    def _message_properties(self):
        raise NotImplementedError

    @staticmethod
    def _test_match(prop_val, key_val):
        ismatch = False
        if isinstance(prop_val, MessageFlags):
            ismatch = prop_val.matches_pattern(key_val)
        elif isinstance(prop_val, Address):
            ismatch = prop_val.matches_pattern(key_val)
        elif isinstance(prop_val, Userdata):
            ismatch = prop_val.matches_pattern(key_val)
        else:
            if prop_val is None or key_val is None:
                ismatch = True
            else:
                ismatch = prop_val == key_val
        return ismatch
