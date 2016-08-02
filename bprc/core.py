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
        3.1.4. Write output file
  4. Exit.

"""

import os
import sys
# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


import yaml
import bprc.utils
from bprc.utils import vlog,errlog,verboseprint, logleveldict
import logging
import bprc.cli
from bprc.recipe import Recipe
from bprc.stepprocessor import StepProcessor



def main():
    """
    The main function.
    Pre-process args
    and run the main program with error handling.
    Return exit status code.
    """

    if bprc.cli.args.loglevel == 'none':
        logging.basicConfig(
        level=logleveldict[bprc.cli.args.loglevel],
        format='%(levelname)s:%(asctime)s: %(message)s',
        handlers=[logging.NullHandler()]) # set up with a NullHandler
    else:
        logging.basicConfig(
        level=logleveldict[bprc.cli.args.loglevel],
        filename=bprc.cli.args.logfile,
        format='%(levelname)s:%(asctime)s: %(message)s') #Use the standard FileHandler


    logging.info('----------------Initialising log----------------')

    #try to read in the file.

    try:
        vlog("Loading yaml input...")
        datamap = yaml.safe_load(bprc.cli.args.yamlfile)
    except Exception as e:
        errlog("An error occured parsing the yaml input file", e)
    vlog("Yaml file parsed ok...")

    vlog("Instantiating recipe object...")
    r = Recipe(datamap)
    vlog("Recipe object instantiated ok...")

    vlog('Recipe-'+ str(r))

    #loop through steps and execute each one.
    vlog("Commencing processing loop...")
    for i, step in enumerate(r.steps):
        # firstly, for the step about to be executed, substitute any items in the request object using the php-like
        # <%= =>
        vlog("Commencing php-like substitutions for step " + str(i) + ":" + r.steps[i].name)
        #TODO: add try:'s around all the below calls.
        processor = StepProcessor(recipe=r, stepid=i) # instantiate a step processor
        r.steps[i] = processor.prepare() # substitutes and php-like strings to prepare the step for calling & returns
        vlog("Php-like substitutions complete for step " + str(i) + ":" + r.steps[i].name)
        processor.call() # makes the call and populates the response object.
        processor.generateOutput() #writes the output for this step.

