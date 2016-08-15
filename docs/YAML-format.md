# YAML recipe file format

The recipe file follows the standard [YAML](https://en.wikipedia.org/wiki/YAML) format which gives an easy, human-readable method of representing an hierarchical structured document that can be easily parsed by the software. The `bprc` recipe must follow the YAML format and must be appropriately indented. It has two top-level sections which follow the optional triple-dash start-of-document marker (`---`) as illustrated below:

<pre>
---
variables:
	<i>&lt;variables&gt;</i>
recipe:
	<i>&lt;steps&gt;</i>
</pre>

## Variables

The variables section is represented as a set of key-value pairs indented under the `variables` heading as shown here. You should only set literal variables here (strings, numbers, true/false settings) - **structured variables like lists or key-value pairs may work, but are not currently supported**. To be safe, just stick to a dictionary of variable names and values. 

```yaml
variables:
	name: brad
	favourite_colour: red
	age: 345
	drinks_beer: true
	age_and_colour: <%!age%>:<%!favourite_colour%> # 345:red
	lorumfile: <%f./examples/lorum.txt%> #entire contents of file.
```
You can use the `<%! %>` and `<%f %>` constructs to insert other variable values or data from files repsectively in any of the variable as shown above. You can use these constructs repeatedly to build up more complex strings without a problem, but **nesting of these constructs is currently untested**.

## Recipe

Unlike the variables section, the recipe section must be organised as a _list_ in YAML terms, with each item in the list representing a single _step_ in the recipe. The program will excute these steps in the order listed. In keeping with YAML rules for lists, each step starts with a `-` as shown here.

<pre>
recipe:
	- 
		<i>&lt;step 0...&gt;</i>
	-
		<i>&lt;step 1...&gt;</i>
	- 
		<i>&lt;...&gt;</i>
</pre>

### Steps
Each step must follow a defined structure in order to be processed properly, with some sections mandatory (like the `URL`) and other optional (like `headers`).

Each step can take the following elements as key-value pairs:

|Step element | Description                                                          | Data-type | Required  | Default         |
|-------------|----------------------------------------------------------------------|-----------|-----------| --------------- |
| `name`      | a simple label for this step                                         | String    | no        |  `Step n`       |
| `httpmethod`| an HTTP verb like `GET`, `POST`, `PUT` or `DELETE`\*                 | String    | yes       |   `GET`         |
| `URL`       | the URL of the endpoint to visit (excluding querystring)             | String    | yes       |   -             |
| `request`   | request parameters, specifically `headers`, `querystring` and `body` | Dictionary| no        |   see below     |
| `options`   | additional control options like retries or body-encoding instructions| Dictionary| no        |   see below     |

\* `bprc` applies no checks on the method passed so you must ensure that the server will support the method selected.

#### Name
A simple string which, if defined will be set and then used in verbose output or logging.

#### HTTP Method
The usual methods like `GET`, `POST`, `PUT`, `DELETE` and `PATCH` are typical here, but other methods will work if your server supports them.

#### Options
THe `options` element allows for certain control options to be passed to control how the step is executed. Currently, there are only 2 options as shown in the example below.

```yaml

recipe:
  -
    URL: http://some.domain.com/index.json
    options:
    	request.retries: 7
    	request.body_format: form
    request:
      headers:
        someheader: SomeVal
```
The `request.body_format` option can either be `form` or `json` and will specify how the request body is encoded. The `request.retries`, as the name suggests, specifies how many attempts to make when trying to fetch a URL. It will only take effect if the httpmethod is non-modifying on the server (e.g., a `GET`), `POST`s, `DELETE`s, etc will ignore this value and only try once. The default for non-destructive `GET`s is 3. 


#### URL
A URL scheme must be passed here. Only `http` and  `https` are currently supported. DNS or IP address network locations work, along with ports, URL paths, usernames and passwords (in the case of HTTP Basic Authentication).  Query strings can be passed direcly on the URL, but must be manually URLEncoded. It is probably better to use the querystring YAML element as described below. 

#### Request
The `request` element of the step is optional, but if it is used, it must include **at least one** sub-element from the below list. 

|Request element| Description                                                            | Data-type  | Required|   Default      |
|---------------|----------------------------------------------------------------------- |------------|---------|----------------|
| `headers`     | a set of key-value pairs defining all the HTTP headers to pass         | Dictionary | no      | `Host` & `Content-type`* |
| `querystring` | a set of key-value pairs defining all the URL querystring to pass      | Dictionary | no      |  -             |
| `body`        | a set of key-value pairs defining all the JSON body parameters to pass | Dictionary | no      |  -             |

\* `bprc` these defaults can be overridden. The `Host` header is determined from the URL if not supplied, and the `Content-type` is set to
either `application/json` or `application/x-www-form-urlencoded` depending on the Options passed.

##### Request Headers
These are simply a list of key-values pairs defined in the YAML like this. 

```yaml
recipe:
  -
    URL: http://some.domain.com/index.json
    request:
      headers:
        someheader: SomeVal
```

Note that `bprc` does not check for duplicate headers and will (probably) use the last header of the same key to replace any earlier ones with the same key. 
Note also that HTTP headers are case-insensitive as required in the HTTP/1.1 RFC. `Host` is a mandated header, and so `bprc` will attempt to set this to a
sane value if you do not explicitly set it.

#####  QueryString
These are simply a list of key-values pairs defined in the YAML like this. 

```yaml
recipe:
  -
    URL: http://some.domain.com/index.json
    request:
      querystring:
        var1: val1
        var2: val2

```

Note that `bprc` does not check for duplicate querystring parameters and will simply pass whatever is specified in the recipe on the URL.  It will URLEncode the querystring before appending it to the URL, so the above request will look like `GET http://some.domain.com/index.json&var1=val1&var2=val2`

#####  Body
These are simply a list of key-values pairs defined in the YAML like this. 

```yaml
recipe:
  -
    URL: http://some.domain.com/index.json
    request:
      body:
        var1: val1
        var2: val2

```

Note that `bprc` does not check for duplicate body parameters and will simply pass whatever is specified in the recipe in the request body. The body, by default, will be encoded as a JSON payload unless form body-encoding has been specified as an Option. **Nested JSON structures beyond a basic dictionary of key-value pairs are not currently supported (tested).**

# Performing substitutions

TBC
