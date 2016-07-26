"""This module provides the main functionality of bprc.
Invocation flow:
  1. Read, validate and process the input (args, `stdin`).
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
from recipe import Recipe
import logging

def main():
    """
    The main function.
    Pre-process args
    and run the main program with error handling.
    Return exit status code.
    """
    #configure login
    #TODO: generalise this and make logging better
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Initialising log')

    with open("examples/recipe.yml") as stream:
        try:
            datamap = yaml.safe_load(stream)
        except Exception as e:
            raise RuntimeError("An error occured parsing the yaml input file") from None
            print("Reason:", e)

    r = Recipe(datamap)

    logging.debug(r.steps[0].request.headers["Authorisation"])
    logging.debug(r.steps[1].request.headers["blah"])
    logging.debug(r.steps[0].response.body["id"])
    logging.debug(r.steps[1].response.headers["Authorisation"])



    print("\n\n")
    print(r)

