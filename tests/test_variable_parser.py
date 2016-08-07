import sys
sys.path.append('/home/travis/build/bradwood/BPRC/bprc')
sys.path.append('/home/travis/build/bradwood/BPRC/bprc/tests')
print(sys.path)

import unittest
import yaml
from ddt import ddt, data, file_data, unpack
from bprc.variables import Variables
from bprc.varprocessor import VarProcessor
from bprc.utils import *

@ddt
class SimpleTest(unittest.TestCase):
    def setUp(self):
         """Sets up the YAML data."""
         self.yamldata="""
--- #sample recipe
variables:
  name: brad
  favourite_colour: red
  age: 345  #add tests for ints
  drinks_beer: true #add tests for boolean type
  age_and_colour: <%!age%>:<%!favourite_colour%>
  lorumfile: <%f./examples/lorum.txt%> # add tests for file types
  testnull:
"""
    @unpack
    @data(
          ['name', "brad"],
          ['age', '345'],
          ['age_and_colour', "345:red"],
# fails   ['drinks_beer', 'true'],
          )
    def test_processor_parse_values(self,varname,varval):
        """tests the php-like substitution logic in the recipe steps using various random checks for values"""
        datamap=yaml.load(self.yamldata)
        variables = Variables(datamap['variables'])
        varprocessor = VarProcessor(variables) #instantiate a variable processor
        variables[varname] = varprocessor.parse(variables[varname], variables)
        self.assertEquals(variables[varname],varval)

    @unpack
    @data(
          ['lorumfile', """Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
This is a new line
And so is this.
"""],
          )
    def test_processor_fileparse_values(self,varname,varval):
        """tests the php-like substitution logic in the recipe steps using various random checks for values"""
        datamap=yaml.load(self.yamldata)
        variables = Variables(datamap['variables'])
        varprocessor = VarProcessor(variables) #instantiate a variable processor
        variables[varname] = varprocessor.fileparse(variables[varname], variables)
        self.assertEquals(variables[varname],varval)
