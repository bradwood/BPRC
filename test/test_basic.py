import unittest
import yaml

from bprc.recipe import Recipe
from bprc.stepprocessor import StepProcessor

#TODO: Parametrise test cases -- try this http://pastebin.com/rdMqXc7b


class RecipeTest(unittest.TestCase):
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

    def test_yaml_load(self):
        """tests the yaml loads and is able to instantiate a Recipe object"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)

    def test_yaml_parse(self):
        """conducts misc checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        self.assertIsInstance(r,Recipe)
        self.assertEquals(r.steps[0].request.headers["Authorisation"],"yadda-step one authorisation header brad")
        self.assertEquals(r.steps[0].name,"Create Kong API")
        self.assertEquals(r.steps[0].response.body["id"],"this_is_a_param") #is None, but defined in the Yaml.
        self.assertIsNone(r.steps[1].response.headers["Authorisation"])

    def test_processor_prepare(self):
        """tests the php-like substitution logic in the recipe steps using various random checks"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)
        processor = StepProcessor(recipe=r, stepid=1) #instantiate a step processor/
        r.steps[1] = processor.prepare()
        self.assertEquals(r.steps[1].URL,"http://kong:8001/apdis/this_is_a_param/vala")
        self.assertEquals(r.steps[1].request.querystring["keysub"],"yadda-step one authorisation header brad")
        self.assertEquals(r.steps[1].request.body["key4"],"valueprefix application/json")
        self.assertEquals(r.steps[1].request.headers["Authorisation"],"bearer http://wiremock/blah")
        self.assertIsNone(r.steps[1].response.code)

#TODO: add cli tests.

if __name__ == '__main__':
    unittest.main()
