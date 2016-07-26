"""
This module implements all the class types required to represent the YAML recipe in memory.
"""

import logging
import collections

class Headers(collections.MutableMapping): #Make this class behave and look like a dict
    """A collection of HTTP request or response headers"""

    def __init__(self, headers):
        self._headers = headers

    def __getitem__(self, key):
        return self._headers[key]

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


class QueryString: #Make this class behave and look like a dict
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


class Response:
    """An HTTP Response, part of a step"""
    def __init__(self, code, headers, body):
        self.code = code
        self.headers=Headers(headers)
        self.body=Body(body)

class Request:
    """An HTTP Request, part of a step"""
    def __init__(self, headers, querystring, body): # TODO use kwargs
        self.headers=Headers(headers)
        logging.debug("in Request.__init__", headers)
        self.querystring=QueryString(querystring)
        self.body=Body(body)

class Step:
    """Defines a Step in the Recipe - a specific URL and its properties"""
    def __init__(self, name, URL, httpmethod, request, response): #TODO: use kwargs
        self.name = name
        self.URL = URL
        self.httpmethod = httpmethod
        self.request = Request(request["headers"], request["querystring"],request["body"])
        self.response = Response(response["code"], response["headers"], response["body"])

class Recipe:
    """Defines the Recipe class, which holds a list of URLs to process"""
    #takes a datamap to initialise the data structure
    def __init__(self, dmap):
        self.steps = []
        for i, item in enumerate(dmap["recipe"]):
            #instantiate the step object and add it to the list of steps.
            self.steps.append(Step(dmap["recipe"][i]["name"],
                                   dmap["recipe"][i]["URL"],
                                   dmap["recipe"][i]["httpmethod"],
                                   dmap["recipe"][i]["request"],
                                   dmap["recipe"][i]["response"]))

    # def __str__(self):
    #     #TODO make a nice string printable function here.
    #     return '{0!s}'.format(self)
