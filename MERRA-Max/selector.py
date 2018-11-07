#!/usr/bin/python

import argparse
import csv
import glob
import os
import sys

from MmxApplication import MmxApplication
from MmxConfig import MmxConfig

#-------------------------------------------------------------------------------
# class Selector
#-------------------------------------------------------------------------------
class Selector(MmxApplication):
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, configFile, logger = None):
        
        mmxConfig = MmxConfig()
        mmxConfig.initializeFromFile(configFile)
        super(Selector, self).__init__(mmxConfig, 'Selector', logger)
    
        self.logHeader()
    
    #---------------------------------------------------------------------------
    # compileContributions
    #---------------------------------------------------------------------------
    def compileContributions(self):
        
        #---
        # Loop through the trials creating a dictionary like:
        # {predictor: [contribution, contribution, ...],
        #  predictor: [contribution, contribution, ...]} 
        #---
        contributions = {}
        allTrialDirs  = glob.glob(os.path.join(self.trialsDir, 'trial-*'))
        CONTRIB_KWD   = 'permutation'
        
        for trialDir in allTrialDirs:
            
            resultsFile = os.path.join(trialDir, 'results/maxentResults.csv')
            results     = csv.reader(open(resultsFile))
            header      = results.next()

            for row in results:

                rowDict = dict(zip(header, row))
                
                for key in rowDict.iterkeys():
                    
                    if CONTRIB_KWD in key:
                        
                        newKey = key.split(CONTRIB_KWD)[0].strip()
                        
                        if newKey not in contributions:
                            contributions[newKey] = []

                        contributions[newKey].append(float(rowDict[key]))

        return contributions
        
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'SELECTOR'

    #---------------------------------------------------------------------------
    # run
    #---------------------------------------------------------------------------
    def run(self):
        
        contributions = self.compileContributions()
        
        averages = {}
        
        for key in contributions.iterkeys():
            
            samples = contributions[key]
            averages[key] = float(sum(samples) / max(len(samples), 1))
            
        sortedAvgs = sorted(averages.items(), 
                            key = lambda x:x[1], 
                            reverse = True)[:10]
                            
        self.config.topTen = [k for k, v in sortedAvgs]
        
        topTen = []
        
        for k, v in sortedAvgs:
            
            pred = os.path.join(self.config.inDir,
                                'FINISHED',
                                'asc',
                                k + '.asc')
                                
            topTen.append(pred)
            
        self.config.topTen = topTen
        self.config.write()

        if self.logger:

            self.logger.info('Sorted predictors: ' + str(sortedAvgs))
            self.logger.info('Top ten: ' + str(self.config.topTen))

#-------------------------------------------------------------------------------
# main
#
# 1.  configureMmxRun
# 2.  getMerra
# 3.  prepareImages
# 4.  prepareTrials
# 5.  ./runTrials.py 
# 6.  ./selector.py -c ~/Desktop/SystemTesting/Mmx/config.mmx
# 7.  ./modeler.py 
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application the top ten predictors from the trials.'
    parser = argparse.ArgumentParser(description = desc)
    
    parser.add_argument('-c',
                        required = True, 
                        help = 'Path to MERRA-Max configuration file')
    
    args = parser.parse_args()
    selector = Selector(args.c)
    selector.run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())


