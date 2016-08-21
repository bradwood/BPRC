"""
TO TEST:
 [x] error handling with bad URL
 [x] http-codes (check for different numbers) 
 [x] missing content-type response header aborts unless a 204 & 205 response code is returned
 [x] error handling with socket/timeout error
 [ ] error handling with ssl ignoring - NOT TESTED (YET)

 [x] setting of request explicit headers
 [x] bad options passed (type, or unrecognised key or value)
 [x] default request headers set okay (host, user-agent, others)
 [x] http method types (including weird ones) -- Note, unknown methods deliberately passed through
 [x] http retries -- MANUALLY TESTED ONLY (eyeball)
 [ ] http request body (json and URL encode)
 [x] retry after 4xx or 5xx (option passed)

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


    @data(
              0, 1, 2, 3, 5, 6, 7, 8
         )
    @requests_mock.Mocker(kw='mock')
    def test_bad_URLs(self, id,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           requests_mock.GET,
                           requests_mock.ANY,
                           status_code=200,
                           headers={'content-type': 'application/json'},
                           json={'msg': 'hello'}
                           )

        with self.assertRaises(ValueError):
            prepared_statement = processor.call()


    @unpack
    @data(
              [
               9, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               'http://two.com', # url / path to match
               {'someheader': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_server_sent_no_content_header(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )

        with self.assertRaises(KeyError):
            prepared_statement = processor.call()


    @unpack
    @data(
              [
               9, # step id being mocked
               204, # response code
               requests_mock.GET, # http method
               'http://two.com', # url / path to match
               {'someheader': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],

               [
               9, # step id being mocked
               205, # response code
               requests_mock.GET, # http method
               'http://two.com', # url / path to match
               {'someheader': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
         )
    @requests_mock.Mocker(kw='mock')
    def test_server_sent_no_content_header_ok_for_204_or_205 (self, id, code, method, urlmatch, headers, json_body,**kwargs):
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
        self.assertEqual(self.r.steps[id].response.code, code) # checks the code was 204 or 205
        self.assertEqual(self.r.steps[id].response.headers, headers) # checks all headers mocked are loaded in the response object


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


    def _connection_error(self):
        raise requests.exceptions.ConnectionError

    def _ssl_error(self):
        raise requests.exceptions.SSLError

    @unpack
    @data(
              [
               9, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               'http://two.com', # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    def test_connection_error(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        requests.send = MagicMock(side_effect=self._connection_error)
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            prepared_statement = processor.call()

    #TODO: @TEST - fix ssl mocking (99)

    #@unpack
    #@data(
    #          [
    #           10, # step id being mocked
    #           200, # response code
    #           requests_mock.GET, # http method
    #           'https://two.com', # url / path to match
    #           {'content-type': 'application/json'}, # res headers
    #           {'msg': 'hello'} # res body
    #           ]
    #     )
    #def test_ssl_error(self, id, code, method, urlmatch, headers, json_body,**kwargs):
    #    requests.send = MagicMock(side_effect=self._ssl_error)
    #    processor = StepProcessor(recipe=self.r, stepid=id, variables={})
    #    self.r.steps[id] = processor.prepare()
    #    with self.assertRaises(requests.exceptions.SSLError) as sslm:
    #        prepared_statement = processor.call()


    @unpack
    @data(
              [
               11, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test__bad_options_passed(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        """checks if type checks are done on request.retries"""
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

    @unpack
    @data(
              [
               12, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_default_passed(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        """checks if type checks are done on request.retries"""
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )

        #with self.assertRaises(ValueError):
        #    prepared_statement = processor.call()


    #NOTE: This is where default request headers are tested.

    @unpack
    @data(
              [
               13, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ]
         )
    @requests_mock.Mocker(kw='mock')
    def test_default_headers_set(self, id, code, method, urlmatch, headers, json_body,**kwargs):
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
        self.assertEqual(self.r.steps[id].request.headers["user-agent"], 'bprc/'+__version__)
        self.assertEqual(self.r.steps[id].request.headers["host"], 'this.is.a.url.org')


    @unpack
    @data(
              [
               14, # step id being mocked
               200, # response code
               requests_mock.POST, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               16, # step id being mocked
               200, # response code
               requests_mock.DELETE, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               17, # step id being mocked
               200, # response code
               requests_mock.PUT, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               18, # step id being mocked
               200, # response code
               requests_mock.PATCH, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               19, # step id being mocked
               200, # response code
               requests_mock.HEAD, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               20, # step id being mocked
               200, # response code
               requests_mock.OPTIONS, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],

         )
    @requests_mock.Mocker(kw='mock')
    def test_default_http_methods(self, id, code, method, urlmatch, headers, json_body,**kwargs):
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
        self.assertEqual(self.r.steps[id].httpmethod, method)

    @unpack
    @data(
              [
               15, # step id being mocked
               200, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               14, # step id being mocked
               201, # response code
               requests_mock.POST, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               206, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
         )
    @requests_mock.Mocker(kw='mock')
    def test_non_error_http_response_codes(self, id, code, method, urlmatch, headers, json_body,**kwargs):
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
        self.assertEqual(self.r.steps[id].response.code, code)

    @unpack
    @data(
            
              [
               15, # step id being mocked
               401, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               404, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               500, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               410, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],

         )
    @requests_mock.Mocker(kw='mock')
    def test_error_http_response_codes(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )
        with self.assertRaises(requests.exceptions.HTTPError):
            prepared_statement = processor.call()


    @unpack
    @data(
            
              [
               15, # step id being mocked
               401, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               404, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               500, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],
              [
               15, # step id being mocked
               410, # response code
               requests_mock.GET, # http method
               requests_mock.ANY, # url / path to match
               {'content-type': 'application/json'}, # res headers
               {'msg': 'hello'} # res body
               ],

         )
    @requests_mock.Mocker(kw='mock')
    def test_error_http_response_codes_suppressed(self, id, code, method, urlmatch, headers, json_body,**kwargs):
        processor = StepProcessor(recipe=self.r, stepid=id, variables={})
        self.r.steps[id] = processor.prepare()
        kwargs['mock'].request(  # set up the mock
                           method,
                           urlmatch,
                           status_code=code,
                           headers=headers,
                           json=json_body
                           )

        import bprc.cli
        bprc.cli.args =  bprc.cli.parser.parse_args(['--skip-http-errors'])
        prepared_statement = processor.call()
        self.assertEqual(self.r.steps[id].response.code, code)




#TODO: @TEST (150) add cli tests.

if __name__ == '__main__':
    unittest.main()
