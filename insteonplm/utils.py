"""Utility methods."""


from insteonplm.constants import HC_LOOKUP, UC_LOOKUP

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