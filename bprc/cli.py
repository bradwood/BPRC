"""
This module takes care of capturing the cli options
"""

import argparse

parser = argparse.ArgumentParser(description='Batch Processing RESTful Client')

#TODO add version argument -- see https://pymotw.com/2/argparse/
parser.add_argument('--version', action='version', version='%(prog)s 2.0',
                    help='shows version number and exits') ##TODO: fix/check

parser.add_argument(dest='yamlfile', nargs=1, help="YAML recipe file")

parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='verbose mode', default=False)

parser.add_argument('-d', '--dry-run', dest='dryrun', action='store_true',default=False,
                    help='parses and outputs recipe without making any calls')

parser.add_argument('--ignore-ssl', dest='ignoressl', action='store_true',default=False,
                    help='do not validate ssl certificates')

#DONE
parser.add_argument('--debug', dest='debug', action='store_true',default=False,
                    help='turns on stacktrace dumps on errors')

parser.add_argument('-q','--quiet', dest='quiet', action='store_true',default=False,
                    help='supresses all console output')

parser.add_argument('--skip-http-errors', dest='skiphttperrors', action='store_true',default=False,
                    help='does not exit when HTTP 4xx or 5xx is returned')

parser.add_argument('--log-level', dest='loglevel', action='store',default='none',
                    choices={'none','critical','error','warning','info','debug'},
                    help='sets logging level, defaults to none.')

parser.add_argument('--log-file', dest='logfile', action='store', metavar='logfile',
                    help='specifies logfile, defaults to STDOUT')


#TODO: output files /formats

args = parser.parse_args()
