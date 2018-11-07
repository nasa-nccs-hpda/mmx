#!/usr/bin/python

import argparse
import glob
import os
import sys
import zipfile

from osgeo import gdal

sys.path.append('/Users/a/Desktop/Source/Recover/RecoverScripts')
import wrangleEmptySite
import wrangleOnePredictor

from MmxApplication import MmxApplication
from MmxConfig import MmxConfig

#-------------------------------------------------------------------------------
# class GetMerra
#-------------------------------------------------------------------------------
class GetMerra(MmxApplication):
    
    USER   = 'wmAdmin'
    KEY    = '13c952ea-9ca6-4248-a6b1-f9af29a1fa37'
    SERVER = 'recoverdss.us'
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, configFile, siteID = None, logger = None):
        
        mmxConfig = MmxConfig()
        mmxConfig.initializeFromFile(configFile)
        super(GetMerra, self).__init__(mmxConfig, 'GetMerra', logger)
    
        self.logHeader()

        # Try to use an existing zip file.
        self.zipFile = None

        zipFiles = glob.glob(os.path.join(self.merraDir, '*.zip'))

        if len(zipFiles) == 1:
            
            self.zipFile = zipFiles[0]
            self.logger.info('Extracting TIFs from ' + str(self.zipFile))
        
        elif len(zipFiles) > 1:
            
            raise RuntimeError('There are multiple zip files available.')

        else:

            self.siteID = siteID

            if self.siteID:
                self.logger.info('Using site: ' + str(self.siteID))
        
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        return 'MERRA'

    #---------------------------------------------------------------------------
    # removeFiller
    #---------------------------------------------------------------------------
    def removeFiller(self):
        
        tifFiles = glob.glob(os.path.join(self.merraDir, '*.tif'))

        if self.logger:
            
            baseNames = [str(os.path.basename(tif)) for tif in tifFiles]
            self.logger.info('\nTIFs: ' + str(baseNames) + '\n')

        for tifFile in tifFiles:
            
            tifImage = gdal.Open(tifFile)
            tifBand  = tifImage.GetRasterBand(1)
            minValue, maxValue, mean, stddev =tifBand.GetStatistics(False, True)
            
            if minValue == maxValue:
                
                msg = 'Removing ' + tifFile + ' because its minimum value = ' +\
                      'maximum value, so it must be entirely comprised of ' + \
                      'filler.  Min = ' + str(minValue) + ', Max = ' + \
                      str(maxValue)
                      
                print msg
                self.logger.warning(msg)

                os.remove(tifFile)
            
    #---------------------------------------------------------------------------
    # run
    #---------------------------------------------------------------------------
    def run(self):
        
        if not os.path.exists(self.merraDir):
            os.mkdir(self.merraDir)
            
        if not self.zipFile:
            
            verbose  = False
        
            if not self.siteID:

                sDateStr = self.config.startDate.strftime('%Y-%m-%d')
                eDateStr = self.config.endDate.strftime('%Y-%m-%d')

                self.siteID = wrangleEmptySite.createEmptySite(self.config.ulx, 
                                                               self.config.uly, 
                                                               self.config.lrx, 
                                                               self.config.lry, 
                                                               self.config.epsg, 
                                                               GetMerra.USER, 
                                                               GetMerra.KEY,
                                                               sDateStr, 
                                                               eDateStr,
                                                               GetMerra.SERVER, 
                                                               verbose)
                                 
                self.logger.info('New site ID: ' + str(self.siteID))

            zipFile = wrangleOnePredictor.wrangle(GetMerra.USER,
                                                  GetMerra.KEY,
                                                  self.siteID, 
                                                  False, # disable GCPC 
                                                  False, # disable Lsat, 
                                                  False, # disable MERRA
                                                  True,  # MERRA All
                                                  False, # disable modis,
                                                  GetMerra.SERVER,
                                                  verbose)
        
            name = os.path.basename(zipFile)
            self.zipFile = os.path.join(self.merraDir, name)                                           
            os.rename(zipFile, self.zipFile)
                                                   
        if self.zipFile:
            
            zf = zipfile.ZipFile(self.zipFile , 'r')
            zf.extractall(self.merraDir)
            
        # Remove images comprised entirely of filler.
        self.removeFiller()
                                        
#-------------------------------------------------------------------------------
# main
#
# 1.  configureMmxRun
# 2.  ./getMerra.py -c ~/Desktop/SystemTesting/Mmx/config.mmx -s 414
# 3.  prepareImages
# 4.  prepareTrials
# 5.  runTrials
# 6.  ./selector.py
# 7.  ./modeler.py 
#-------------------------------------------------------------------------------
def main():

    # Process command-line args. 
    desc = 'This application retrieves MERRA files for a MERRA/Max run.'

    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument('-c',
                        required = True, 
                        help='path to MERRA-Max configuration file')
    
    parser.add_argument('-s',
                        help='site ID of an existing site; use this to continue a site that was already started')
    
    args = parser.parse_args()
    
    gm = GetMerra(args.c, args.s)
    gm.run()
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())

