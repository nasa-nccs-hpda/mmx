
from datetime import datetime
import json
import os

from osgeo import ogr
    
#-------------------------------------------------------------------------------
# class MmxConfig
#
# http://gdal.org/python/
#
# MERRA-Max requires:  Java JDK, GDAL
#-------------------------------------------------------------------------------
class MmxConfig(object):

    DATE_FORMAT = '%m-%d-%Y'
    
    STATES = {'PENDING' : 'Pending', 
              'RUNNING' : 'Running', 
              'COMPLETE': 'Complete', 
              'FAILED'  : 'Failed'}

    CONFIG_FILE_KEY  = 'configFile'
    END_DATE_KEY     = 'endDate'
    EPSG_KEY         = 'epsg'
    IN_DIR_KEY       = 'inputDirectory'
    LRX_KEY          = 'lrx'
    LRY_KEY          = 'lry'
    NUM_PROCS_KEY    = 'numProcesses'
    NUM_TRIALS_KEY   = 'numTrials'
    OUT_DIR_KEY      = 'outputDirectory'
    PHASE_KEY        = 'phase'
    PRES_FILE_KEY    = 'presenceFile'
    SPECIES_KEY      = 'species'
    START_DATE_KEY   = 'startDate'
    STATE_KEY        = 'state'
    TOP_TEN_KEY      = 'topTen'
    ULX_KEY          = 'ulx'
    ULY_KEY          = 'uly'
    
    DEFAULT_PROCESSES = 10
    DEFAULT_TRIALS    = 10
    MAXIMUM_PROCESSES = 2000
    MAXIMUM_TRIALS    = 10000

    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):

        self.phase = 'Unknown'
        self.setStatePending()
        self.configFile = None

        self.numProcesses = MmxConfig.DEFAULT_PROCESSES
        self.numTrials    = MmxConfig.DEFAULT_TRIALS
        
        self.startDate    = None
        self.endDate      = None
        
        self.inDir        = '.'
        self.outDir       = '.'
        
        self.presFile     = None
        self.species      = 'species'
        
        self.ulx          = None
        self.uly          = None
        self.lrx          = None
        self.lry          = None
        self.epsg         = None
        
        self.topTen       = None

    #---------------------------------------------------------------------------
    # fromDict
    #---------------------------------------------------------------------------
    def fromDict(self, inDict):
        
        self.configFile = inDict[MmxConfig.CONFIG_FILE_KEY]
        self.setEndDate(inDict[MmxConfig.END_DATE_KEY])
        self.setEPSG(inDict[MmxConfig.EPSG_KEY])
        self.setInDir(inDict[MmxConfig.IN_DIR_KEY])
        self.setLrx(inDict[MmxConfig.LRX_KEY])
        self.setLry(inDict[MmxConfig.LRY_KEY])
        self.setNumProcs(inDict[MmxConfig.NUM_PROCS_KEY])
        self.setNumTrials(inDict[MmxConfig.NUM_TRIALS_KEY])
        self.setOutDir(inDict[MmxConfig.OUT_DIR_KEY])
        self.phase = inDict[MmxConfig.PHASE_KEY]
        self.setPresFile(inDict[MmxConfig.PRES_FILE_KEY])
        self.setSpecies(inDict[MmxConfig.SPECIES_KEY])
        self.setStartDate(inDict[MmxConfig.START_DATE_KEY])
        self.state = inDict[MmxConfig.STATE_KEY]
        self.topTen = inDict[MmxConfig.TOP_TEN_KEY]
        self.setUlx(inDict[MmxConfig.ULX_KEY])
        self.setUly(inDict[MmxConfig.ULY_KEY])

    #---------------------------------------------------------------------------
    # getConfigFile
    #---------------------------------------------------------------------------
    def getConfigFile(self):
        return self.configFile
        
    #---------------------------------------------------------------------------
    # initializeFromFile
    #---------------------------------------------------------------------------
    def initializeFromFile(self, inFile):

        with open(inFile, 'r') as f:

            jsonStr = f.read()
            jsonConfig = json.loads(jsonStr)
            self.fromDict(jsonConfig)
        
    #---------------------------------------------------------------------------
    # initializeFromValues
    #---------------------------------------------------------------------------
    def initializeFromValues(self, presFile, startDate, endDate, species,
							 inDir, outDir, numProcs, numTrials):
                             
        self.setNumProcs(numProcs)
        self.setNumTrials(numTrials)
        self.setStartDate(startDate)
        self.setEndDate(endDate)
        self.setInDir(inDir)
        self.setOutDir(outDir)
        self.setPresFile(presFile)
        self.setSpecies(species)
        
    #---------------------------------------------------------------------------
    # setEndDate
    #---------------------------------------------------------------------------
    def setEndDate(self, inDate):

        if inDate != None:
            
            self.endDate = \
                datetime.strptime(inDate, MmxConfig.DATE_FORMAT).date()  
                
            if self.startDate != None and self.endDate < self.startDate:      
                raise RuntimeError('Start date must be before end date.')

    #---------------------------------------------------------------------------
    # setEPSG
    #---------------------------------------------------------------------------
    def setEPSG(self, epsg):
    
        if not epsg:
            return
            
        # Store just the integer.  Check for a string.
        try:
            intEpsg = int(epsg)
            
        except ValueError:
            intEpsg = int(epsg.split(':')[1])
            
        self.epsg = intEpsg
            
    #---------------------------------------------------------------------------
    # setInDir
    #---------------------------------------------------------------------------
    def setInDir(self, inDir):
        
        if not inDir or not os.path.exists(inDir) or \
           not os.path.isdir(inDir):
           
            raise RuntimeError('A valid input directory is required.')
            
        self.inDir = inDir
        
    #---------------------------------------------------------------------------
    # setLrx
    #---------------------------------------------------------------------------
    def setLrx(self, lrx):
        
        if lrx != None:
            
            lrx = float(lrx)
            
            if self.ulx != None and self.ulx >= lrx:
                raise RuntimeError('Lower-right X must be less than '
                                   'upper-left X.')  
                                   
            self.lrx = lrx
        
    #---------------------------------------------------------------------------
    # setLry
    #---------------------------------------------------------------------------
    def setLry(self, lry):
        
        if lry != None:
            
            lry = float(lry)
            
            if self.uly != None and self.uly <= lry:
                raise RuntimeError('Lower-right Y must be less than '
                                   'upper-left Y.')  
                                   
            self.lry = lry
        
    #---------------------------------------------------------------------------
    # setNumProcs
    #---------------------------------------------------------------------------
    def setNumProcs(self, numProcs):
        
        if numProcs > 0 and numProcs < MmxConfig.MAXIMUM_PROCESSES:
            self.numProcesses = numProcs
        
    #---------------------------------------------------------------------------
    # setNumTrials
    #---------------------------------------------------------------------------
    def setNumTrials(self, numTrials):
        
        if numTrials > 0 and numTrials < MmxConfig.MAXIMUM_TRIALS:
            self.numTrials = numTrials
        
    #---------------------------------------------------------------------------
    # setOutDir
    #---------------------------------------------------------------------------
    def setOutDir(self, outDir):
        
        if not outDir or not os.path.exists(outDir) or \
           not os.path.isdir(outDir):
           
            raise RuntimeError('A valid output directory is required.')
            
        self.outDir = outDir
        
    #---------------------------------------------------------------------------
    # setPresFile
    #---------------------------------------------------------------------------
    def setPresFile(self, presFile):
        
        if not presFile:
            print 'MmxConfig.setPresFile: presFile is None'
            return
            # raise RuntimeError('A presence point file is required.')

        BASE_MSG = 'Presence point file, ' + str(presFile) + ', '
        
        if not os.path.exists(presFile):
            raise RuntimeError(BASE_MSG + 'does not exist.')

        if not os.path.isfile(presFile):
            raise RuntimeError(BASE_MSG + 'must be a file.')

        if os.path.splitext(presFile)[1].lower() != '.csv':
            raise RuntimeError(BASE_MSG + 'must be a CSV file.')
            
        self.presFile = presFile
        
    #---------------------------------------------------------------------------
    # setSpecies
    #---------------------------------------------------------------------------
    def setSpecies(self, species):
        
        if not species:
			raise RuntimeError('A species must be provided.')
			
        self.species = species
        
    #---------------------------------------------------------------------------
    # setStartDate
    #---------------------------------------------------------------------------
    def setStartDate(self, inDate):
        
        if inDate != None:

            self.startDate = \
                datetime.strptime(inDate, MmxConfig.DATE_FORMAT).date()
        
            if self.endDate != None and self.startDate > self.endDate:
                raise RuntimeError('Start date must be before end date.')

    #---------------------------------------------------------------------------
    # setStateComplete
    #---------------------------------------------------------------------------
    def setStateComplete(self):
        self.state = MmxConfig.STATES['COMPLETE']
        
    #---------------------------------------------------------------------------
    # setStateFailed
    #---------------------------------------------------------------------------
    def setStateFailed(self):
        self.state = MmxConfig.STATES['FAILED']
        
    #---------------------------------------------------------------------------
    # setStatePending
    #---------------------------------------------------------------------------
    def setStatePending(self):
        self.state = MmxConfig.STATES['PENDING']
        
    #---------------------------------------------------------------------------
    # setStateRunning
    #---------------------------------------------------------------------------
    def setStateRunning(self):
        self.state = MmxConfig.STATES['RUNNING']

    #---------------------------------------------------------------------------
    # setUlx
    #---------------------------------------------------------------------------
    def setUlx(self, ulx):
        
        if ulx != None:
            
            ulx = float(ulx)
            
            if self.lrx != None and self.lrx <= ulx:
                raise RuntimeError('Lower-right X must be greater than '
                                   'upper-left X.')  
                                   
            self.ulx = ulx
        
    #---------------------------------------------------------------------------
    # setUly
    #---------------------------------------------------------------------------
    def setUly(self, uly):
        
        if uly != None:
            
            uly = float(uly)
            
            if self.lry != None and self.lry >= uly:
                raise RuntimeError('Upper-left Y must be greater than '
                                   'lower-right Y.')  
                                   
            self.uly = uly
        
    #---------------------------------------------------------------------------
    # toDict
    #---------------------------------------------------------------------------
    def toDict(self):
        
        startDate = None
        endDate   = None

        if self.startDate != None:
            startDate = self.startDate.strftime(MmxConfig.DATE_FORMAT)
            
        if self.endDate != None:
            endDate = self.endDate.strftime(MmxConfig.DATE_FORMAT)
            
        return {MmxConfig.CONFIG_FILE_KEY  : self.configFile,
                MmxConfig.END_DATE_KEY     : endDate,
                MmxConfig.EPSG_KEY         : self.epsg,
                MmxConfig.LRX_KEY          : self.lrx,
                MmxConfig.LRY_KEY          : self.lry,
                MmxConfig.NUM_PROCS_KEY    : self.numProcesses,
                MmxConfig.NUM_TRIALS_KEY   : self.numTrials,
                MmxConfig.IN_DIR_KEY       : self.inDir,
                MmxConfig.OUT_DIR_KEY      : self.outDir,
                MmxConfig.PHASE_KEY        : self.phase,
                MmxConfig.PRES_FILE_KEY    : self.presFile,
                MmxConfig.SPECIES_KEY      : self.species,
                MmxConfig.START_DATE_KEY   : startDate,
                MmxConfig.STATE_KEY        : self.state,
                MmxConfig.TOP_TEN_KEY      : self.topTen,
                MmxConfig.ULX_KEY          : self.ulx,
                MmxConfig.ULY_KEY          : self.uly}
                      
    #---------------------------------------------------------------------------
    # __str__
    #---------------------------------------------------------------------------
    def __str__(self):
        
        startDate = None
        endDate   = None

        if self.startDate != None:
            startDate = self.startDate.strftime(MmxConfig.DATE_FORMAT)
            
        if self.endDate != None:
            endDate = self.endDate.strftime(MmxConfig.DATE_FORMAT)
            
        msg = 'Species:          ' + str(self.species) + '\n' + \
              'Area of Interest: ' + \
              '(' + str(self.ulx) + ', ' + str(self.uly) + '), ' + \
              '(' + str(self.lrx) + ', ' + str(self.lry) + ')\n' + \
              'Dates:            ' + str(startDate) + ' - ' + \
              str(endDate) + '\n' + \
              'Input Directory: ' + str(self.inDir) + '\n' + \
              'Output Directory: ' + str(self.outDir) + '\n' + \
              'Trials:           ' + str(self.numTrials)
        
        return msg
        
    #---------------------------------------------------------------------------
    # write
    #---------------------------------------------------------------------------
    def write(self):
        
        configFile = os.path.join(self.outDir, 'config.mmx')
        
        with open(configFile, 'w') as f:

            self.configFile = configFile
            f.write(json.dumps(self.toDict(), indent = 0)) #indent pretty prints
            
        
        