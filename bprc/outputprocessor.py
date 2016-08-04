"""
This module implements output processing class.
"""

import os
import sys
# see http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from bprc.utils import vlog
from bprc.utils import errlog
from bprc.utils import verboseprint
from bprc.utils import printstepcolophon
from bprc.utils import printhttprequest
from bprc.utils import printheaders
from bprc.utils import printbody
from bprc.utils import printhttpresponse

import json
from pprint import pprint
import logging

class OutputProcessor():
    """Class to process """

    def __init__(self, *,step, id, req): #kwargs for recipe and stepid
        """Instantiates the Output Processor Object"""
        self.step = step
        self.id = id
        self.req = req

    #TODO: REFACTOR Rewrite this Output generatro to use the requests object for output.
    # See http://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
    def writeOutput(self, *, writeformat, writefile, req):
        """Writes the output to the writefile in the format specified"""
        vlog("Generating output of step: " + str(self.id) +" " + self.step.name + ". Format=" + writeformat)

        if writeformat == 'json':
            if self.step.response.body is not None:
                with open(writefile + '.'+str(self.id),'wt') as f:
                    print(json.dumps(self.step.response.body,indent=4, sort_keys=True),file=f)
                    vlog("Wrote " + writefile + '.'+str(self.id))
            else:
                open(writefile + '.'+str(self.id),'wt').close() #touch the file (although it's empty)
        else:
            ## assume format = raw
            if self.id==0: open(writefile,'wt').close() # empty out the output file if it exists.
            with open(writefile,'at') as f:

                printstepcolophon(self.step,id=self.id, file=f)

                if writeformat == 'raw-all': ## need to write the http resquest first.
                    print("-- Request --", file=f)
                    printhttprequest(self.step, id=self.id,file=f)
                    printheaders(self.step, id=self.id,file=f,http_part='request')
                    logging.debug("PRINTING REQUEST HEADERS")
                    if self.step.request.body:
                        logging.debug("Req.body==" +req.body)
                        print(req.body, file=f)
                    print("-- Response --", file=f)

                # now write the response
                printhttpresponse(self.step, id=self.id,file=f)
                printheaders(self.step, id=self.id,file=f,http_part='response')

                if self.step.response.body:
                    printbody(self.step, id=self.id,file=f,http_part='response')
                    #print(req.body, file=f)
                vlog("Appended output to " + writefile)



