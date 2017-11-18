"""Helper objects for maintaining PLM state and interfaces."""
import logging
import binascii

class PLMCode(object):
    """Class to store PLM code definitions and attributes."""

    def __init__(self, code, name=None, size=None, returnsize=None):
        """Create a new PLM code object."""
        self.code = code
        self.size = size
        self.returnsize = returnsize
        self.name = name
