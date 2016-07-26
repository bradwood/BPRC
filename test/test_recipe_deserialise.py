import unittest
import yaml

from bprc.recipe import Recipe

class RecipeTest(unittest.TestCase):
    def setUp(self):
         """Sets up the YAML file."""
         self.yamlfile="test/test_recipe.yml"

    def test_yaml_load(self):
        with open(self.yamlfile) as stream:
            datamap=yaml.safe_load(stream)
        r = Recipe(datamap)
        self.assertIsInstance(r,Recipe)






















if __name__ == '__main__':
    unittest.main()
