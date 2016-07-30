"""
This module implements output processing class.
"""

from utils import vlog, errlog, verboseprint, printstepcolophon, printhttprequest, printheaders, printbody

import json
from pprint import pprint

class OutputProcessor():
    """Class to process """

    def __init__(self, *,step, id): #kwargs for recipe and stepid
        """Instantiates the Output Processor Object"""
        self.step = step
        self.id = id

    def writeOutput(self, *, writeformat, writefile):
        """Writes the output to the writefile in the format specified"""
        vlog("Generating output of step: " + str(self.id) +" " + self.step.name + ". Format=" + writeformat)

        if writeformat == 'json':
            with open(writefile + '.'+str(self.id),'wt') as f:
                print(json.dumps(self.step.response.body,indent=4, sort_keys=True),file=f)
                vlog("Wrote " + writefile + '.'+str(self.id))
        else:
            ## assume format = raw
            if self.id==0: open(writefile,'wt').close() # empty out the output file if it exists.
            with open(writefile,'at') as f:
                printstepcolophon(self.step,id=self.id, file=f)
                printhttprequest(self.step, id=self.id,file=f)
                printheaders(self.step, id=self.id,file=f)
                printbody(self.step, id=self.id,file=f)
                vlog("Appended output to " + writefile)



