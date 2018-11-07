#!/usr/bin/python

import csv
import glob
import os
import shutil
import sys

from osgeo import gdal
from osgeo import gdalconst
from osgeo import gdal_array
from osgeo import osr

from optparse import OptionParser

#-------------------------------------------------------------------------------
# createMDS
#-------------------------------------------------------------------------------
def createMDS(fdFile, imgFiles, catFiles, outFile):
    
    # Read the entire csv file.
    fieldData = readFieldData(fdFile)

    # Loop through image files.
    fieldData = loadValues(imgFiles, fieldData)
    
    # Loop through categorical image files.
    fieldData = loadValues(catFiles, fieldData, True)
    
    # Write the field data
    writeFieldData(fieldData, outFile)

#-------------------------------------------------------------------------------
# getEPSG
#-------------------------------------------------------------------------------
def getEPSG(dataset):
    
    wkt = dataset.GetProjection()
    s_srs = osr.SpatialReference(wkt)
    
    epsg = s_srs.GetAuthorityCode("PROJCS")
    if epsg == None: epsg = s_srs.GetAuthorityCode("GEOGCS")
    
    if epsg == None:
        print "Warning: unable to extract the EPSG code from the image."    
    
    return epsg 

#-------------------------------------------------------------------------------
# groundToImage
#-------------------------------------------------------------------------------
def groundToImage(x, y, coefs):
    
    xOrigin     = coefs[0] 
    yOrigin     = coefs[3] 
    pixelWidth  = coefs[1] 
    pixelHeight = coefs[5] 
    
    xOffset = round(float((x - xOrigin) / pixelWidth))
    yOffset = round(float((y - yOrigin) / pixelHeight))
    
    return [xOffset, yOffset]

#-------------------------------------------------------------------------------
# loadValues
#-------------------------------------------------------------------------------
def loadValues(imgFiles, fieldData, isCategorical = False):
    
    epsg = None
    firstEPSG = None
    
    for imgFile in imgFiles:  
        
        # Open the image.
        dataset = gdal.Open(imgFile, gdalconst.GA_ReadOnly)

        if not dataset: 
            raise RuntimeError('Unable to read ' + imgFile + '.')
        
        # Ensure each image is of the same projection.
        epsg = getEPSG(dataset)
        
        if not firstEPSG:
            
            firstEPSG = epsg
        
        elif epsg != firstEPSG:
            
            raise RuntimeError('Error: image ' + imgFile + \
                               ' has EPSG ' + epsg + \
                               '.  Previous images have EPSG ' + \
                               firstEPSG + '.')
        
        # Load the values for the current image.
        path, fileName = os.path.split(imgFile)
        name, ext = os.path.splitext(fileName)
        if isCategorical:  name = 'categorical:' + name
        fieldData = loadValuesForImage(dataset, fieldData, name)
    
    return fieldData

#-------------------------------------------------------------------------------
# loadValuesForImage
#-------------------------------------------------------------------------------
def loadValuesForImage(dataset, fieldData, predictorName):
        
    # Loop through field data.
    first = True
    
    for row in fieldData:
        
        if first == True:
            
            first = False
            row.append(predictorName)
        
        else:
            
            # Ground to image.
            coefs = dataset.GetGeoTransform()
            x = float(row[0])
            y = float(row[1])
            
            offsets = groundToImage(x, y, coefs)

            # Offsets start at 1, while bands start at 0.
            xOffset = int(offsets[0]) - 1
            yOffset = int(offsets[1]) - 1
            
            band = dataset.GetRasterBand(1)
            data = band.ReadAsArray(xOffset, yOffset, 1, 1)
    
            value = data[0, 0]
            row.append(value)
                    
    return fieldData

#-------------------------------------------------------------------------------
# readFieldData
#-------------------------------------------------------------------------------
def readFieldData(fdFile):
    
    fieldData = []
    fdReader = csv.reader(open(fdFile), delimiter=',')
    # for row in fdReader: fieldData.append(row)
    
    # Omit the response and epsg fields.
    for row in fdReader: fieldData.append([row[0], row[1]])

    return fieldData

#-------------------------------------------------------------------------------
# writeFieldData
#-------------------------------------------------------------------------------
def writeFieldData(fieldData, outFile):
    
    fdWriter = csv.writer(open(outFile, 'w'), delimiter=',')
    for row in fieldData: fdWriter.writerow(row)

