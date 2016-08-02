"""
This module implements the logic to process a step in a recipe
"""

import sys
import os

#TODO: make sure type casting works for boolean, int, string, float etc

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
from bprc._version import __version__


class BodyEncoder(json.JSONEncoder):
    """ encodes a request body"""
    def default(self,body):
        logging.debug("inside JSON BodyEncoder.default()")
        if isinstance(body,Body):
            return body._body


class StepProcessor():
    """Class to process """

    def __init__(self, *, recipe,stepid,variables): #kwargs for recipe and stepid
        """Instantiates the Step Processor Object"""
        self.recipe = recipe
        self.stepid = stepid
        self.variables = variables

    def prepare(self):
        """prepares the step by substituting php-like constructs or variables in the step subtree of the passed recipe"""
        vlog("Step parser initialised for step " + str(self.stepid))
        php_sub_pattern=re.compile(r'<%=(\S+?)%>') #substitution pattern to find - of the form <%=some.var["blah"]%>
        var_sub_pattern=re.compile(r'<%!(\S+?)%>')  #substitution pattern to find - of the form <%!somevar%>
        file_sub_pattern=re.compile(r'<%f(\S+?)%>')  #substitution pattern to find - of the form <%f./somefile.txt%>

        def _insert_file_param(m):
            """used by the re.subn call below - takes an re.match object -returns a string"""
            try:
                with open(str(m.group(1)), "rb") as f:
                    data=f.read()
                    text = data.decode('utf-8')
                    vlog("Found file-like pattern: <$f" +m.group(1) + "%>... substituting with contents of " + m.group(1))
            except Exception as e:
                errlog("Could not open "+ m.group(1)+" in the rest of the recipe. Aborting.", e)
            return text

        def _insert_php_param(m, recipe):
            """used by the re.subn call below - takes an re.match object -returns a string"""
            try:
                vlog("Found php-like pattern: <$=" +str(m.group(1)) + "%>... substituting with " +str(eval('recipe.' + m.group(1))))
            except KeyError as ke:
                errlog("Could not find "+ m.group(1)+" in the rest of the recipe. Aborting.", ke)
            return str(eval('recipe.' + m.group(1)))

        def _insert_var(m, variables):
            """used by the re.subn call below - takes an re.match object -returns a string """
            try:
                vlog("Found variable pattern: <$!" +str(m.group(1)) + "%>... substituting with " +str(eval('variables["' + m.group(1)+'"]')))
            except KeyError as ke:
                errlog("Could not find "+ m.group(1)+" in the variables. Aborting.", ke)
            return str(eval('variables["' + m.group(1)+'"]'))

        # Algorithm: -- TODO: turn this into a set of functions or a parser parametrised object.

        #do variable substitutions --  only doing files and other variables
        vlog("Variables: Commencing pattern match for substitutions...")
        for key in self.variables:
            vari=self.variables[key]
            file_substituted_text, n = file_sub_pattern.subn(_insert_file_param, str(vari))
            vlog("Files: Made " +str(n)+ " php-like substitutions. Result: " + key + "=" + file_substituted_text)
            v=file_substituted_text
            var_substituted_text, n = var_sub_pattern.subn(partial(_insert_var,variables=self.variables),v)
            vlog("Files: Made " +str(n)+ " variable substitutions. Result: "+key+"="+ var_substituted_text)
            self.variables[key]=var_substituted_text


        # process substitutions in Name string
        vlog("Name: Commencing pattern match for substitutions...")
        u=self.recipe.steps[self.stepid].name
        #TODO: add try: here
        php_substituted_text, n = php_sub_pattern.subn(partial(_insert_php_param, recipe=self.recipe), u)
        vlog("Name: Made " +str(n)+ " php-like substitutions. Result: Name="+ php_substituted_text)
        v=php_substituted_text
        var_substituted_text, n = var_sub_pattern.subn(partial(_insert_var,variables=self.variables),v)
        vlog("Name: Made " +str(n)+ " variable substitutions. Result: Name="+ var_substituted_text)
        self.recipe.steps[self.stepid].name=var_substituted_text

        # process substitutions in URL string
        vlog("URL: Commencing pattern match for substitutions...")
        u=self.recipe.steps[self.stepid].URL
        #TODO: add try: here
        php_substituted_text, n = php_sub_pattern.subn(partial(_insert_php_param, recipe=self.recipe), u)
        vlog("URL: Made " +str(n)+ " php-like substitutions. Result: URL="+ php_substituted_text)
        v=php_substituted_text
        var_substituted_text, n = var_sub_pattern.subn(partial(_insert_var,variables=self.variables),v)
        vlog("URL: Made " +str(n)+ " variable substitutions. Result: URL="+ var_substituted_text)
        self.recipe.steps[self.stepid].URL=var_substituted_text


        # loop through all QueryString dictionaries and process substition
        vlog("QueryString: Commencing pattern match for php-like pattern over all parameters...")

        for key in self.recipe.steps[self.stepid].request.querystring:
            vlog("QueryString: " + key + " found: Commencing pattern match for php-like pattern...")
            qs=self.recipe.steps[self.stepid].request.querystring[key]
            php_substituted_text, n = php_sub_pattern.subn(partial(_insert_php_param, recipe=self.recipe), qs)
            vlog("QueryString: Made " +str(n)+ " php-like substitutions. Result: " + key + "=" + php_substituted_text)
            v=php_substituted_text
            var_substituted_text, n = var_sub_pattern.subn(partial(_insert_var,variables=self.variables),v)
            vlog("QueryString: Made " +str(n)+ " variable substitutions. Result: "+key+"="+ var_substituted_text)
            self.recipe.steps[self.stepid].request.querystring[key]=var_substituted_text

        # loop through all Request.body dictionaries and process substitutions
        vlog("Body: Commencing pattern match for php-like pattern over all parameters...")
        for key in self.recipe.steps[self.stepid].request.body:
            vlog("Body: " + key + " found: Commencing pattern match for php-like pattern...")
            bod=str(self.recipe.steps[self.stepid].request.body[key])
            php_substituted_text, n = php_sub_pattern.subn(partial(_insert_php_param, recipe=self.recipe), bod)
            vlog("Body: Made " +str(n)+ " php-like substitutions. Result: " + key + "=" + php_substituted_text)
            v=php_substituted_text
            var_substituted_text, n = var_sub_pattern.subn(partial(_insert_var,variables=self.variables),v)
            vlog("Body: Made " +str(n)+ " variable substitutions. Result: "+key+"="+  var_substituted_text)
            self.recipe.steps[self.stepid].request.body[key]=var_substituted_text

        # loop through all Request.header dictionaries and process substitutions
        vlog("Header: Commencing pattern match for php-like pattern over all parameters...")
        for key in self.recipe.steps[self.stepid].request.headers:
            vlog("Header: " + key + " found: Commencing pattern match for php-like pattern...")
            heads=self.recipe.steps[self.stepid].request.headers[key]
            php_substituted_text, n = php_sub_pattern.subn(partial(_insert_php_param, recipe=self.recipe), heads)
            vlog("Header: Made " +str(n)+ " php-like substitutions. Result: " + key + "=" + php_substituted_text)
            v=php_substituted_text
            var_substituted_text, n = var_sub_pattern.subn(partial(_insert_var,variables=self.variables),v)
            vlog("Header: Made " +str(n)+ " variable substitutions. Result: "+key+"="+  var_substituted_text)
            self.recipe.steps[self.stepid].request.headers[key]=var_substituted_text



        return self.recipe.steps[self.stepid]

    def call(self):
        """calls the URL specified in the current step"""
        # set up parameters
        name = self.recipe.steps[self.stepid].name
        httpmethod = self.recipe.steps[self.stepid].httpmethod
        url = self.recipe.steps[self.stepid].URL

        try:
            vlog("Content-type = " +self.recipe.steps[self.stepid].request.headers["Content-type"])
        except KeyError as ke:
            vlog("No Content-type header set, defaulting to application/json")
            self.recipe.steps[self.stepid].request.headers["Content-type"]="application/json"

        try:
            vlog("User-agent = " +self.recipe.steps[self.stepid].request.headers["User-agent"])
        except KeyError as ke:
            vlog("Non User-agent header set, defaulting to bprc/" + __version__)
            self.recipe.steps[self.stepid].request.headers["User-agent"]="bprc/"+__version__

        #request
        querystring = self.recipe.steps[self.stepid].request.querystring
        requestheaders = self.recipe.steps[self.stepid].request.headers
        requestbody = self.recipe.steps[self.stepid].request.body

        #response
        responsecode = self.recipe.steps[self.stepid].response.code
        responseheaders = self.recipe.steps[self.stepid].response.headers
        responsebody = self.recipe.steps[self.stepid].response.body


        #make the call

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
        if r.status_code == 204 or r.status_code == 205: # no content or reset content don't send any content
            response_content_type = ""
        else:
            response_content_type = r.headers['Content-type'].split(';')[0] # grabs the xxx/yyyy bit of the header
        logging.debug(r.text)
        logging.debug("Content-type:" + response_content_type)
        logging.debug("Encoding:" + str(r.encoding))
        logging.debug("Text:" + r.text)

        #now, check if JSON was sent in the response body, if it was, load it, otherwise exit with an error
        if response_content_type.lower() == 'application/json' or response_content_type == "":
            vlog("JSON/empty response expected. Received Content-type: " + response_content_type)
            try:
                vlog("Attempting to parse JSON response body...")
                if response_content_type == "":
                    vlog("Response had no body... Proceeding...")
                    self.recipe.steps[self.stepid].response.body=None
                else:
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






