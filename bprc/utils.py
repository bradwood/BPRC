"""
Misc utils and setup calls.
"""
import sys
import cli
import logging
import json

#TODO: add docstrings to all these functions

#Turns on stack-traces if debug is passed
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if cli.args.debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print("{}: {}".format(exception_type.__name__, exception))

sys.excepthook = exceptionHandler

# set up logging
logleveldict = {'none': 100, #Hack, as will only log stuff >= 100, critical=50
                'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL
                }

logging.basicConfig(
    level=logleveldict[cli.args.loglevel],
    filename=cli.args.logfile,
    format='%(levelname)s:%(asctime)s: %(message)s')


logging.info('----------------Initialising log----------------')

#sets up a print function for the --verbose argument
verboseprint = print if cli.args.verbose else lambda *a, **k: None

# helper function to call both verboseprint and logging.info
def vlog(msg):
    verboseprint(msg)
    logging.info(msg)

#helper function to call logging.error and raise a RunTime error
def errlog(msg, e):
    logging.error(msg)
    raise RuntimeError(msg) from e

#helper function to serialise a an object so json.dumps will accept it.
def serialiseBody(obj):
    #d=dict()
    #d.update(vars(obj))
    d=vars(obj)
    return d
