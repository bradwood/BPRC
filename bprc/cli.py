"""
This module takes care of capturing the cli options
"""

import argparse

#TODO add version argument -- see https://pymotw.com/2/argparse/
#TODO add quiet option
#TODO add logging/output option
parser = argparse.ArgumentParser(description='Executes a batch of RESTful JSON calls with with variable substitution')

parser.add_argument(dest='yamlfile', nargs=1, help="YAML recipe file")

parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='verbose mode')

parser.add_argument('-d', '--dry-run', dest='dryrun', action='store_true',
                    help='outputs recipe without making any calls')

args = parser.parse_args()
