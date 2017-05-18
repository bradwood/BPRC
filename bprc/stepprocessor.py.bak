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
#import bprc.utils
from bprc.recipe import Body
from bprc.utils import vlog
from bprc.utils import errlog
from bprc.utils import verboseprint
from bprc.utils import httpstatuscodes
from bprc.utils import php_sub_pattern
from bprc.utils import var_sub_pattern
from bprc.utils import file_sub_pattern

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
        # php_sub_pattern=re.compile(r'<%=(\S+?)%>') #substitution pattern to find - of the form <%=some.var["blah"]%>
        # var_sub_pattern=re.compile(r'<%!(\S+?)%>')  #substitution pattern to find - of the form <%!somevar%>
        # file_sub_pattern=re.compile(r'<%f(\S+?)%>')  #substitution pattern to find - of the form <%f./somefile.txt%>

        # these are teh functions to produce the substition for each regex type
        from bprc.utils import _insert_file_param
        from bprc.utils import _insert_php_param
        from bprc.utils import _insert_var

        def executeSubstition(*, re, substitfunc, inputstring, recipe, variables):
            """executes the appropriate substitution type, given a:
            - regex pattern
            - substitution function
            - input text
            - the recipe object
            - the variables object
            """
            vlog("Commencing " + str(inputstring) + " substitution with " + substitfunc.__name__)
            substituted_text, n = re.subn(partial(substitfunc, recipe=recipe, variables=variables),str(inputstring))
            vlog("Made -------------"+ str(n) + " substitutions resulting in " + substituted_text)
            return substituted_text

        #parse the parts of each step for php-like patterns
        parts = [self.recipe.steps[self.stepid].name,
                 self.recipe.steps[self.stepid].URL,
                 self.recipe.steps[self.stepid].request.querystring,
                 self.recipe.steps[self.stepid].request.body,
                 self.recipe.steps[self.stepid].request.headers
                ]
        # these 2 lists work in pairs, for each type of substitution introducted.
        # you need to create a new regex object and and new substitution pattern for
        # each new subscription type.
        subREs = [var_sub_pattern, php_sub_pattern, file_sub_pattern]
        subfuncs = [_insert_var, _insert_php_param, _insert_file_param]

        partlist =[]
        for part in parts:
            for subRE, subfunc in zip(subREs,subfuncs):
                if isinstance(part, str): # part is a string
                    part = executeSubstition(
                           re=subRE,
                           substitfunc=subfunc,
                           inputstring=part,
                           recipe=self.recipe,
                           variables=self.variables)
                elif hasattr(part, '__getitem__'): # part is a dict
                    for key in part:
                        part[key] = executeSubstition(
                                  re=subRE,
                                  substitfunc=subfunc,
                                  inputstring=part[key],
                                  recipe=self.recipe,
                                  variables=self.variables)
            partlist.append(part)


        self.recipe.steps[self.stepid].name = partlist[0]
        self.recipe.steps[self.stepid].URL = partlist[1]
        self.recipe.steps[self.stepid].request.querystring = partlist[2]
        self.recipe.steps[self.stepid].request.body = partlist[3]
        self.recipe.steps[self.stepid].request.headers = partlist[4]

        return self.recipe.steps[self.stepid]

    def call(self):
        """calls the URL specified in the current step"""
        # set up parameters
        name = self.recipe.steps[self.stepid].name
        httpmethod = self.recipe.steps[self.stepid].httpmethod
        url = self.recipe.steps[self.stepid].URL
        options = self.recipe.steps[self.stepid].options

        from urllib.parse import urlparse
        parse_object = urlparse(url)


        if parse_object.hostname is None:
            try:
                raise ValueError("Couldn't find hostname in URL")
            except ValueError as e:
                errlog("Bad URL. Aborting...", e)

        if (parse_object.scheme != 'http') and (parse_object.scheme != 'https'):
            try:
                raise ValueError("Couldn't find http(s) scheme in URL")
            except ValueError as e:
                errlog("Bad URL. Aborting...", e)


        #Set host header on the request.
        try:
            vlog("Host: = " +self.recipe.steps[self.stepid].request.headers["Host"])
        except KeyError as ke:
            #from urllib.parse import urlparse
            vlog("No Host header set, using host part of URL: " + parse_object.hostname)
            self.recipe.steps[self.stepid].request.headers["Host"] = parse_object.hostname

        #Set user agent header
        try:
            vlog("User-agent = " +self.recipe.steps[self.stepid].request.headers["User-agent"])
        except KeyError as ke:
            vlog("No User-agent header set, defaulting to bprc/" + __version__)
            self.recipe.steps[self.stepid].request.headers["User-agent"]="bprc/"+__version__

        #Set accept header
        self.recipe.steps[self.stepid].request.headers["Accept"]="application/json"

        #NOTE: Step Options list HERE! @options
        extra_options = list(set(options.keys()) - set(['request.retries','request.body_format']))

        if len(extra_options)>0:
            #TODO (30) add a wlog options here @optimisation
            vlog("Unrecognised options detected... Ingoring " + str(extra_options))
            #logging.warn("Unrecognised options detected... Ingoring " + str(extra_options))

        #TODO: @OPTIMISATION (90) set gzip, deflate header @DOCUMENTATION

        #Sets up content header according to the format of the body.
        if 'request.body_format' in options:
            if options['request.body_format'] == 'form':   #form option passed, so must encode
                bodyformat='form'
                self.recipe.steps[self.stepid].request.headers["Content-type"]="application/x-www-form-urlencoded"

            else: #defaults to json
                bodyformat='json'
                self.recipe.steps[self.stepid].request.headers["Content-type"]="application/json"
        else:
            bodyformat='json' # if the option wasn't set at all, default to json too.
            self.recipe.steps[self.stepid].request.headers["Content-type"]="application/json"

        #sets up number of retries based on options passed
        if 'request.retries' in options:
            try:
                retries=int(options['request.retries'])
            except ValueError as e:
                errlog("Bad type passed on 'request.retries' option", e)
        else:
            retries=3 #sensible default

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
            if bodyformat == 'json':
                r = requests.Request(httpmethod.lower(),
                                      url,
                                      params=querystring,
                                      headers=requestheaders,
                                      data=json.dumps(requestbody, cls=BodyEncoder)
                                      )

            else:
                r = requests.Request(httpmethod.lower(),
                                      url,
                                      params=querystring,
                                      headers=requestheaders,
                                      data=requestbody._body
                                      )

            prepared = r.prepare()
            logging.debug("Req body" + prepared.body)
            # TODO: (100) @NTH OPTIMISATION, consider creating the session at the Recipe level, not
            # the step level. You can then set up a pool of http connections for reuse.
            s = requests.Session()
            # see http://docs.python-requests.org/en/master/_modules/requests/adapters/#HTTPAdapter
            # sets up connection pooling and retry configs.
            # also see http://stackoverflow.com/questions/21371809/cleanly-setting-max-retries-on-python-requests-get-or-post-method
            # and http://www.coglib.com/~icordasc/blog/2014/12/retries-in-requests.html
            a = requests.adapters.HTTPAdapter(max_retries=retries)
            b = requests.adapters.HTTPAdapter(max_retries=retries)
            s.mount('http://', a)
            s.mount('https://', b)
            logging.debug("Retries set to " + str(retries))

            logging.debug("Verify parameter == " + str(not bprc.cli.args.ignoressl))
            resp = s.send(prepared,verify=not bprc.cli.args.ignoressl)

        except requests.exceptions.SSLError as ssle:
            errlog("Could not verify SSL certificate. Try the --ignore-ssl option", ssle)
        except requests.exceptions.ConnectionError as httpe:
            errlog("Could not open HTTP connection. Network problem or bad URL?", httpe)
        except AttributeError as ae:
            errlog("Problem with URL or HTTP method", ae)

        # load the request headers from requests request opbject rather than just
        # relying on the step's request headers object. We do this to grab any other
        # request headers that requests adds, e.g., an Authorization header which
        # might be set in the library
        self.recipe.steps[self.stepid].request.headers=resp.request.headers

        #set the response code
        #and if it's 4xx or 5xx exist based on whether --ignore-http-errors were passed or not.
        self.recipe.steps[self.stepid].response.code=resp.status_code
        vlog("Received HTTP response code: " + str(self.recipe.steps[self.stepid].response.code))
        vlog("Code prefix " + str(resp.status_code)[:1])
        if (str(resp.status_code)[:1] == '4') or (str(resp.status_code)[:1] == '5'): #4xx or 5xx
            msg="Received an HTTP error code..." + str(resp.status_code)
            logging.error(msg)
            verboseprint(msg)
            if bprc.cli.args.skiphttperrors:
                pass #vlog("--skip-http-errors passed. Ignoring error and proceeding...")
            else:
                try:
                    resp.raise_for_status()
                except Exception as e:
                    if bprc.cli.args.debug:
                        print("Response body: " + resp.text)
                    errlog("Got error HTTP response and --skip-http-errors not passed. Aborting", e)

        #now grab the headers and load them into the response.headers
        self.recipe.steps[self.stepid].response.headers=resp.headers

        #Now load some of the meta data from the response into the step.response
        self.recipe.steps[self.stepid].response.httpversion=resp.raw.version
        self.recipe.steps[self.stepid].response.encoding=resp.encoding
        self.recipe.steps[self.stepid].response.statusmsg=httpstatuscodes[str(resp.status_code)]

        #now parse the json response and load it into the response.body
        if resp.status_code == 204 or resp.status_code == 205: # no content or reset content don't send any content
            response_content_type = ""
        else:
            try:
                response_content_type = resp.headers['Content-type'].split(';')[0] # grabs the xxx/yyyy bit of the header
            except KeyError as ke:
                errlog("Server sent content without content-type header. Cannot parse. Aborting...", ke)


        logging.debug(resp.text)
        logging.debug("Content-type:" + response_content_type)
        logging.debug("Encoding:" + str(resp.encoding))
        logging.debug("Text:" + resp.text)

        #now, check if JSON was sent in the response body, if it was, load it, otherwise exit with an error
        if response_content_type.lower() == 'application/json' or response_content_type == "":
            vlog("JSON/empty response expected. Received Content-type: " + response_content_type)
            try:
                vlog("Attempting to parse JSON response body...")
                if response_content_type == "":
                    vlog("Response had no body... Proceeding...")
                    self.recipe.steps[self.stepid].response.body=None
                else:
                    self.recipe.steps[self.stepid].response.body=json.loads(resp.text)
            except Exception as e:
                errlog("Failed to parse JSON response. Aborting", e)
            vlog("JSON parsed ok.")
        else:
            errlog("Response body is not JSON! Content-type: " +response_content_type+". Aborting", Exception("Non-JSON response not supported"))

        return prepared

    def generateOutput(self, req):
        """imvokes the output processor to write the output"""
        #instantiate an OutputProcessor
        output=OutputProcessor(step=self.recipe.steps[self.stepid], id=self.stepid, req=req)
        # get cli arguments and pass to the output processor

        output.writeOutput(writeformat=bprc.cli.args.outputformat, writefile=bprc.cli.args.outputfile, req=req)






