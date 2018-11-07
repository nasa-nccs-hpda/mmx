#!/usr/bin/python

import argparse
import os
import sys

from BoundingBox import BoundingBox
from MmxApplication import MmxApplication
from MmxConfig import MmxConfig
from PresencePoints import PresencePoints

#-------------------------------------------------------------------------------
# class ConfigureMmxRun
#-------------------------------------------------------------------------------
class ConfigureMmxRun(MmxApplication):
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, presFile, startDate, endDate, species, inDir = '.', 
                 outDir = '.', numProcs = 10, numTrials = 10, logger = None):
        
		# Create the MmxConfig object.
        mmxConfig = MmxConfig()

        mmxConfig.initializeFromValues(presFile, startDate, endDate, species, 
                                       inDir, outDir, numProcs, numTrials)

		# Define the bounding box.
        presPts = PresencePoints(presFile, species)
        bbox = BoundingBox(presPts.points, presPts.epsg)
        
        mmxConfig.setUlx(bbox.getUlx())
        mmxConfig.setUly(bbox.getUly())
        mmxConfig.setLrx(bbox.getLrx())
        mmxConfig.setLry(bbox.getLry())
        mmxConfig.setEPSG(bbox.getEpsg())

        super(ConfigureMmxRun, self).__init__(mmxConfig, 
                                              'ConfigureMmxRun', 
                                              logger)
                                         
        # Log what we have so far.
        self.logHeader()
        self.logger.info(str(self.config))
        
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'configure'
            
#-------------------------------------------------------------------------------
# main
#
# 1.  ./configureMmxRun.py -f /Users/a/Desktop/SystemTesting/GSENM/CSV_Field_Data/GSENM_cheat_pres_abs_2001.csv --startDate 1-1-2016 --endDate 3-2-2016 -o ~/Desktop/SystemTesting/Mmx -s 'cheatgrass'
# 2.  getMerra
# 3.  prepareImages
# 4.  prepareTrials
# 5.  runTrials.py 
# 6.  ./selector.py
# 7.  ./modeler.py 
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application creates and initializes a configuration file ' + \
           'for a MERRA/Max run.'

    parser = argparse.ArgumentParser(description = desc)
    
    parser.add_argument('-f',
                        required = True, 
                        help = 'path to file of presence points')
    
    parser.add_argument('-i', default = '.', help = 'path to input directory')
    parser.add_argument('-o', default = '.', help = 'path to output directory')
    
    parser.add_argument('-p', 
                        default = 10, 
                        type = int,
                        help = 'number of concurrent processes to run')
    
    parser.add_argument('-s',
						required = True,
                        help = 'species name')
    
    parser.add_argument('-t',
                        default = 10,
                        type = int,
                        help='number of trials for selecting top-ten predictors')
    
    parser.add_argument('--startDate', help = 'MM-DD-YYYY')
    parser.add_argument('--endDate', help = 'MM-DD-YYYY')

    args = parser.parse_args()
    
    ConfigureMmxRun(args.f, args.startDate, args.endDate, args.s, args.i, 
                    args.o, args.p, args.t)
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())
        
    
