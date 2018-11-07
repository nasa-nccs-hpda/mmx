#!/usr/bin/python

import argparse
import os
import sys

from ISFS import clipReproject
from ISFS import finishFolder
from ISFS.tif2asc import *

from MmxApplication import MmxApplication
from MmxConfig import MmxConfig
from PresencePoints import PresencePoints

#-------------------------------------------------------------------------------
# class PrepareImages
#
# This clips and reprojects the images, then converts them to ASC format.
#-------------------------------------------------------------------------------
class PrepareImages(MmxApplication):
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, configFile, logger = None):
        
        mmxConfig = MmxConfig()
        mmxConfig.initializeFromFile(configFile)
        super(PrepareImages, self).__init__(mmxConfig, 'PrepareImages', logger)
    
        self.logHeader()

    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'PREP_IMAGES'

    #---------------------------------------------------------------------------
    # run
    #---------------------------------------------------------------------------
    def run(self):
        
        # Clip and reproject.
        if self.logger:
            self.logger.info('Clipping and reprojecting to bounding box.')
                             
        presPts = PresencePoints(self.config.presFile, self.config.species)
        
        if not os.path.exists(self.clipReprojDir):
            os.mkdir(self.clipReprojDir)
            
        clipReproject.clipReprojDir(self.merraDir,      \
                                    self.clipReprojDir, \
                                    presPts.epsg,       \
                                    self.config.ulx,    \
                                    self.config.uly,    \
                                    self.config.lrx,    \
                                    self.config.lry,    \
                                    presPts.epsg)
        
        if not os.path.exists(self.finishedDir):
            os.mkdir(self.finishedDir)
            
        # Resample for square pixels.
        if self.logger:
            self.logger.info('Resampling to square pixels.')
            
        finishFolder.resampleForTemplate(self.clipReprojDir, self.finishedDir)

        # Convert to ASC format.
        if self.logger:
            self.logger.info('Converting images to ASC format.')
            
        ascDir = createAsc(self.finishedDir)
        
        # Fix NaNs in ASC files.
        if self.logger:
            self.logger.info('Converting NaNs to the no-data value.')
            
        fixAscNan(ascDir)
        
#-------------------------------------------------------------------------------
# main
#
# 1.  configureMmxRun
# 2.  getMerra
# 3.  ./prepareImages.py -c ~/Desktop/SystemTesting/Mmx/config.mmx
# 4.  prepareTrials
# 5.  runTrials.py 
# 6.  ./selector.py
# 7.  ./modeler.py 
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application clips and reprojects tifs, and creates a set ' + \
           'of ASC images for a MERRA/Max run.'

    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument('-c',
                        required = True, 
                        help='path to MERRA-Max configuration file')
    
    args = parser.parse_args()
    
    prepareImages = PrepareImages(args.c)
    prepareImages.run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())


