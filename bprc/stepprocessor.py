"""
This module implements the logic to process a step in a recipe
"""
import logging
import json
import requests
import re
from functools import partial

class StepProcessor():
    """Class to process """

    def __init__(self, *, recipe,stepid): #kwargs for recipe and stepid
        """Instantiates the Step Processor Object"""
        self.recipe = recipe
        self.stepid = stepid

    def prepare(self):
        """prepares the step by substituting php-like constructs in the step subtree of the passed recipe"""
        logging.debug('In StepProcessor.prepare(): stepid=%s',self.stepid)

        subpat=re.compile(r'<%=(\S+?)%>') #substitution pattern to find - of the form <%=some.var["blah"]%>

        def _insert_param(m, recipe):
            """
            used by the re.subn call below
            takes an re.match object
            returns a string
            """
            logging.debug('In StepProcessor.prepare()._insert_param: m.group(1)=%s',m.group(1))
            logging.debug('In StepProcessor.prepare()._insert_param: recipe.steps[0].response.body["id"]=%s',recipe.steps[0].response.body["id"])

            return eval('recipe.' + m.group(1))

        if self.stepid == 0:
            return self.recipe.steps[self.stepid] # nothing to process if we are on the first step TODO: maybe do some step validation later?
        else:
            # Algorithm:
            # process substitutions in URL string
            u=self.recipe.steps[self.stepid].URL

            substituted_text, n = subpat.subn(partial(_insert_param, recipe=self.recipe), u)
            #TODO: Log the above
            self.recipe.steps[self.stepid].URL=substituted_text
            logging.debug('In StepProcessor.prepare(): substituted_text=%s',substituted_text)
            # loop through all QueryString dictionaries and process substition
            for key in self.recipe.steps[self.stepid].request.querystring:
                qs=self.recipe.steps[self.stepid].request.querystring[key]
                substituted_text, n = subpat.subn(partial(_insert_param, recipe=self.recipe), qs)
                #TODO: Log the above
                self.recipe.steps[self.stepid].request.querystring[key]=substituted_text




            # loop through all Request.body dictionaries and process substitutions
            # loop throuhg all Request.header dictionaries and process substitutions

        return self.recipe.steps[self.stepid]

    def call(self):
        """calls the URL specified in the current step"""
        pass

