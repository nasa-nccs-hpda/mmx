#!/usr/bin/python

import argparse
import glob
import os
import shutil
import sys

from MaxEntHelper import MaxEntHelper
from MmxApplication import MmxApplication
from MmxConfig import MmxConfig

#-------------------------------------------------------------------------------
# class RunTrials
#
# https://biodiversityinformatics.amnh.org/open_source/maxent/
#-------------------------------------------------------------------------------
class RunTrials(MmxApplication):
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, configFile, trialsToRun = None, logger = None):
        
        mmxConfig = MmxConfig()
        mmxConfig.initializeFromFile(configFile)
        super(RunTrials, self).__init__(mmxConfig, 'RunTrials', logger)
    
        self.logHeader()
        
        # Configure the trials to run.
        self.trialDirs = self.getTrialDirs(trialsToRun)
    
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'RUN_TRIALS'

    #---------------------------------------------------------------------------
    # getTrialDirs
    #---------------------------------------------------------------------------
    def getTrialDirs(self, trialsToRun):
        
        trialDirs = []
        
        if trialsToRun:
            
            startStr, endStr = trialsToRun.split('-')
            start            = int(startStr.strip())
            end              = int(endStr.strip()) + 1
            trialsToRun      = range(start, end)
            
            for trialNum in trialsToRun:
                
                trialDir = os.path.join(self.trialsDir, \
                                        'trial-' + str(trialNum))

                if not os.path.exists(trialDir):
                    
                    raise RuntimeError('Trial directory, ' + \
                                       trialDir + \
                                       ' does not exist.')
                                       
                trialDirs.append(trialDir)
                
        else:
            
            trialDirs = glob.glob(os.path.join(self.trialsDir, 'trial-*'))
            
            if len(trialDirs) == 0:
                raise RuntimeError('No trials found in ' + str(trialDirs))
            
        return trialDirs
            
    #---------------------------------------------------------------------------
    # run
    #---------------------------------------------------------------------------
    def run(self):
        
        speciesFile = os.path.basename(self.config.presFile)
    
        for trialDir in self.trialDirs:

            if os.path.exists(os.path.join(trialDir, \
                              MmxApplication.PENDING_FILE)):
    
                if self.logger:
                    self.logger.info('Running ' + trialDir)
                
                resultsDir = os.path.join(trialDir, 'results')
            
                if not os.path.exists(resultsDir):
                    os.mkdir(resultsDir)
            
                # Set the state to running and remove pending file.
                os.system('touch "' + \
                          os.path.join(trialDir, MmxApplication.RUNNING_FILE) +\
                          '"')
                      
                os.remove(os.path.join(trialDir, MmxApplication.PENDING_FILE))
            
                MaxEntHelper.runMaxEnt(os.path.join(trialDir, speciesFile),
                                       os.path.join(trialDir, 'asc'),
                                       resultsDir,
                                       self.logger)

                # Set the state back to pending.
                os.remove(os.path.join(trialDir, MmxApplication.RUNNING_FILE))

                os.system('touch "' + \
                          os.path.join(trialDir, MmxApplication.PENDING_FILE) +\
                          '"')
            
#-------------------------------------------------------------------------------
# main
#
# 1.  configureMmxRun
# 2.  getMerra
# 3.  prepareImages
# 4.  prepareTrials
# 5.  ./runTrials.py -c ~/Desktop/SystemTesting/Mmx/config.mmx
# 6.  ./selector.py
# 7.  ./modeler.py 
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application runs the trials for a MERRA/Max run.'

    parser = argparse.ArgumentParser(description = desc)
    
    parser.add_argument('-c',
                        required = True, 
                        help = 'Path to MERRA-Max configuration file')
    
    parser.add_argument('--range',
                        help = 'Range of trial numbers to run, like "--range 1-10".  Defaults all trials.')
    
    parser.add_argument('--reset',
                        action = 'store_true', 
                        help = 'Reset trials to be run again.  ' + \
                               'The trials are not run.')
    
    args = parser.parse_args()
    
    # Reset the trials directories, if requested.
    if args.reset:
        
        config = MmxConfig()
        config.initializeFromFile(args.c)
        allTrialDirs = glob.glob(os.path.join(config.outDir, 'TRIALS/trial-*'))

        for trialDir in allTrialDirs:

            try:
                shutil.rmtree(os.path.join(trialDir, 'results'))

            except OSError:
                pass

            os.system('touch ' + \
                      os.path.join(trialDir, MmxApplication.PENDING_FILE))

    else:

        runTrials = RunTrials(args.c, args.range)
        runTrials.run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())


