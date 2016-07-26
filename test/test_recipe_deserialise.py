import unittest
import yaml

from bprc.recipe import Recipe

#TODO: Parametrise test cases -- try this http://pastebin.com/rdMqXc7b


class RecipeTest(unittest.TestCase):
    def setUp(self):
         """Sets up the YAML file."""
         self.yamlfile="test/test_recipe.yml"

    def test_yaml_load(self):
        with open(self.yamlfile) as stream:
            datamap=yaml.safe_load(stream)
        r = Recipe(datamap)
        self.assertIsInstance(r,Recipe)
        self.assertEquals(r.steps[0].request.headers["Authorisation"],"yadda")
        self.assertEquals(r.steps[0].name,"Create Kong API")
        self.assertIsNone(r.steps[0].response.body["id"]) #is None, but defined in the Yaml.
        self.assertIsNone(r.steps[1].response.headers["Authorisation"])


















if __name__ == '__main__':
    unittest.main()
