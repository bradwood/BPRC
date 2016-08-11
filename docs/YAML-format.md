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

|Step element | Description                                                          | Data-type | Required  |
|-------------|----------------------------------------------------------------------|-----------|-----------|
| `name`      | a simple label for this step                                         | String    |no (check!)|
| `httpmethod`| an HTTP verb like `GET`, `POST`, `PUT` or `DELETE`\*                 | String    | yes       |
| `URL`       | the URL of the endpoint to visit (excluding querystring)             | String    | yes       |
| `request`   | request parameters, specifically `headers`, `querystring` and `body` | Dictionary| no        |
| `options`   | additional control options like retries or body-encoding instructions| Dictionary| no        |

\* `bprc` applies no checks on the method passed so you must ensure that the server will support the method selected.

#### Request
The `request` element of the step is optional, but if it is used, it must include **at least one** sub-element from the below list. 

|Request element| Description                                                            | Data-type  | Required|
|---------------|----------------------------------------------------------------------- |------------|---------|
| `headers`     | a set of key-value pairs defining all the HTTP headers to pass         | Dictionary | no      |
| `querystring` | a set of key-value pairs defining all the URL querystring to pass      | Dictionary | no      |
| `body`        | a set of key-value pairs defining all the JSON body parameters to pass | Dictionary | no      |
