"""
This module implements the logic to process a step in a recipe
"""

import sys
import os


# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import logging
import json
import requests
import re
from functools import partial
import bprc.utils
from bprc.recipe import Body
from bprc.utils import vlog,errlog,verboseprint, httpstatuscodes
from urllib.parse import urlencode
import bprc.cli
from bprc.outputprocessor import OutputProcessor


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
            try:
                vlog("Found php-like pattern: <$=" +m.group(1) + "%>... substituting with " +eval('recipe.' + m.group(1)))
            except KeyError as ke:
                errlog("Could not find "+ m.group(1)+" in the rest of the recipe. Aborting.", ke)

            logging.debug('In StepProcessor.prepare()._insert_param: m.group(1)=%s',m.group(1))

            return eval('recipe.' + m.group(1))

        if self.stepid == 0:
            vlog("Stepid=" + str(self.stepid) + " - nothing to parse, skipping step") #TODO: change handing of step 0.
            return self.recipe.steps[self.stepid]
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

        #TODO: stuff a few extra request headers if these are not aready present
        # e.g: accepts:
        # content-type? maybe, if requests doesn't do this
        # User agent.

        #make the call
        #TODO: enhancement, take file data and form data. "@ parameter"
        #bprc.cli.args.ignoressl

        vlog("About to make HTTP request for step " + str(self.stepid) + " " + str(self.recipe.steps[self.stepid].name))
        vlog(httpmethod.upper() + " " + self.recipe.steps[self.stepid].URL)
        try:
            r = eval('requests.'+httpmethod.lower()+'(url, params=querystring, headers=requestheaders, verify='+ str(not bprc.cli.args.ignoressl) +', data=json.dumps(requestbody, cls=BodyEncoder))')
        except requests.exceptions.SSLError as ssle:
            errlog("Could not verify SSL certificate. Try the --ignore-ssl option", ssle)
        except requests.exceptions.ConnectionError as httpe:
            errlog("Could not open HTTP connection. Network problem or bad URL?", httpe)
        except AttributeError as ae:
            errlog("Problem with URL or HTTP method", ae)
        #set the response code
        #and if it's 4xx or 5xx exist based on whether --ignore-http-errors were passed or not.
        self.recipe.steps[self.stepid].response.code=r.status_code
        vlog("Received HTTP response code: " + str(self.recipe.steps[self.stepid].response.code))
        if not r.status_code == requests.codes.ok:
            msg="Received an HTTP error code..."
            logging.warning(msg)
            verboseprint(msg)
            if bprc.cli.args.skiphttperrors:
                vlog("--skip-http-errors passed. Ignoring error and proceeding...")
            else:
                try:
                    r.raise_for_status()
                except Exception as e:
                    if bprc.cli.args.debug:
                        print("Response body: " + r.text)
                    errlog("Got error HTTP response. Aborting", e)

        #now grab the headers and load them into the response.headers
        self.recipe.steps[self.stepid].response.headers=r.headers

        #Now load some of the meta data from the response into the step.response
        self.recipe.steps[self.stepid].response.httpversion=r.raw.version
        self.recipe.steps[self.stepid].response.encoding=r.encoding
        self.recipe.steps[self.stepid].response.statusmsg=httpstatuscodes[str(r.status_code)]

        #now parse the json response and load it into the response.body
        response_content_type = r.headers['content-type'].split(';')[0] # grebs the xxx/yyyy bit of the header
        logging.debug(r.text)
        logging.debug("Content-type:" + response_content_type)
        logging.debug("Encoding:" + str(r.encoding))
        logging.debug("Text:" + r.text)

        #now, check if JSON was sent in the response body, if it was, load it, otherwise exit with an error
        if response_content_type.lower() == 'application/json':
            vlog("JSON response expected. Content-type: " + response_content_type)
            try:
                vlog("Attempting to parse JSON response body...")
                self.recipe.steps[self.stepid].response.body=json.loads(r.text)
            except Exception as e:
                errlog("Failed to parse JSON response. Aborting", e)
            vlog("JSON parsed ok.")
        else:
            errlog("Response body is not JSON! Content-type: " +response_content_type+". Aborting", None)

    def generateOutput(self):
        """imvokes the output processor to write the output"""
        #instantiate an OutputProcessor
        output=OutputProcessor(step=self.recipe.steps[self.stepid], id=self.stepid)
        # get cli arguments and pass to the output processor

        output.writeOutput(writeformat=bprc.cli.args.outputformat, writefile=bprc.cli.args.outfile)






