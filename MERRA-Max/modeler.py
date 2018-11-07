#!/usr/bin/python

import argparse
import os
import shutil
import sys

from MaxEntHelper import MaxEntHelper
from MmxApplication import MmxApplication
from MmxConfig import MmxConfig

#-------------------------------------------------------------------------------
# class Modeler
#-------------------------------------------------------------------------------
class Modeler(MmxApplication):
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, configFile, logger = None):
        
        mmxConfig = MmxConfig()
        mmxConfig.initializeFromFile(configFile)
        super(Modeler, self).__init__(mmxConfig, 'Modeler', logger)
        self.logHeader()
    
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'MODELER'

    #---------------------------------------------------------------------------
    # run
    #---------------------------------------------------------------------------
    def run(self):
        
        # Ensure the final model directory exists.
        finalDir = os.path.join(self.config.outDir, 'FINAL_MODEL')
        
        if not os.path.exists(finalDir):
            os.mkdir(finalDir)
        
        MaxEntHelper.copyAscFiles(self.config.topTen, finalDir)
        
        samplesFile = MaxEntHelper.createSamplesFile(self.config.presFile, 
                                                     self.config.species, 
                                                     finalDir)

        MaxEntHelper.runMaxEnt(samplesFile, finalDir, finalDir, self.logger)
        
#-------------------------------------------------------------------------------
# main
#
# 1.  configureMmxRun
# 2.  getMerra
# 3.  prepareImages
# 4.  prepareTrials
# 5.  ./runTrials.py 
# 6.  ./selector.py -c 
# 7.  ./modeler.py -c ~/Desktop/SystemTesting/Mmx/config.mmx
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application runs the final model.'
    parser = argparse.ArgumentParser(description = desc)
    
    parser.add_argument('-c',
                        required = True, 
                        help = 'Path to MERRA-Max configuration file')
    
    args = parser.parse_args()
    modeler = Modeler(args.c)
    modeler.run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())

