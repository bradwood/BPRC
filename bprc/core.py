"""This module provides the main functionality of bprc.
Invocation flow:
  - Read, validate and process the input (args).
  - Parse the YAML file.
  - Create a Variables object from the yaml file.
    - Parse it and create the Variables object
  - Create the Recipe object from the yaml file.
    - Validate the Recipe Opbject
  - Iterate over the Recipe object
    - Invoke each step by:
      - Substiting any response, variable or file data into the current step
      - Executing the call
      - Updating all response objects
      - Writing the output
  - Exit.

"""

import os
import sys
# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import select
import yaml
import bprc.utils
from bprc.utils import vlog,errlog,verboseprint, logleveldict
import logging
import bprc.cli
from bprc.recipe import Recipe
from bprc.variables import Variables
from bprc.stepprocessor import StepProcessor
from bprc.varprocessor import VarProcessor



def main():
    """
    The main function.
    Pre-process args
    and run the main program with error handling.
    Return exit status code.
    """
    # Hack to make the program exit if neither stdin, nor a file param is passed.
    if bprc.cli.args.yamlfile == sys.stdin and not select.select([sys.stdin,],[],[],0.0)[0]:
        bprc.cli.parser.print_usage()
        bprc.cli.parser.exit(status=1)

    # set up the log file
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
        sys.exit(1)
    vlog("Yaml file parsed ok...")

    vlog("Instantiating variables object...")
    try:
        variables = Variables(datamap["variables"])
    except Exception as e:
        vlog("No variable object in YAML file")
        variables = Variables({})
    vlog("Variables object instantiated ok... (albeit maybe empty)")

    try:
        vlog("Instantiating recipe object...")
        r = Recipe(datamap)
        vlog("Recipe object instantiated ok...")
        vlog('Recipe-'+ str(r))
    except Exception as e:
        errlog("Could not create Recipe Object.",e)
        sys.exit(2)

    #parse variables
    vlog("Commencing variable parsing and substitution...")
    varprocessor = VarProcessor(variables)
    #do recursive variable substitution.
    for varname, varval in variables.items():
        vlog("Commencing variable substitutions for variable " + str(varname) + "=" + str(varval))
        variables[varname] = varprocessor.parse(varval, variables)
        vlog("Substituted " + str(varname) + "=" + str(variables[varname]))

    # now subsitute filenames -- note, I tried this in the above loop but go errors.
    # probably safer to parse *all* varnames before trying with files anyway.
    for varname, varval in variables.items():
        vlog("Commencing filename-- substitutions for variable " + str(varname) + "=" + str(varval))
        variables[varname] = varprocessor.fileparse(varval, variables)
        vlog("Substituted filespec " + str(varname) + "=" + str(variables[varname]))

    #loop through steps and execute each one.
    vlog("Commencing processing loop...")
    for i, step in enumerate(r.steps):
        # firstly, for the step about to be executed, substitute any items in the request object using the php-like
        # <%= =>
        vlog("Commencing php-like substitutions for step " + str(i) + ":" + r.steps[i].name)
        processor = StepProcessor(recipe=r, stepid=i, variables=variables) # instantiate a step processor
        r.steps[i] = processor.prepare() # substitutes recipe strings to prepare the step for calling.
        vlog("Php-like substitutions complete for step " + str(i) + ":" + r.steps[i].name)
        p_statement=processor.call() # makes the call and populates the response object.
        processor.generateOutput(p_statement) #writes the output for this step.
    sys.exit(0)

