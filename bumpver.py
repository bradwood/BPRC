#!/usr/bin/env python3
"""
Simple script that:
- reads the current version number
- using an argument, bumps it
- does a git tag and a git commit
"""
#TODO: @RELEASE @NTH (99) - consider using git shortlog 0.6.2..0.6.3 to generate release notes.
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

# check if there are any unstaged changes. if there are, then exit
from subprocess import call, run, PIPE
result=run('expr $(git status --porcelain 2>/dev/null| egrep "^(M| M)" | wc -l)',
            shell=True, universal_newlines=True, stdout=PIPE)

if int(result.stdout) > 0:
    print("There are unstaged changes. Please fix, and re-run.")
    sys.exit(1)

print('Git status is clean. Incrementing version number in' + verfile)
print('New version is ' + newver)
newverfile = open(verfile, 'w')
newverfile.write('__version__ = "'+ newver +'"' +"\n")
newverfile.close()
call(["git", "add", verfile])
call(["git", "commit", "-m", "Version bump to " + newver])
call(["git", "tag", newver ,"-m", "Version bump to " + newver])






