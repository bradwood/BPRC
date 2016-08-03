"""
This module implements all the class types required to variables in the YAML in memory.
"""

import os
import sys
from itertools import chain

# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


import logging
import collections
from bprc.utils import vlog,errlog,verboseprint

class Variables(collections.MutableMapping): #Make this class behave and look like a dict
    """A collection of general purpose variables that can be substituted in throughout the recipe"""

    def __init__(self, variables):
        self._variables = variables

    def __getitem__(self, key):
        return self._variables[key]

    def __setitem__(self, key, value):
        self._variables[key] = value

    def __delitem__(self, key):
        del self._variables[key]

    def __iter__(self):
        return iter(self._variables)

    def __len__(self):
        return len(self._variables)

