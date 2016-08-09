# BPRC 
[![Build Status](https://travis-ci.org/bradwood/BPRC.svg?branch=master)](https://travis-ci.org/bradwood/BPRC)
[![codecov](https://codecov.io/gh/bradwood/BPRC/branch/master/graph/badge.svg)](https://codecov.io/gh/bradwood/BPRC)
[![PyPI version](https://badge.fury.io/py/bprc.svg)](https://badge.fury.io/py/bprc)
[![PyPI status](https://img.shields.io/pypi/status/bprc.svg)](https://pypi.python.org/pypi/bprc)
[![license](https://img.shields.io/github/license/bradwood/bprc.svg)](https://github.com/bradwood/BPRC/blob/master/LICENSE)

#Batch Processing RESTFul Client

A Dev/DevOps tool to automate calling a set of RESTFul JSON endpoints, with the ability to grab data from the JSON payload and use it in subsequent calls in the recipe.

## What it does
If you're a Dev/DevOps engineer you may have been faced with a situation where you find yourself writing a shell script to automate getting JSON data from one or more RESTful endpoints using `curl` or `wget` or `httpie`, and then parsing the output using `sed`, `grep` or `jq`. This tool is designed to provide a generic, simplied, yet powerful means of writing such scripts in the form of a simple _recipe_ specification, rather than a shell script. 

It relies on the excellent [Pygments](http://pygments.org/) and [Requests](http://docs.python-requests.org/en/master/) libraries.

## To install
This is a Python application which is written in Python 3. It has only currently been tested on Linux (Ubuntu 14.04).

### Pre-requisites
Make sure you've installed Python 3 and Pip 3
```bash
$ apt-get install -y python3
$ apt-get install -y python3-pip
```

### Installation
Install like this:
```bash
$ pip3 install bprc
```
Or a tagged version directly from GitHub (as PyPI can sometimes be erratic)
```bash
$ pip3 install https://github.com/bradwood/BPRC/tarball/x.y.x # replace with version tag in GitHub, no tar.gz extension needed
```

## How it works
The recipe is specified in a single YAML file which describes:
 - A list of variables that are initialised at the top of the recipe for use in the steps below.
 - A list of ordered steps that comprise the recipe, each containing some or all of the below:
	 - the URL that need to be visited
	 - the HTTP method to use
	 - the headers, querystring and body data to include in the step
	 - specific options to pass into the this step -- currently only the following options are supported:
		 - `request.retries` - set to the number of retries to attempt on the step in question. Only works for non-mutating calls (e.g., GETs), defaults to 3.
		 - `request.body_format` - can be set to `json` (default) or `form`. Will assemble the request body as either form-encoded or json and set the `Content-type:` header to `application/x-www-form-urlencoded` or `application/json` respectively.

Additionally, the YAML recipe file supports the ability to grab data from any part of any of the HTTP requests or responses in earlier steps in the recipe and insert them into later steps using a PHP-like construct. For example, say I have a 10-step recipe specified and in step 7 I need to POST some data that I received in step 3's reponse. I can include a construct like this in any part of the YAML file: 
```
<%=steps[3].response.body["id"]%>
```
Assuming that step 3 did indeed contain a parameter called `id` in it's JSON response payload, this data will then be substituted in the specified part of step 10's request.

The insertion of  variables anywhare in the recipe is done as shown:
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
    # using the HTTP Basic auth process to see if the Authorization: header
    # is visible in the output file.
    URL: http://Aladdin:OpenSesame@mockbin.org/request/path/to/<%!name%>
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
    options:
      request.retries: 10  #set retries to 10, overriding the default of 3.
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
 - Pretty-printed output

## Known issues/shortcomings
The following are known areas for improvement:
- poor tolerance of badly formatted YAML
- `--dry-run` option not implemented
- poor test coverage and test automation
- only handles JSON in the response bodies, XML or ther payload types are not supported.

## Planned improvements
- improving error handling
- better test coverage
- Implementing `--dry-run`
- passing an entire payload, rather than just a single parameter, using a file include
- setting a recipe variable via cli and/or environment variable

## Contributing
Contributions are welcome! Please fork, make your changes, add tests to cover your work and then raise a pull request.


