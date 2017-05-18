import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
import yaml
from ddt import ddt, data, file_data, unpack
from bprc.recipe import Recipe
from bprc.stepprocessor import StepProcessor
from bprc.varprocessor import VarProcessor
from bprc.variables import Variables
from bprc.utils import *


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

    @unpack
    @data(
          ['steps[7].request.headers["directfile"]', "dA4eyNMS3A9q3azj"],
          ['steps[7].request.headers["file_from_var"]', "dA4eyNMS3A9q3azj"],
          ['steps[7].request.headers["directfile_plus"]', "dummy_password = dA4eyNMS3A9q3azj"],
          ['steps[7].request.headers["file_from_var_plus"]', "dummy_password = dA4eyNMS3A9q3azj"],
          )
    def test_processor_prepare_file_values(self,path_suffix,val):
        """tests the file and variable substitiion logic"""
        datamap=yaml.load(self.yamldata)
        r = Recipe(datamap)

        variables = Variables(datamap['variables'])
        varprocessor = VarProcessor(variables)

        for varname, varval in variables.items():
            variables[varname] = varprocessor.parse(varval, variables)

        for varname, varval in variables.items():
            variables[varname] = varprocessor.fileparse(varval, variables)

        step_under_test=7
        processor = StepProcessor(recipe=r, stepid=step_under_test, variables=variables) #instantiate a step processor
        r.steps[step_under_test] = processor.prepare()

        self.assertEquals(eval('r.' + path_suffix),val)


if __name__ == '__main__':
    unittest.main()
