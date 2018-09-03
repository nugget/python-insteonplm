"""Utility methods."""


from insteonplm.constants import (HC_LOOKUP,
                                  UC_LOOKUP,
                                  X10_COMMAND_ALL_UNITS_OFF,
                                  X10_COMMAND_ALL_LIGHTS_ON,
                                  X10_COMMAND_ALL_LIGHTS_OFF,
                                  X10CommandType)


def housecode_to_byte(housecode):
    """Return the byte value of an X10 housecode."""
    return HC_LOOKUP.get(housecode.lower())


def unitcode_to_byte(unitcode):
    """Return the byte value of an X10 unitcode."""
    return UC_LOOKUP.get(unitcode)


def byte_to_housecode(bytecode):
    """Return an X10 housecode value from a byte value."""
    hc = list(HC_LOOKUP.keys())[list(HC_LOOKUP.values()).index(bytecode)]
    return hc.upper()


def byte_to_unitcode(bytecode):
    """Return an X10 unitcode value from a byte value."""
    return list(UC_LOOKUP.keys())[list(UC_LOOKUP.values()).index(bytecode)]


def x10_command_type(command):
    """Return the X10 command type from an X10 command."""
    command_type = X10CommandType.DIRECT
    if command in [X10_COMMAND_ALL_UNITS_OFF,
                   X10_COMMAND_ALL_LIGHTS_ON,
                   X10_COMMAND_ALL_LIGHTS_OFF]:
        command_type = X10CommandType.BROADCAST
    return command_type


def rawX10_to_bytes(rawX10):
    """Return the byte value of a raw X10 command."""
    yield rawX10 >> 4
    yield rawX10 & 0x0f


def bit_is_set(bitmask, bit):
    """Return True if a specific bit is set in a bitmask.

    Uses the low bit is 1 and the high bit is 8.
    """
    bitshift = bit - 1
    return bool(bitmask & (1 << bitshift))


def set_bit(bitmask, bit, is_on):
    """Set the value of a bit in a bitmask on or off.

    Uses the low bit is 1 and the high bit is 8.
    """
    bitshift = bit - 1
    if is_on:
        return bitmask | (1 << bitshift)
    return bitmask & (0xff & ~(1 << bitshift))
