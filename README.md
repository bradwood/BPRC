# BPRC 
[![Build Status](https://travis-ci.org/bradwood/BPRC.svg?branch=master)](https://travis-ci.org/bradwood/BPRC)
[![codecov](https://codecov.io/gh/bradwood/BPRC/branch/master/graph/badge.svg)](https://codecov.io/gh/bradwood/BPRC)
[![PyPI version](https://badge.fury.io/py/bprc.svg)](https://badge.fury.io/py/bprc)
[![PyPI status](https://img.shields.io/pypi/status/bprc.svg?maxAge=2592000)](https://pypi.python.org/pypi/bprc)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/bradwood/BPRC/blob/master/LICENSE)

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
variables:
  name: brad
  favourite_colour: red
  age: 345
  drinks_beer: true
  age_and_colour: <%!age%>:<%!favourite_colour%>
  lorumfile: <%f./examples/lorum.txt%>

recipe:
  -  # step0
    name: Call Mockbin # see http://mockbin.org/docs#http-request
    httpmethod: POST
    URL: http://mockbin.org/request/path/to/<%!name%>
    request:
      body:
        name: My name is <%!name%>
        age: I am <%!age%> years old.
        beer_drinker: <%!drinks_beer%>
        lorum_impsum: <%!lorumfile%>
      querystring:
        colors: blue, green,  <%!favourite_colour%>
      headers:
        X-info: <%!age_and_colour%>
  - name: Call Mockbin with data from the previous call.
    httpmethod: GET
    URL: http://mockbin.org/request/path/to/<%!name%>
    request:
      headers:
        date_header_from_previous_call: <%=steps[0].response.headers["Date"]%>
      body:
        http_response_code_from_previous_call: <%=steps[0].response.code%>

```
## Other features
`bprc` provides the following features:
 - robust logging support
 - saving output files as raw HTTP (response only, or both request and response) or JSON
 - SSL support (including the ability to ingore invalid server certificates)
 - verbose and/or debug output
 - HTTP request bodies formatted either as JSON or form-encoded 

## Known issues/shortcomings
The following are known areas for improvement:
- poor tolerance of badly formatted YAML
- `--dry-run` option not implemented
- poor test coverage and test automation
- only handles JSON in the response bodies, XML or ther payload types are not supported.
- BUG: file substitution only happens in the variables section of the YAML, not the recipe section. 

## Planned improvements
- improving error handling
- better test coverage and integration with a coverage tool
- Implementing `--dry-run`
- passing an entire payload, rather than just a single parameter, using a file include
- setting a recipe variable via cli and/or environment variable

## Contributing
Contributions are welcome! Please fork, make your changes, add tests to cover your work and then raise a pull request.


