import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
import yaml
from ddt import ddt, data, file_data, unpack
from bprc.recipe import Recipe
from bprc.utils import *

#TODO: TEST -Add mocking for some of these tests to make them smaller/less complex

@ddt
class SimpleTest(unittest.TestCase):
    def setUp(self):
         """Sets up the YAML data."""
         self.yamldata="""
--- #sample recipe
recipe:
  -  # step0
    name: Create Kong API
    httpmethod: POST
    URL: http://kong:8001/apis
    request:
      body:
        name: Consumer API
        upstream_uri: http://wiremock/blah
        strip_url: false
      headers:
        Authorisation: yadda-step one authorisation header brad
        Content-type: application/json
      querystring:
        keya: vala
        keyb: valb
    response: # set up this response section if you need to pull out data here for use later in the recipe.
      body:
        id: this_is_a_param
      headers:
        Authorisation:
      code:
  -
    name: Load OAUTH Plugin
    httpmethod: POST
    URL: http://kong:8001/apdis/<%=steps[0].response.body["id"]%>/<%=steps[0].request.querystring["keya"]%> #gets the JSON field id from the body of the response from step 1.
    request:
      querystring:
        key3: value3
        keysub: <%=steps[0].request.headers["Authorisation"]%>
      body:
        key4: valueprefix <%=steps[0].request.headers["Content-type"]%>
      headers:
        blah: blahbha
        Authorisation: bearer <%=steps[0].request.body["upstream_uri"]%>
    response: # set up this response section if you need to pull out data here for use later in the recipe.
      code:
      body:
      headers:
        Authorisation:

"""
#TODO: TEST impement excecptions test
    def test_yaml_load(self):
        """tests the yaml loads and is able to instantiate a Recipe object"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        self.assertIsInstance(r,Recipe)
        #TODO: TEST add a test for multiple docs in 1 YAML (using ---) -- reject this??

    @unpack
    @data(['steps[0].request.headers["Authorisation"]', "yadda-step one authorisation header brad"],
          ['steps[0].name', "Create Kong API"],
          ['steps[0].response.body["id"]', "this_is_a_param"])
    def test_yaml_parse_values(self, path_suffix, val):
        """conducts misc value checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        self.assertEquals(eval('r.' + path_suffix),val)

    @data('r.steps[1].response.headers["Authorisation"]')
    def test_yaml_parse_nones(self, path_suffix):
        """conducts misc None checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        self.assertIsNone(eval(path_suffix))

if __name__ == '__main__':
    unittest.main()
