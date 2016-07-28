"""This module provides the main functionality of bprc.
Invocation flow:
  1. Read, validate and process the input (args).
  2. Create the Recipe object.
    2.1. Validate the Recipe Opbject
  3. Iterate over the Recipe object
    3.1. Invoke each Ingredient by:
        3.1.1. Substiting any response data into the current Ingredient
        3.1.2. Executing the call
        3.1.3. Updating all response objects
  4. Exit.
"""

import yaml
import logging
from recipe import Recipe
from stepprocessor import StepProcessor
import sys
import cli
import fileinput

#Turns on stack-traces if debug is passed
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if cli.args.debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print("{}: {}".format(exception_type.__name__, exception))

sys.excepthook = exceptionHandler

# set up logging if needed.
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s:%(message)s')
logging.debug('Initialising log')

#TODO: finish this
if cli.args.verbose:
    def verboseprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
           print(arg,)
        print
else:
    verboseprint = lambda *a: None      # do-nothing function

def main():
    """
    The main function.
    Pre-process args
    and run the main program with error handling.
    Return exit status code.
    """
    print(cli.args.verbose)
    print(cli.args.dryrun)

    #try to read in the file.

    try:
        datamap = yaml.safe_load(cli.args.yamlfile)
    except Exception as e:
        raise RuntimeError("An error occured parsing the yaml input file") from None
    logging.debug("Yaml file parsed ok...")
    logging.debug(cli.args.yamlfile)

    r = Recipe(datamap)

    logging.debug('r.steps[0].request.headers["Authorisation"]=%s', r.steps[0].request.headers["Authorisation"])
    logging.debug('r.steps[1].request.headers["blah"]=%s',r.steps[1].request.headers["blah"])
    logging.debug('r.steps[0].response.body["id"]=%s',r.steps[0].response.body["id"])
    logging.debug('r.steps[1].response.headers["Authorisation"]=%s',r.steps[1].response.headers["Authorisation"])

    #loop through steps and execute each one.
    for i, step in enumerate(r.steps):
        logging.debug('In steps loop PREPROCESS: r.steps[%s].URL=%s',i,r.steps[i].URL)
        # firstly, for the step about to be executed, substitute any items in the request object using the php-like
        # <%= =>
        processor = StepProcessor(recipe=r, stepid=i) # instantiate a step processor
        r.steps[i] = processor.prepare() # substitutes and php-like strings to prepare the step for calling & returns
        processor.call() # makes the call and populates the response object.
        logging.debug('In steps loop POSTPROCESS: r.steps[%s].URL=%s',i,r.steps[i].URL)

    print("\n\n")
    print(r)
    logging.debug('Post-loop: r.steps[1].URL=%s',r.steps[1].URL)
    logging.debug('Post-loop: r.steps[1].request.querystring["keysub"]=%s',r.steps[1].request.querystring["keysub"])
    logging.debug('Post-loop: r.steps[1].request.body["key4"]=%s',r.steps[1].request.body["key4"])
    logging.debug('Post-loop: r.steps[1].request.headers["Authorisation"]=%s',r.steps[1].request.headers["Authorisation"])
