"""
This module takes care of capturing the cli options
"""


import os
import sys
# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


import argparse
import sys
import logging
from bprc._version import __version__ as __version__

parser = argparse.ArgumentParser(description='Batch Processing RESTful Client')

outputgroup=parser.add_argument_group(title="I/O arguments")
logtestgroup=parser.add_argument_group(title="Logging, testing and debugging arguments")
protocolgroup=parser.add_argument_group(title="Protocol arguments")

parser.add_argument('--version', action='version', version='{} {}'.format(sys.argv[0],__version__),
                    help='shows version number and exits')

parser.add_argument('yamlfile', nargs='?', help="YAML recipe file, defaults to stdin",
                    type=argparse.FileType('r'), default=sys.stdin)

parser.add_argument('outputfile', nargs='?', help=argparse.SUPPRESS, #help='specifies output file, defaults to stdout', turned off for now.
                    type=argparse.FileType('w'), default=sys.stdout)

outputgroup.add_argument('--output-format', dest='outputformat', action='store',
                    choices={'raw-all','raw-response','json'}, default='raw-all',
                    help='specifies output format, defaults to %(default)s')

outputgroup.add_argument('--no-color', dest='nocolor', action='store_true', default=False,
                    help='turns off pretty printing for console output')

logtestgroup.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='verbose mode', default=False)

#TODO implement dry run
# logtestgroup.add_argument('-d', '--dry-run', dest='dryrun', action='store_true',default=False,
#                     help='does everything except actually making any HTTP calls')

logtestgroup.add_argument('--debug', dest='debug', action='store_true',default=False,
                    help='turns on stacktrace dumps for exceptions')

logtestgroup.add_argument('--log-level', dest='loglevel', action='store',default='none',
                    choices={'none','critical','error','warning','info','debug'},
                    help='sets logging level, defaults to %(default)s')

logtestgroup.add_argument('--log-file', dest='logfile', action='store', metavar='logfile',
                    default='bprc.log', help='specifies logfile, defaults to %(default)s')

protocolgroup.add_argument('--skip-http-errors', dest='skiphttperrors', action='store_true',default=False,
                    help='moves to the next step if an HTTP 4xx or 5xx response code is returned')

protocolgroup.add_argument('--ignore-ssl', dest='ignoressl', action='store_true',default=False,
                    help='do not validate ssl certificates')

args = parser.parse_args()


