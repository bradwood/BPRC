"""
This module implements the logic to process a step in a recipe
"""
import logging
import json
import requests
import re
from functools import partial
import utils
from recipe import Body
from utils import vlog,errlog,verboseprint,serialiseBody
from urllib.parse import urlencode



class BodyEncoder(json.JSONEncoder):
    """ encodes a request body"""
    def default(self,body):
        logging.debug("inside JSON BodyEncoder.default()")
        if isinstance(body,Body):
            return body._body


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
            try:
                vlog("Found php-like pattern: <$=" +m.group(1) + "%>... substituting with " +eval('recipe.' + m.group(1)))
            except KeyError as ke:
                errlog("Could not find "+ m.group(1)+" in the rest of the recipe. Aborting.", ke)

            logging.debug('In StepProcessor.prepare()._insert_param: m.group(1)=%s',m.group(1))

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
        # set up parameters
        name = self.recipe.steps[self.stepid].name
        httpmethod = self.recipe.steps[self.stepid].httpmethod
        url = self.recipe.steps[self.stepid].URL
        #request
        querystring = self.recipe.steps[self.stepid].request.querystring
        requestheaders = self.recipe.steps[self.stepid].request.headers
        requestbody = self.recipe.steps[self.stepid].request.body
        #response
        responsecode = self.recipe.steps[self.stepid].response.code
        responseheaders = self.recipe.steps[self.stepid].response.headers
        responsebody = self.recipe.steps[self.stepid].response.body

        #make the call
        #TODO: wrap in a try to catch bad methods, dodgy URLS, timeouts, etc, etc
        #TODO: enhancement, take file data and form data. "@ parameter"
        #TODO: SSL
        vlog("About to make HTTP request for step " + str(self.stepid) + " " + str(self.recipe.steps[self.stepid].name))
        vlog(httpmethod.upper() + " " + self.recipe.steps[self.stepid].URL)
        r = eval('requests.'+httpmethod.lower()+'(url, params=querystring, headers=requestheaders, data=json.dumps(requestbody, cls=BodyEncoder))')
        #set the response code
        self.recipe.steps[self.stepid].response.code=r.status_code

        #TODO: implement break on error code cli flag here.
        vlog("Received HTTP response code: " + str(self.recipe.steps[self.stepid].response.code))

        #now grab the headers and load them into the response.headers
        self.recipe.steps[self.stepid].response.headers=r.headers

        #now parse the json response and load it into the response.body
        #TODO: try: on this to catch dodgy/missing json.
        self.recipe.steps[self.stepid].response.body=json.loads(r.text)
        logging.debug(r.text)




