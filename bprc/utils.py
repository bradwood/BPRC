"""
Misc utils and setup calls.
"""

import sys
import os


# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import bprc.cli
import logging
import json
from urllib.parse import urlencode
import collections
import re
from pygments import highlight, lexers, formatters
from json import JSONDecoder
from json import JSONDecodeError

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
    if bprc.cli.args.debug:
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
def vprint(arg):
    print(arg, file=sys.stderr)

verboseprint = vprint if bprc.cli.args.verbose else lambda *a, **k: None

# helper function to call both verboseprint and logging.info
def vlog(msg):
    verboseprint(msg)
    logging.info(msg)

#TODO: @NTH (40) @LOGGING Add a debug, WARNING an INFO version of vlog (parametrised) review all vlog/debug calls to make consistent format, etc.

#helper function to call logging.error and raise a RunTime error
def errlog(msg, e):
    logging.error(msg)
    try:
        raise RuntimeError(msg) from e
    except Exception as er:
        sys.stderr.write('ERROR: ' + str(er) + "\n")
    finally:
        raise e

## helper functions to print out bits of a step.
def printstepcolophon(step,*,file, id):
    """Prints out the heading of the step to the output file"""
    print("--- " + step.name +" ---",file=file)

def printhttprequest(step,*,file, id, colourful):
    """Prints out the heading of the step to the output file"""

    if colourful:
        if step.request.querystring == {}:
            print(step.httpmethod + " " + step.URL +"?" + urlencode(step.request.querystring),file=file)
            #print(highlight(step.httpmethod + " " + step.URL,lexers.HttpLexer(stripnl=True), formatters.TerminalFormatter()), file=file)
        else:
            print(step.httpmethod + " " + step.URL +"?" + urlencode(step.request.querystring),file=file)
    else:
        if step.request.querystring == {}:
            print(step.httpmethod + " " + step.URL,file=file)
        else:
            print(step.httpmethod + " " + step.URL +"?" + urlencode(step.request.querystring),file=file)


def printhttpresponse(step,*,file, id, colourful):
    if colourful:
        #print(highlight("HTTP/"+str(step.response.httpversion/10) +" " +
        #str(step.response.code) +" " +
        #httpstatuscodes[str(step.response.code)].upper(),lexers.HttpLexer(stripnl=True), formatters.TerminalFormatter()) ,file=file)
        print("HTTP/"+str(step.response.httpversion/10) +" " +
        str(step.response.code) +" " +
        httpstatuscodes[str(step.response.code)].upper() ,file=file)
    else:
        print("HTTP/"+str(step.response.httpversion/10) +" " +
        str(step.response.code) +" " +
        httpstatuscodes[str(step.response.code)].upper() ,file=file)

def printheaders(step,*,file, id, http_part, colourful):
    """Prints out the heading of the step to the output file"""
    logging.debug("in printheaders() http_part=" + http_part)
    od = collections.OrderedDict(sorted(eval("step."+ http_part +".headers.items()"))) # sort the headers
    for key, val in od.items():
        if colourful: #for now, does the same thing
            #print(highlight(key +": "+ val, lexers.TextLexer(stripnl=True), formatters.TerminalFormatter()), file=file)
            print(key +": "+val, file=file)
        else:
            print(key +": "+val, file=file)

#TODO: @REFACTOR (60) refactor all these print* functions -- too much copy/paste!

def printbody(step,*,file, id,http_part, colourful):
    if http_part == 'response':
        try:
            printoutput = json.dumps(step.response.body,indent=4, sort_keys=True)
            isJsonPayload = True
        except JSONDecodeError as e: # if it doesn't parse as JSON, set it as raw output
            printoutput = step.response.body
            colourful = False # and if it is not JSON, turn off colourful output.
            isJsonPayload = False
    else: ## http_part == request:
        try:
            printoutput = json.dumps(step.request.body,indent=4, sort_keys=True)
            isJsonPayload = True
        except JSONDecodeError as e: # if it doesn't parse as JSON, set it as raw output
            printoutput = step.request.body
            colourful = False # and if it is not JSON, turn off colourful output.
            isJsonPayload = False


    if colourful and isJsonPayload:
        print(highlight(printoutput,lexers.JsonLexer(),formatters.TerminalFormatter()),file=file)
    else: #not JSON payload, and therefore, not colourful either
        print(printoutput,file=file)



# define regex patterns.
php_sub_pattern=re.compile(r'<%=(\S+?)%>') #substitution pattern to find - of the form <%=some.var["blah"]%>
var_sub_pattern=re.compile(r'<%!(\S+?)%>')  #substitution pattern to find - of the form <%!somevar%>
file_sub_pattern=re.compile(r'<%f(\S+?)%>')  #substitution pattern to find - of the form <%f./somefile.txt%>

###### The three functions below are used to parse variables in the recipe.
# They are passed into the re.sub() call
def _insert_file_param(m,*,recipe,variables):
    """used by the re.subn call below - takes an re.match object -returns a string"""
    try:
        with open(str(m.group(1)), "rb") as f:
            data=f.read()
            text = data.decode('utf-8')
            vlog("Found file-like pattern: <$f" +m.group(1) + "%>... substituting with contents of " + m.group(1))
    except Exception as e:
        errlog("Could not open "+ m.group(1)+" in the rest of the recipe. Aborting.", e)
    return text

def _insert_php_param(m,*,recipe,variables):
    """used by the re.subn call below - takes an re.match object -returns a string"""
    try:
        vlog("Found php-like pattern: <$=" +str(m.group(1)) + "%>... substituting with " +str(eval('recipe.' + m.group(1))))
    except KeyError as ke:
        errlog("Could not find "+ m.group(1)+" in the rest of the recipe. Aborting.", ke)
    return str(eval('recipe.' + m.group(1)))

def _insert_var(m, *,recipe,variables):
    """used by the re.subn call below - takes an re.match object -returns a string """
    try:
        vlog("Found variable pattern: <$!" +str(m.group(1)) + "%>... substituting with " +str(eval('variables["' + m.group(1)+'"]')))
    except KeyError as ke:
        errlog("Could not find "+ m.group(1)+" in the variables. Aborting.", ke)
    return str(eval('variables["' + m.group(1)+'"]'))
