
import csv
import os

#-------------------------------------------------------------------------------
# class PresencePoints
#-------------------------------------------------------------------------------
class PresencePoints():

    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, presFile, species):

        self.epsg   = None
        self.points = []
        
        if not species:
            raise RuntimeError('A species is required.')
            
        self.species = species
        
        # Validate the file.
        if not presFile:
            raise RuntimeError('A presence point file is required.')

        BASE_MSG = 'Presence point file, ' + str(presFile) + ', '
        
        if not os.path.exists(presFile):
            raise RuntimeError(BASE_MSG + 'does not exist.')

        if not os.path.isfile(presFile):
            raise RuntimeError(BASE_MSG + 'must be a file.')

        if os.path.splitext(presFile)[1].lower() != '.csv':
            raise RuntimeError(BASE_MSG + 'must be a CSV file.')

        # Read the file.
        with open(presFile) as csvFile:

            fdReader = csv.reader(csvFile, delimiter = ',')
            first = True
            
            for row in fdReader:

                # Find the EPSG code.
                if first:
                    
                    first = False
                    
                    for field in row:
                        if 'epsg' in field:
                            tag, self.epsg = field.split(':')
                            break
                            
                    if self.epsg == None:

                        raise RuntimeError('Points file must contain and EPSG '
                                           'code, like "epsg:4326" in its '
                                           'first row.')
                            
                else:
                    self.points.append((row[0], row[1]))
                    
