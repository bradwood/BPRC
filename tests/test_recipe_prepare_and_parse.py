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

#TODO@ test file inserts here @test (30)

@ddt
class SimpleTest(unittest.TestCase):
    def setUp(self):
        """Sets up the YAML data."""
        with open('tests/yaml_load_test.yml', 'r') as myfile:
            self.yamldata=myfile.read()


    @unpack
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

#TODO: @TEST (150) add cli tests.

if __name__ == '__main__':
    unittest.main()
