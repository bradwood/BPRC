"""
Tests the various printing options.
"""

import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
from mock import Mock
from mock import MagicMock
import yaml
import requests
import requests_mock

from ddt import ddt, data, file_data, unpack
from bprc.recipe import Recipe
from bprc.stepprocessor import StepProcessor
from bprc.varprocessor import VarProcessor
from bprc.variables import Variables
from bprc.utils import *
from bprc._version import __version__


@ddt
class SimpleTest(unittest.TestCase):
    def setUp(self):
        """Sets up the YAML data."""
        with open('tests/yaml_call_test.yml', 'r') as myfile:
            self.yamldata=myfile.read()
        datamap=yaml.load(self.yamldata)
        self.r = Recipe(datamap)


# --- Step: 9 ---
# -- Request --
# GET http://two.com
# Content-Length: 2
# accept: application/json
# content-type: application/json
# host: two.com
# user-agent: bprc/0.6.9
# -- Response --
# HTTP/0.0 200 OK
# content-type: application/json
# {
#     "msg": "hello"
# }

    @unpack
    @data(
              [
               9, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_outpout_default(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )
        
        from unittest.mock import patch
        from io import StringIO
        
        with patch('sys.stdout', new_callable=StringIO) as fake_std_out:
            import bprc.cli
            bprc.cli.args =  bprc.cli.parser.parse_args(['-','-'])
            prepared_statement = processor.call()
            processor.generateOutput(prepared_statement)
            self.assertGreaterEqual(fake_std_out.getvalue().find('--- Step: 9 ---'),0)
            self.assertGreaterEqual(fake_std_out.getvalue().find('-- Request --'),0)
            self.assertGreaterEqual(fake_std_out.getvalue().find('-- Response --'),0)
    
    @unpack
    @data(
              [
               9, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_outpout_call_json(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )
        
        from unittest.mock import patch
        from io import StringIO
        
        with patch('sys.stdout', new_callable=StringIO) as fake_std_out:
            import bprc.cli
            bprc.cli.args =  bprc.cli.parser.parse_args(['--output-format=json','-','-'])
            prepared_statement = processor.call()
            processor.generateOutput(prepared_statement)
            fake_std_out.seek(0)
            # these 3 should not match, so checking for -1
            self.assertEquals(fake_std_out.getvalue().find('--- Step: 9 ---'),-1)
            self.assertEquals(fake_std_out.getvalue().find('-- Request --'),-1)
            self.assertEquals(fake_std_out.getvalue().find('-- Response --'),-1)

            # this should match.
            self.assertGreaterEqual(fake_std_out.getvalue().find('hello'),0)








if __name__ == '__main__':
    unittest.main()
