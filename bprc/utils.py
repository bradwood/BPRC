"""
Misc utils and setup calls.
"""
import sys
import cli
import logging
import json
from urllib.parse import urlencode
import collections

httpstatuscodes = {
"100": "Continue",
"101": "Switching Protocols",
"200": "OK",
"201": "Created",
"202": "Accepted",
"203": "Non-Authoritative Information",
"204": "No Content",
"205": "Reset Content",
"206": "Partial Content",
"300": "Multiple Choices",
"301": "Moved Permanently",
"302": "Found",
"303": "See Other",
"304": "Not Modified",
"305": "Use Proxy",
"307": "Temporary Redirect",
"400": "Bad Request",
"401": "Unauthorized",
"402": "Payment Required",
"403": "Forbidden",
"404": "Not Found",
"405": "Method Not Allowed",
"406": "Not Acceptable",
"407": "Proxy Authentication Required",
"408": "Request Time-out",
"409": "Conflict",
"410": "Gone",
"411": "Length Required",
"412": "Precondition Failed",
"413": "Request Entity Too Large",
"414": "Request-URI Too Large",
"415": "Unsupported Media Type",
"416": "Requested range not satisfiable",
"417": "Expectation Failed",
"500": "Internal Server Error",
"501": "Not Implemented",
"502": "Bad Gateway",
"503": "Service Unavailable",
"504": "Gateway Time-out",
"505": "HTTP Version not supported"
}

#Turns on stack-traces if debug is passed
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if cli.args.debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print("{}: {}".format(exception_type.__name__, exception))

sys.excepthook = exceptionHandler

# set up logging
logleveldict = {'none': 100, #Hack, as will only log stuff >= 100, critical=50
                'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL
                }


#sets up a print function for the --verbose argument
verboseprint = print if cli.args.verbose else lambda *a, **k: None

# helper function to call both verboseprint and logging.info
def vlog(msg):
    verboseprint(msg)
    logging.info(msg)

#helper function to call logging.error and raise a RunTime error
def errlog(msg, e):
    logging.error(msg)
    raise RuntimeError(msg) from e

## helper functions to print out bits of a step.
def printstepcolophon(step,*,file, id):
    """Prints out the heading of the step to the output file"""
    print("--- Step " + str(id) + ": " + step.name +" ---",file=file)

def printhttprequest(step,*,file, id):
    """Prints out the heading of the step to the output file"""
    if step.request.querystring == {}:
        print(step.httpmethod + " " + step.URL,file=file)
    else:
        print(step.httpmethod + " " + step.URL +"?" + urlencode(step.request.querystring),file=file)
    print("HTTP/"+str(step.response.httpversion/10) +" " + str(step.response.code) +" " + httpstatuscodes[str(step.response.code)].upper() ,file=file)

def printheaders(step,*,file, id):
    """Prints out the heading of the step to the output file"""
    od = collections.OrderedDict(sorted(step.response.headers.items())) # sort the headers

    for key, val in od.items():
        print(key +": "+val, file=file)

def printbody(step,*,file, id):
    print(json.dumps(step.response.body,indent=4, sort_keys=True),file=file)
    print("\n", file=file)

