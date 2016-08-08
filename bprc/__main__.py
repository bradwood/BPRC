#!/usr/bin/env python
"""The main entry point. Invoke as `bprc' or `python3 -m bprc'."""
import sys
import os


# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from bprc.core import main


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
