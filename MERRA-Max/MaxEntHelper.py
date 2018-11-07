
import csv
import os
import shutil

#-------------------------------------------------------------------------------
# class MaxEntHelper
#-------------------------------------------------------------------------------
class MaxEntHelper(object):

    #---------------------------------------------------------------------------
    # copyAscFiles
    #---------------------------------------------------------------------------
    @staticmethod
    def copyAscFiles(predFiles, destDir):
        
        if not destDir:
            raise RuntimeError('A destination directory must be provided.')
        
        if not os.path.exists(destDir):
            raise RuntimeError(destDir + ' does not exist.')
            
        if not os.path.isdir(destDir):
            raise RuntimeError(destDir + ' is not a directory.')
            
        for predFile in predFiles:
            
            # If it is a TIF file, get the ASC version.
            path, name = os.path.split(predFile)
            ascName    = None
            sourceFile = None

            if '.tif' in name:
                
                ascName    = name.replace('.tif', '.asc')
                sourceFile = os.path.join(path, 'asc', ascName)

            else:
                
                ascName    = name
                sourceFile = predFile
                
            destFile = os.path.join(destDir, ascName)
            shutil.copyfile(sourceFile, destFile)
                
    #---------------------------------------------------------------------------
    # createSamplesFile
    #---------------------------------------------------------------------------
    @staticmethod
    def createSamplesFile(fdFile, species, outDir):

        path, name  = os.path.split(fdFile)
        samplesFile = os.path.join(outDir, name)        
        firstRow    = True
        fdReader    = csv.reader(open(fdFile), delimiter = ',')
        
        for row in fdReader:
            
            outRow = []
            
            if firstRow:

                firstRow  = False
                meWriter  = csv.writer(open(samplesFile, 'w'), delimiter = ',')
                meWriter.writerow(['species', 'x', 'y'])
                
            else:
                
                meWriter.writerow([species, row[0], row[1]])

        return samplesFile
        
    #---------------------------------------------------------------------------
    # runMaxEnt
    #---------------------------------------------------------------------------
    @staticmethod
    def runMaxEnt(speciesFile, ascDir, outDir, logger):
        
        if not os.path.exists(speciesFile):

            raise RuntimeError('Species file: ' + str(speciesFile) + \
                               ' does not exist.')

        if not ascDir or not os.path.isdir(ascDir):
            raise RuntimeError('You must provide an ASC directory.')

        if not outDir or not os.path.isdir(outDir):
            raise RuntimeError('You must provide an output directory.')

        maxentJar = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'ISFS',
                                 'maxent.jar')
        
        baseCmd = 'java -Xmx1024m -jar ' + \
                  maxentJar + \
                  ' visible=false autorun -P -J writeplotdata ' + \
                  '"applythresholdrule=Equal training sensitivity and specificity" ' + \
                  'removeduplicates=false '
                  
        cmd = baseCmd + \
              '-s "' + speciesFile + '" ' + \
              '-e "' + ascDir + '" ' + \
              '-o "' + outDir + '"'
        
        if logger:
            logger.info('MaxEnt command: ' + cmd)

        os.system(cmd)
    
