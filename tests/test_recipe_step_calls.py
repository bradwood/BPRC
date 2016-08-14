"""
TO TEST:
 - error handling with bad URL
 - error handling with socket/timeout error
 - error handling with ssl ignoring
 - missing content type on response

 Request stuff:
 - setting of explicit header
 - bad options passed (type, or unrecognised key or value)
 - default headers set okay (host, user-agent, others)
 - http method types (including weird ones)
 - http retries
 - http body (json and URL encode)
 - retry after 4xx or 5xx (option passed)

"""

import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
import yaml
import requests_mock

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
        with open('tests/yaml_call_test.yml', 'r') as myfile:
            self.yamldata=myfile.read()
        datamap=yaml.load(self.yamldata)
        self.r = Recipe(datamap)
        #for i, step in enumerate(r.steps):
        #    processor = StepProcessor(recipe=r, stepid=i, variables={})
        #    r.steps[i] = processor.prepare()

    @unpack
    @data(
              [
               0, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # was'blah', # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_bad_URLs(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )

        with self.assertRaises(ValueError):
            prepared_statement = processor.call()

        #self.assertEqual(self.r.steps[id].response.code, 200)



    @unpack
    @data(
              [
               1, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               'http://two.com', # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_basic_call(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )
        prepared_statement = processor.call()
        self.assertEqual(self.r.steps[id].response.code, 200)



    #@unpack
    #@data(['steps[1].URL', "http://kong:8001/apdis/this_is_a_param/vala"],
    #      ['steps[1].request.querystring["keysub"]', "yadda-step one authorisation header brad"],
    #      ['steps[1].request.body["key4"]', "valueprefix application/json"],
    #      ['steps[1].request.headers["Authorisation"]', "bearer http://wiremock/blah"])
    #def test_processor_prepare_values(self,path_suffix,val):
    #    """tests the php-like substitution logic in the recipe steps using various random checks for values"""
    #    datamap=yaml.load(self.yamldata)
    #    r = Recipe(datamap)
    #    processor = StepProcessor(recipe=r, stepid=1, variables={}) #instantiate a step processor
    #    r.steps[1] = processor.prepare()
    #    self.assertEquals(eval('r.' + path_suffix),val)

    #@data('r.steps[1].response.code')
    #def test_processor_prepare_nones(self, path_suffix):
    #    """tests the php-like substitution logic in the recipe steps using various random checks for NONE"""
    #    datamap=yaml.load(self.yamldata)
    #    r = Recipe(datamap)
    #    processor = StepProcessor(recipe=r, stepid=1,variables={}) #instantiate a step processor
    #    r.steps[1] = processor.prepare()
    #    self.assertIsNone(eval(path_suffix))

    #@unpack
    #@data(
    #      ['steps[7].request.headers["directfile"]', "dA4eyNMS3A9q3azj"],
    #      ['steps[7].request.headers["file_from_var"]', "dA4eyNMS3A9q3azj"],
    #      ['steps[7].request.headers["directfile_plus"]', "dummy_password = dA4eyNMS3A9q3azj"],
    #      ['steps[7].request.headers["file_from_var_plus"]', "dummy_password = dA4eyNMS3A9q3azj"],
    #      )
    #def test_processor_prepare_file_values(self,path_suffix,val):
    #    """tests the file and variable substitiion logic"""
    #    datamap=yaml.load(self.yamldata)
    #    r = Recipe(datamap)

    #    variables = Variables(datamap['variables'])
    #    varprocessor = VarProcessor(variables)

    #    for varname, varval in variables.items():
    #        variables[varname] = varprocessor.parse(varval, variables)

    #    for varname, varval in variables.items():
    #        variables[varname] = varprocessor.fileparse(varval, variables)

    #    step_under_test=7
    #    processor = StepProcessor(recipe=r, stepid=step_under_test, variables=variables) #instantiate a step processor
    #    r.steps[step_under_test] = processor.prepare()

    #    self.assertEquals(eval('r.' + path_suffix),val)




#TODO: @TEST (150) add cli tests.

if __name__ == '__main__':
    unittest.main()
