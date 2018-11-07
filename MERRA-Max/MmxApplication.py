
import logging
import os

from MmxConfig import MmxConfig

#-------------------------------------------------------------------------------
# class MmxApplication
#-------------------------------------------------------------------------------
class MmxApplication(object):

    COMPLETE_FILE = 'complete.state'
    FAILURE_FILE  = 'failed.state'
    PENDING_FILE  = 'pending.state'
    RUNNING_FILE  = 'running.state'
    
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, mmxConfig, applicationName, logger = None):
        
        self.config = mmxConfig
        self.config.phase = self.getPhase()
        self.config.write()

        if not logger:
            
            logFileName = os.path.join(self.config.outDir, 'mmx.log')
            logging.basicConfig(format = '%(message)s', filename = logFileName)
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

        self.logger = logger
        
        if not applicationName:
            raise RuntimeError('An application name must be provided.')
            
        self.applicationName = applicationName
        self.clipReprojDir   = os.path.join(mmxConfig.inDir,  'CLIP_REPROJ')
        self.finishedDir     = os.path.join(mmxConfig.inDir,  'FINISHED')
        self.merraDir        = os.path.join(mmxConfig.inDir,  'RAW_MERRA')
        self.trialsDir       = os.path.join(mmxConfig.outDir, 'TRIALS')

    #---------------------------------------------------------------------------
    # logHeader
    #---------------------------------------------------------------------------
    def logHeader(self):
        
        self.logger.info('--------------------------------------------------')
        self.logger.info(self.applicationName)
        self.logger.info('--------------------------------------------------')
        
    #---------------------------------------------------------------------------
    # getPhase
    #---------------------------------------------------------------------------
    def getPhase(self):
        raise RuntimeError('This method must be overridden by a subclass.')
        
