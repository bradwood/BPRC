"""
This module implements the logic to process a step in a recipe
"""
import logging
import json
import requests
import re
from functools import partial
import utils
from utils import vlog,errlog,verboseprint, generateQueryString
from urllib.parse import urlencode

class StepProcessor():
    """Class to process """

    def __init__(self, *, recipe,stepid): #kwargs for recipe and stepid
        """Instantiates the Step Processor Object"""
        self.recipe = recipe
        self.stepid = stepid

    def prepare(self):
        """prepares the step by substituting php-like constructs in the step subtree of the passed recipe"""
        vlog("Step parser initialised for step " + str(self.stepid))
        subpat=re.compile(r'<%=(\S+?)%>') #substitution pattern to find - of the form <%=some.var["blah"]%>

        def _insert_param(m, recipe):
            """
            used by the re.subn call below
            takes an re.match object
            returns a string
            """
            #TODO: add try catches on RE replace.
            vlog("Found php-like pattern: <$=" +m.group(1) + "%>... substituting with " +eval('recipe.' + m.group(1)))
            logging.debug('In StepProcessor.prepare()._insert_param: m.group(1)=%s',m.group(1))
            logging.debug('In StepProcessor.prepare()._insert_param: recipe.steps[0].response.body["id"]=%s',recipe.steps[0].response.body["id"])

            return eval('recipe.' + m.group(1))

        if self.stepid == 0:
            vlog("Stepid=" + str(self.stepid) + " - nothing to parse, skipping step") #TODO: change handing of step 0.
            return self.recipe.steps[self.stepid] # nothing to process if we are on the first step TODO: maybe do some step validation later?
        else:
            # Algorithm:

            # process substitutions in URL string
            vlog("URL: Commencing pattern match for php-like pattern...")
            u=self.recipe.steps[self.stepid].URL
            substituted_text, n = subpat.subn(partial(_insert_param, recipe=self.recipe), u)
            vlog("URL: Made " +str(n)+ " substitutions. Result: URL="+ substituted_text)
            self.recipe.steps[self.stepid].URL=substituted_text

            # loop through all QueryString dictionaries and process substition
            vlog("QueryString: Commencing pattern match for php-like pattern over all parameters...")

            for key in self.recipe.steps[self.stepid].request.querystring:
                vlog("QueryString: " + key + " found: Commencing pattern match for php-like pattern...")

                qs=self.recipe.steps[self.stepid].request.querystring[key]
                substituted_text, n = subpat.subn(partial(_insert_param, recipe=self.recipe), qs)
                vlog("QueryString: Made " +str(n)+ " substitutions. Result: " + key + "=" + substituted_text)
                self.recipe.steps[self.stepid].request.querystring[key]=substituted_text

            vlog("QueryString: now looks like " + urlencode(self.recipe.steps[self.stepid].request.querystring))

            # loop through all Request.body dictionaries and process substitutions
            vlog("Body: Commencing pattern match for php-like pattern over all parameters...")
            for key in self.recipe.steps[self.stepid].request.body:
                vlog("Body: " + key + " found: Commencing pattern match for php-like pattern...")
                bod=self.recipe.steps[self.stepid].request.body[key]
                substituted_text, n = subpat.subn(partial(_insert_param, recipe=self.recipe), bod)
                vlog("Body: Made " +str(n)+ " substitutions. Result: " + key + "=" + substituted_text)
                self.recipe.steps[self.stepid].request.body[key]=substituted_text

            # TODO: fix vlog("Body: now looks like " + urlencode(self.recipe.steps[self.stepid].request.body))

            # loop through all Request.header dictionaries and process substitutions
            vlog("Header: Commencing pattern match for php-like pattern over all parameters...")
            for key in self.recipe.steps[self.stepid].request.headers:
                vlog("Header: " + key + " found: Commencing pattern match for php-like pattern...")
                heads=self.recipe.steps[self.stepid].request.headers[key]
                substituted_text, n = subpat.subn(partial(_insert_param, recipe=self.recipe), heads)
                vlog("Header: Made " +str(n)+ " substitutions. Result: " + key + "=" + substituted_text)
                self.recipe.steps[self.stepid].request.headers[key]=substituted_text

            # TODO: fix vlog("Header: Headers now look like " + urlencode(self.recipe.steps[self.stepid].request.headers))

        return self.recipe.steps[self.stepid]

    def call(self):
        """calls the URL specified in the current step"""
        pass

