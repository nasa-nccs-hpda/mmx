#!/usr/bin/python

import argparse
import csv
import glob
import os
import random
import shutil
import sys

from MaxEntHelper import MaxEntHelper
from MmxApplication import MmxApplication
from MmxConfig import MmxConfig

#-------------------------------------------------------------------------------
# class PrepareTrials
#-------------------------------------------------------------------------------
class PrepareTrials(MmxApplication):
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, configFile, logger = None):
        
        mmxConfig = MmxConfig()
        mmxConfig.initializeFromFile(configFile)
        super(PrepareTrials, self).__init__(mmxConfig, 'PrepareTrials', logger)
    
        self.logHeader()

    #---------------------------------------------------------------------------
    # generateFileIndexes
    #---------------------------------------------------------------------------
    def generateFileIndexes(self, maxIndex):
        
        listOfIndexLists = []
        PREDICTORS_PER_TRIAL = 10
        
        for i in range(1, self.config.numTrials + 1):
            
            listOfIndexLists.append(random.sample(range(0, maxIndex - 1), 
                                                  PREDICTORS_PER_TRIAL))
        
        return listOfIndexLists
        
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'PREPARE_TRIALS'

    #---------------------------------------------------------------------------
    # removeAbsencePoints
    #---------------------------------------------------------------------------
    def removeAbsencePoints(self):
        
        #---
        # Copy the field data file to the config's output directory, and update
        # the configuration.  Do not alter the original field data.
        #---
        if self.logger:
            
            self.logger.info('Copying field data file for MERRA/Max run.')
            self.logger.info('Removing absence points from field data.')
            
        baseName = os.path.basename(self.config.presFile)
        localPresFile = os.path.join(self.config.outDir, baseName)
        
        if self.config.presFile != localPresFile:

            shutil.copy(self.config.presFile, localPresFile)
            self.config.setPresFile(localPresFile)
            self.config.write()
        
        # Create a temporary presence file, while we remove absence points.
        tempPresFile = os.path.splitext(self.config.presFile)[0] + '-temp.csv'
        shutil.move(self.config.presFile, tempPresFile)

        with open(tempPresFile) as inFile:
            with open(self.config.presFile, 'w') as outFile:
            
                reader = csv.reader(inFile,  delimiter = ',')
                writer = csv.writer(outFile, delimiter = ',')
                first  = True
            
                for row in reader: 

                    if first:
                    
                        first = False
                        writer.writerow(row)
                    
                    else:
                    
                        if float(row[2]) == 1.0:
                            writer.writerow(row)
                                             
        os.remove(tempPresFile)
        
    #---------------------------------------------------------------------------
    # run
    #---------------------------------------------------------------------------
    def run(self):
        
        # Get a list of the predictors.
        tifFiles = glob.glob(os.path.join(self.finishedDir, '*.tif'))
        
        # Generate lists of random indexes in the files.
        trialConstituents = self.generateFileIndexes(len(tifFiles))

        if not os.path.exists(self.trialsDir):
            os.mkdir(self.trialsDir)

        # Remove absence points.
        self.removeAbsencePoints()
            
        # Run MaxEnt for each trial constituent.
        for i in range(len(trialConstituents)):
            
            # Create a directory for this trial.
            TRIAL_NAME = 'trial-' + str(i)
            TRIAL_DIR  = os.path.join(self.trialsDir, TRIAL_NAME)
            
            if not os.path.exists(TRIAL_DIR):
                os.mkdir(TRIAL_DIR)
            
            if self.logger:
                self.logger.info('\nPreparing ' + TRIAL_NAME)

            # Get this trial's constituents.
            constituents    = trialConstituents[i]
            trialPredictors = [tifFiles[c] for c in constituents]
            
            if self.logger:
                
                baseNames = [str(os.path.basename(t)) for t in trialPredictors]
                self.logger.info('Trial predictors: ' + str(baseNames))
                
            # Set the state to pending.
            os.system('touch "' + \
                      os.path.join(TRIAL_DIR, MmxApplication.PENDING_FILE) + \
                      '"')
            
            # Create the field data samples file for the trial.
            samplesFile = MaxEntHelper.createSamplesFile(self.config.presFile, 
                                                         self.config.species, 
                                                         TRIAL_DIR)

            if self.logger:
                self.logger.info('Created samples file ' + str(samplesFile))
            
            # Copy the ASC files to the trial.
            ascDir = os.path.join(TRIAL_DIR, 'asc')
            
            if not os.path.exists(ascDir):
                os.mkdir(ascDir)
            
            MaxEntHelper.copyAscFiles(trialPredictors, ascDir)
            
#-------------------------------------------------------------------------------
# main
#
# 1.  configureMmxRun
# 2.  getMerra
# 3.  prepareImages
# 4.  ./prepareTrials.py -c ~/Desktop/SystemTesting/Mmx/config.mmx
# 5.  runTrials.py 
# 6.  ./selector.py
# 7.  ./modeler.py 
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application prepares the trials for a MERRA/Max run.'

    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument('-c',
                        required = True, 
                        help='path to MERRA-Max configuration file')
    
    args = parser.parse_args()
    
    prepTrials = PrepareTrials(args.c)
    prepTrials.run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())


