# BPRC 
[![Build Status](https://travis-ci.org/bradwood/BPRC.svg?branch=master)](https://travis-ci.org/bradwood/BPRC)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/bradwood/BPRC/blob/master/LICENSE)
[![bprc version](https://img.shields.io/pypi/v/bprc.svg?maxAge=2592000)](https://pypi.python.org/pypi/bprc)
[![PyPI version](https://badge.fury.io/py/bprc.svg)](https://badge.fury.io/py/bprc)
[![PyPI status](https://img.shields.io/pypi/status/bprc.svg?maxAge=2592000)](https://pypi.python.org/pypi/bprc)

#Batch Processing RESTFul Client

A Dev/DevOps tool to automate calling a set of RESTFul JSON endpoints, with the ability to grab data from the JSON payload and use it in subsequent calls in the recipe.

## What it does
If you're a Dev/DevOps engineer you may have been faced with a situation where you find yourself writing a shell script to automate getting JSON data from one or more RESTful endpoints using `curl` or `wget` or `httpie`, and then parsing the output using `sed`, `grep` or `jq`. This tool is designed to provide a generic, simplied, yet powerful means of writing such scripts in the form of a simple _recipe_ specification, rather than a shell script. 

## To install
This is a Python application which is written in Python 3. It has only currently been tested on Linux (Ubuntu 14.04).

### Pre-requisites
Make sure you've installed Python 3 and Pip 3
```bash
apt-get install -y python3
apt-get install -y python3-pip
```

### Installation
Install like this:
```bash
pip3 install bprc
```

## How it works
The recipe is specified in a single YAML file which describes:
 - the list of URLs that need to be visited, in order
 - the HTTP method to use for each
 - the headers, querystring and body data to include for each step of the recipe

Additionally, the YAML recipe file supports the ability to grab data from any part of any of the HTTP requests or responses in earlier steps in the recipe and insert them into later steps using a PHP-like construct. For example, say I have a 10-step recipe specified and in step 7 I need to POST some data that I received in step 3's reponse. I can include a construct like this in any part of the YAML file: 
```
<%=steps[3].response.body["id"]%>
```
Assuming that step 3 did indeed contain a parameter called `id` in it's JSON response payload, this data will then be substituted in the specified part of step 10's request.

The inclusion of variables in the recipe are also supported. They can be inserted into the recipe as shown:
```
<%!varname%>
```
Files can also be included into a recipe using a construct like this:
```
<%f/path/to/file.txt%>
```

### Sample Recipe
This functionality is best illustrated with a complete recipe file as shown below.
```yaml
--- #sample recipe
variables: ## substitution patter for variables is <%!varname%>
  varname: val-1
  var2: 8001
recipe:
  -  # step0
    name: HTTPBIN call
    httpmethod: GET
    URL: http://httpbin.org/get
    request:
      body:
        name: json name parameter
        url: http://wiremock/blah
        booleanflag: false
      headers:
        X-ABC: 1231233425435fsdf <%!varname%>
      querystring:
        keya: vala
        keyb: valb
    response: # set up this response section if you need to pull out data here for use later in the recipe.
              # the YAML hierarchy will map to the JSON response obtained and the the values received from
              # the call will be inserted into the appropriate response variables so that subsequent steps
              # can access them with the php-like construct
      body:
        id: this_is_a_param
        origin: somval
      headers:
        Authorization:
      code: #HTTP response code
  -
    name: Load OAUTH Plugin
    httpmethod: POST
    URL: http://httpbin.org/post
    request:
      querystring:
        key3: value3
      body:
        key4: valueprefix <%=steps[0].request.headers["X-ABC"]%>
      headers:
        blah: blahbha
        Authorisation: bearer <%=steps[0].request.querystring["keyb"]%>
   
```
## Other features
`bprc` provides the following features:
 - robust logging support
 - saving output files as raw HTTP or JSON
 - SSL support (including the ability to ingore invalid server certificates)
 - Dry-run *(Not implemented yet)*
 - verbose and/or debug output

## Known issues/shortcomings
The following are known areas for improvement:
- poor tolerance of badly formatted YAML
- `--dry-run` option not implemented
- poor test coverage and test automation
- only handles JSON in both the request and response bodies, XML or ther payload types are not supported.
- can not do a substitution using data in a response body if the JSON payload is a list (array). Only dictionaries (key/value pairs) at the top level of the JSON document are currently supported. 
- does not support multiple YAML recipes in one file (separated by `---`)

## Planned improvements
- Improving error handling
- Better test coverage and integration with a coverage tool
- Implementing `--dry-run`
