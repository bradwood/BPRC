"""
This module implements all the class types required to represent the YAML recipe in memory.
"""

import os
import sys
from itertools import chain

# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


import logging
import collections
from bprc.utils import vlog,errlog,verboseprint

class Headers(collections.MutableMapping): #Make this class behave and look like a dict
    """A collection of HTTP request or response headers"""

    def __init__(self, headers):
        self._headers = headers

    def __getitem__(self, key):
        return self._headers[key]  #Header key's should be case-insensitive

    def __setitem__(self, key, value):
        self._headers[key] = value

    def __delitem__(self, key):
        del self._headers[key]

    def __iter__(self):
        return iter(self._headers)

    def __len__(self):
        return len(self._headers)


class Body(collections.MutableMapping): #Make this class behave and look like a dict
    """A collection of parameters in an HTTP request or response body"""

    def __init__(self, body):
        self._body = body

    def __getitem__(self, key):
        return self._body[key]

    def __setitem__(self, key, value):
        self._body[key] = value

    def __delitem__(self, key):
        del self._body[key]

    def __iter__(self):
        return iter(self._body)

    def __len__(self):
        return len(self._body)


class QueryString(collections.MutableMapping): #Make this class behave and look like a dict
    """An collection of parameters passed on an HTTP Querystring, used for passing URL parameters"""
    def __init__(self, querystring):
        self._querystring=querystring

    def __getitem__(self, key):
        return self._querystring[key]

    def __setitem__(self, key, value):
        self._querystring[key] = value

    def __delitem__(self, key):
        del self._querystring[key]

    def __iter__(self):
        return iter(self._querystring)

    def __len__(self):
        return len(self._querystring)

class Options(collections.MutableMapping): #Make this class behave and look like a dict
    """An collection of parameters passed options into a step"""
    def __init__(self, options):
        self._options=options

    def __getitem__(self, key):
        return self._options[key]

    def __setitem__(self, key, value):
        self._options[key] = value

    def __delitem__(self, key):
        del self._options[key]

    def __iter__(self):
        return iter(self._options)

    def __len__(self):
        return len(self._options)

    def __str__(self):
        outstr = ''
        for key, value in sorted(self._options.items()):
            outstr += key+": " + str(value) +", "
        return outstr

class Response:
    """An HTTP Response, part of a step"""
    def __init__(self, *, code, headers, body):
        self.code = code
        self.headers=Headers(headers)
        self.body=Body(body)

class Request:
    """An HTTP Request, part of a step"""
    def __init__(self, *, headers, querystring, body):
        self.headers=Headers(headers)
        self.querystring=QueryString(querystring)
        self.body=Body(body)

class Step:
    """Defines a Step in the Recipe - a specific URL and its properties"""
    def __init__(self, *, name, URL, httpmethod, request, response, options):
        self.name = name
        self.URL = URL
        self.httpmethod = httpmethod
        self.options = Options(options)
        logging.debug("Options dump =" + str(self.options))

        # try:
        #     logging.debug(request["options"])
        # except KeyError as ke:
        #     vlog("No options values passed into step " + self.name)
        #     request.update({'options': {}})



        #TODO NTH -- fix these trys to not use logging as a test...
        try:
            logging.debug(request["headers"])
        except KeyError as ke:
            vlog("No request headers values passed into step " + self.name)
            request.update({'headers': {}})

        try:
            logging.debug(request["body"])
        except KeyError as ke:
            vlog("No request body values passed into step " + self.name)
            request.update({'body': {}})

        try:
            logging.debug(request["querystring"])
        except KeyError as ke:
            vlog("No request querystring values passed into step " + self.name)
            request.update({'querystring': {}})

        self.request = Request(headers=request["headers"], querystring=request["querystring"], body=request["body"])


        #set up empty response headers if none are passed
        try:
            logging.debug(response["headers"])
        except KeyError as ke:
            vlog("No response headers values passed into step " + self.name)
            response.update({'headers': {}})
        #set up empty response body if none is passed
        try:
            logging.debug(response["body"])
        except KeyError as ke:
            vlog("No response body values passed into step " + self.name)
            response.update({'body': {}})

        #set up empty response body if none is passed
        try:
            logging.debug(response["code"])
        except KeyError as ke:
            vlog("No response code values passed into step " + self.name)
            response.update({'code': ''})


        #logging.debug("in step constructor " + response["code"])
        self.response = Response(code=response["code"], headers=response["headers"], body=response["body"])

class Recipe:
    """Defines the Recipe class, which holds a list of URLs to process"""
    #takes a datamap to initialise the data structure
    def __init__(self, dmap):
        self.steps = []
        try:    #TODO: (75) @NTH don't use vlog to test for the error condition -- it messes up the log
            for i, item in enumerate(dmap["recipe"]):
                #instantiate the step object and add it to the list of steps.
                vlog("Parsing recipe step " + str(i))
                #set default step Name if one is not set in the YAML
                try:
                    logging.debug(dmap["recipe"][i]["name"])
                except KeyError as ke:
                    vlog("No step name set. Setting name to 'Step " + str(i)+"'")
                    dmap["recipe"][i].update({'name': 'GET'})

                try:
                    logging.debug(dmap["recipe"][i]["options"])
                except KeyError as ke:
                    vlog("No step options passed. Creating empty options opbject for this step.")
                    dmap["recipe"][i].update({'options': {}})

                #Check for URL passed in the YAML, otherwise fail.
                try:
                    logging.debug(dmap["recipe"][i]["URL"])
                except KeyError as ke:
                    errlog("No URL set in step " + str(i)+". Aborting...", ke)

                #set default HTTP Method if one is not set in the YAML
                try:
                    logging.debug(dmap["recipe"][i]["httpmethod"])
                except KeyError as ke:
                    vlog("No HTTPMethod set. Defaulting to GET")
                    dmap["recipe"][i].update({'httpmethod': 'GET'})

                # create request object if one is not set in the YAML
                # and populate it with a body, querystring and headers
                try:
                    logging.debug(dmap["recipe"][i]["request"])
                except KeyError as ke:
                    vlog("No request set. Creating an empty request object with headers, body and querystring")
                    dmap["recipe"][i].update({'request': {'body': {}, 'querystring': {}, 'headers': {}}})

                # create response object if one is not set in the YAML
                # and populate it with a body, querystring and headers
                try:
                    logging.debug(dmap["recipe"][i]["response"])
                except KeyError as ke:
                    vlog("No response set. Creating an empty response object with headers, body and response code")
                    dmap["recipe"][i].update({'response': {'body': {}, 'code': '', 'headers': {}}})

                #Now instantiate the step
                try:
                    vlog("Creating recipe step object id=" + str(i) + "...")
                    self.steps.append(Step(name=dmap["recipe"][i]["name"],
                                           URL=dmap["recipe"][i]["URL"],
                                           httpmethod=dmap["recipe"][i]["httpmethod"],
                                           request=dmap["recipe"][i]["request"],
                                           response=dmap["recipe"][i]["response"],
                                           options=dmap["recipe"][i]["options"]))
                except Exception as e:
                    errlog("Could not instantiate Recipe object from YAML file. Check for typos.", e)
                vlog("Parsed recipe step " + str(i) + " ok...")
        except TypeError as te:
            errlog("Could not parse YAML. PLease check the input file.", te)

    #TODO: @NTH  (74)implement __str__ for all other objects in this module
    def __str__(self):
        ret_str = ""
        for s in self.steps:
            ret_str += "Step= " + str(s)
        return ret_str



