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
import utils
from utils import vlog,errlog,verboseprint
import logging
import cli
from recipe import Recipe
from stepprocessor import StepProcessor
import sys



def main():
    """
    The main function.
    Pre-process args
    and run the main program with error handling.
    Return exit status code.
    """
    #try to read in the file.

    try:
        vlog("Loading yaml input...")
        datamap = yaml.safe_load(cli.args.yamlfile)
    except Exception as e:
        errlog("An error occured parsing the yaml input file", e)
    vlog("Yaml file parsed ok...")

    vlog("Instantiating recipe object...")
    r = Recipe(datamap)
    vlog("Recipe object instantiated ok...")


    #loop through steps and execute each one.
    vlog("Commencing processing loop...")
    for i, step in enumerate(r.steps):
        # firstly, for the step about to be executed, substitute any items in the request object using the php-like
        # <%= =>
        vlog("Commencing php-like substitutions for step " + str(i) + ":" + r.steps[i].name)
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
