#!/usr/bin/env python3
"""
Simple script that:
- reads the current version number
- using an argument, bumps it
- does a git tag and a git commit
"""

import semver
import argparse
import sys
from bprc._version import __version__
import re

parser = argparse.ArgumentParser(description='Version bumper')

parser.add_argument('-b','--bump', dest='bump', action='store',
                    choices={'major','minor','patch'}, default='patch',
                    help='defaults to %(default)s')

args = parser.parse_args()

verfile='bprc/_version.py'

if args.bump == 'major':
    newver=semver.bump_major(__version__)

if args.bump == 'minor':
    newver=semver.bump_minor(__version__)

if args.bump == 'patch':
    newver=semver.bump_patch(__version__)

print('New version is ' + newver)

newverfile = open(verfile, 'w')
newverfile.write('__version__ = "'+ newver +'"' +"\n")
newverfile.close()

from subprocess import call
call(["git", "add",verfile])

