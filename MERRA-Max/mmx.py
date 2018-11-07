#!/usr/bin/python

import argparse
import os
import sys

from configureMmxRun import ConfigureMmxRun
from getMerra        import GetMerra
from prepareImages   import PrepareImages
from prepareTrials   import PrepareTrials
from runTrials       import RunTrials
from selector        import Selector
from modeler         import Modeler

#-------------------------------------------------------------------------------
# main
#
# ./mmx.py -f /Users/a/Desktop/SystemTesting/GSENM/CSV_Field_Data/GSENM_cheat_pres_abs_2001.csv --startDate 1-1-2016 --endDate 3-2-2016 -o ~/Desktop/SystemTesting/Mmx -s 'cheatgrass'
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application run an end-to-end MERRA/Max process.'

    parser = argparse.ArgumentParser(description = desc)
    
    parser.add_argument('-f',
                        required = True, 
                        help = 'path to file of presence points')
    
    parser.add_argument('-o', default = '.', help = 'path to output directory')
    
    parser.add_argument('-p', 
                        default = 10, 
                        help = 'number of concurrent processes to run')
    
    parser.add_argument('-s',
						required = True,
                        help = 'species name')
    
    parser.add_argument('-t',
                        default = 10,
                        help='number of trials for selecting top-ten predictors')
    
    parser.add_argument('--startDate', help = 'MM-DD-YYYY')
    parser.add_argument('--endDate', help = 'MM-DD-YYYY')

    args = parser.parse_args()
    
    # Run the process.
    c = ConfigureMmxRun(args.f, args.startDate, args.endDate, args.s, args.o, 
                        args.p, args.t)
    
    GetMerra     (c.config.configFile).run()
    PrepareImages(c.config.configFile).run()
    PrepareTrials(c.config.configFile).run()
    RunTrials    (c.config.configFile).run()
    Selector     (c.config.configFile).run()
    Modeler      (c.config.configFile).run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
        
    
