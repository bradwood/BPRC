import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
import yaml
from ddt import ddt, data, file_data, unpack
from bprc.recipe import Recipe
from bprc.stepprocessor import StepProcessor
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
    @unpack ##note, this is hardwired into step1 only, for now... improve at some point
    @data(['steps[1].URL', "http://kong:8001/apdis/this_is_a_param/vala"],
          ['steps[1].request.querystring["keysub"]', "yadda-step one authorisation header brad"],
          ['steps[1].request.body["key4"]', "valueprefix application/json"],
          ['steps[1].request.headers["Authorisation"]', "bearer http://wiremock/blah"])
    def test_processor_prepare_values(self,path_suffix,val):
        """tests the php-like substitution logic in the recipe steps using various random checks for values"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        processor = StepProcessor(recipe=r, stepid=1, variables={}) #instantiate a step processor
        r.steps[1] = processor.prepare()
        self.assertEquals(eval('r.' + path_suffix),val)

    @data('r.steps[1].response.code')
    def test_processor_prepare_nones(self, path_suffix):
        """tests the php-like substitution logic in the recipe steps using various random checks for NONE"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        processor = StepProcessor(recipe=r, stepid=1,variables={}) #instantiate a step processor
        r.steps[1] = processor.prepare()
        self.assertIsNone(eval(path_suffix))

#TODO: TEST add cli tests.

if __name__ == '__main__':
    unittest.main()
