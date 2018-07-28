"""Utility methods."""


from insteonplm.constants import (HC_LOOKUP,
                                  UC_LOOKUP,
                                  X10_COMMAND_ALL_UNITS_OFF,
                                  X10_COMMAND_ALL_LIGHTS_ON,
                                  X10_COMMAND_ALL_LIGHTS_OFF,
                                  X10CommandType)


def housecode_to_byte(housecode):
    return HC_LOOKUP.get(housecode.lower())


def unitcode_to_byte(unitcode):
    return UC_LOOKUP.get(unitcode)


def byte_to_housecode(bytecode):
    rev_hc = dict([reversed(i) for i in HC_LOOKUP.items()])
    return rev_hc.get(bytecode).upper()


def byte_to_unitcode(bytecode):
    rev_dc = dict([reversed(i) for i in UC_LOOKUP.items()])
    return rev_dc.get(bytecode)


def x10_command_type(command):
    command_type = X10CommandType.DIRECT
    if command in [X10_COMMAND_ALL_UNITS_OFF,
                   X10_COMMAND_ALL_LIGHTS_ON,
                   X10_COMMAND_ALL_LIGHTS_OFF]:
        command_type = X10CommandType.BROADCAST
    return command_type


def rawX10_to_bytes(rawX10):
    yield rawX10 >> 4
    yield rawX10 & 0x0f
