"""
This module takes care of capturing the cli options and setting up the environmental parameters
like logging, etc.
"""

import argparse
import sys
import logging
from _version import __version__

parser = argparse.ArgumentParser(description='Batch Processing RESTful Client')

#TODO:implement ALL cli commands!!!
#TODO:COSMETIC: re-order args and consider groupings for readability. ArgumentParser.add_argument_group(title=None, description=None)

filegroup=parser.add_argument_group(title="I/O arguments")
logtestgroup=parser.add_argument_group(title="Logging, testing and debugging arguments")
protocolgorup=parser.add_argument_group(title="Protocol arguments")


parser.add_argument('--version', action='version', version='{} {}'.format(sys.argv[0],__version__),
                    help='shows version number and exits')
#ABOVE IMPLEMENTED
filegroup.add_argument('-f', '--input-file', dest='yamlfile', metavar='yamlfile', action='store',
                    help="YAML recipe file", type=argparse.FileType('r'), default=sys.stdin)

filegroup.add_argument('--output-file', dest='outfile', action='store', metavar='outfile',
                    help='specifies output file, defaults to ./bprc.out.{pid}')
#TODO: think about output format? yaml, json, CSV, other?


logtestgroup.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='verbose mode', default=False)

logtestgroup.add_argument('-d', '--dry-run', dest='dryrun', action='store_true',default=False,
                    help='does everything except actually making any HTTP calls')

protocolgorup.add_argument('--ignore-ssl', dest='ignoressl', action='store_true',default=False,
                    help='do not validate ssl certificates')

logtestgroup.add_argument('--debug', dest='debug', action='store_true',default=False,
                    help='turns on stacktrace dumps for exceptions')
#ABOVE IMPLEMENTED


protocolgorup.add_argument('--skip-http-errors', dest='skiphttperrors', action='store_true',default=False,
                    help='moves to the next step if an HTTP 4xx or 5xx response code is returned')

logtestgroup.add_argument('--log-level', dest='loglevel', action='store',default='none',
                    choices={'none','critical','error','warning','info','debug'},
                    help='sets logging level, defaults to %(default)s.')

logtestgroup.add_argument('--log-file', dest='logfile', action='store', metavar='logfile',
                    help='specifies logfile, defaults to stderr')


args = parser.parse_args()

## hack for the case when no arguments are passed. without this, it just sits waiting for stdin.
if len(sys.argv) < 2:
    parser.print_usage()
    parser.exit(status=0)

