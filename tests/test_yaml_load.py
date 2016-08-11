import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
import yaml
from ddt import ddt, data, file_data, unpack
from bprc.recipe import Recipe
from bprc.utils import *

#TODO: @TEST  (100) -Add mocking for some of these tests to make them smaller/less complex

@ddt
class SimpleTest(unittest.TestCase):
    def setUp(self):
        """Sets up the YAML data."""
        with open('tests/yaml_load_test.yml', 'r') as myfile:
            self.yamldata=myfile.read()

    def test_yaml_load(self):
        """tests the yaml loads and is able to instantiate a Recipe object"""
        datamap=yaml.safe_load(self.yamldata)
        r = Recipe(datamap)
        self.assertIsInstance(r,Recipe)
        #TODO: @TEST (70) add a test for multiple docs in 1 YAML (using ---) -- reject this??

    @unpack
    @data(['steps[0].request.headers["Authorisation"]', "yadda-step one authorisation header brad"],
          ['steps[0].name', "Create Kong API"],
          ['steps[0].response.body["id"]', "this_is_a_param"])
    def test_yaml_parse_values(self, path_suffix, val):
        """conducts misc value checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.safe_load(self.yamldata)
        r = Recipe(datamap)
        self.assertEquals(eval('r.' + path_suffix),val)

    @data('r.steps[1].response.headers["Authorisation"]')
    def test_yaml_parse_nones(self, path_suffix):
        """conducts misc None checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.safe_load(self.yamldata)
        r = Recipe(datamap)
        self.assertIsNone(eval(path_suffix))

    @unpack
    @data(['steps[2].request.querystring["qsbool0"]'],
          ['steps[2].request.querystring["qsbool1"]'],
          ['steps[2].request.querystring["qsbool2"]'],
          ['steps[2].request.querystring["qsbool3"]'],
          ['steps[2].request.headers["headerbool0"]'],
          ['steps[2].request.headers["headerbool1"]'],
          ['steps[2].request.headers["headerbool2"]'],
          ['steps[2].request.headers["headerbool3"]'],
          ['steps[2].request.body["bodybool0"]'],
          ['steps[2].request.body["bodybool1"]'],
          ['steps[2].request.body["bodybool2"]'],
          ['steps[2].request.body["bodybool3"]'],)
    def test_yaml_true(self,path_suffix):
        """conducts misc Boolean checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.safe_load(self.yamldata)
        r = Recipe(datamap)
        self.assertTrue(eval('r.' + path_suffix))


    @unpack
    @data(['steps[2].request.querystring["qsbool0"]'  , bool],
          ['steps[2].request.querystring["qsint"]'    , int],
          ['steps[2].request.querystring["qsstring"]' , str],
          ['steps[2].request.querystring["qsfloat"]'  , float],
          ['steps[2].request.headers["headerbool0"]'  , bool],
          ['steps[2].request.headers["headerint"]'    , int],
          ['steps[2].request.headers["headerstring"]' , str],
          ['steps[2].request.headers["headerfloat"]'  , float],
          ['steps[2].request.body["bodybool0"]'       , bool],
          ['steps[2].request.body["bodyint"]'         , int],
          ['steps[2].request.body["bodystring"]'      , str],
          ['steps[2].request.body["bodyfloat"]'       , float],
          )
    def test_yaml_types(self, path_suffix, type):
        """conducts misc value checks on the values passed in from the yaml on the Recipe object"""
        datamap=yaml.safe_load(self.yamldata)
        r = Recipe(datamap)
        self.assertIsInstance(eval('r.' + path_suffix),type)

#TODO: @TEST (20) recipe object types (Step, QueryString, URL, etc)
#TODO: @TEST (20) URL validity
#TODO: @TEST (20) missing Name, URL, Method etc
#TODO: @TEST (20) Finite list of HTTP methods
#TODO: @TEST (20) Empty Request, QS, Header objects list of HTTP methods
#TODO: @TEST (20) Unrecognised element, e.g: "Reesponse", "Heeederr" objects list of HTTP methods
#TODO@ @TEST (20) dicts/lists in a leaf element in the recipe.





if __name__ == '__main__':
    unittest.main()
