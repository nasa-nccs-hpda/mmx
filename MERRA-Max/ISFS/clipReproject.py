#!/usr/bin/python

import glob
import os
import sys

import gdal
from gdalconst import *

from osgeo.osr import CoordinateTransformation
from osgeo.osr import SpatialReference

#-------------------------------------------------------------------------------
# clipReprojDir
#-------------------------------------------------------------------------------
def clipReprojDir(sourceDir, destDir, destEPSG, ulx, uly, lrx, lry, clipEPSG):
    
    result    = True
    sourceDir = os.path.expanduser(sourceDir)
    destDir   = os.path.expanduser(destDir)
    validateDirs(sourceDir, destDir)
    
    # Clip and reproject each source image.
    sourceImages = glob.glob(os.path.join(sourceDir, '*.tif'))

    for image in sourceImages:
        
        inPath, inFile = os.path.split(image)
        dest = os.path.join(destDir, inFile)

        clipReprojFile(image, dest, destEPSG, ulx, uly, lrx, lry, clipEPSG)

#-------------------------------------------------------------------------------
# clipReprojFile
#-------------------------------------------------------------------------------
def clipReprojFile(sourceFile, destFile, destEPSG, \
                   ulx, uly, lrx, lry, clipEPSG):

    print 'Clipping and reprojecting ' + str(sourceFile)
    
    if not 'EPSG' in destEPSG:
        destEPSG = 'EPSG:' + str(destEPSG)

    if not 'EPSG' in clipEPSG:
        clipEPSG = 'EPSG:' + str(clipEPSG)

    cmd = 'gdalwarp -multi ' + \
          '-t_srs "'         + \
          destEPSG + '" "'   + \
          sourceFile + '" "' + \
          destFile + '" '    + \
          '-te_srs "'        + \
          clipEPSG + '" '    + \
          '-te '             + \
          str(ulx) + ' '     + \
          str(lry) + ' '     + \
          str(lrx) + ' '     + \
          str(uly) + ' '

    print cmd
    result = os.system(cmd)

    # Get the spatial reference of the source file.
    # dataset    = gdal.Open(sourceFile, GA_ReadOnly )
    # sourceProj = dataset.GetProjection()
    # sourceSR   = SpatialReference()
    # sourceSR.ImportFromWkt(sourceProj)
    #
    # clipSR = SpatialReference()
    # clipSR.ImportFromEPSG(int(clipEPSG))
    #
    # destSR = SpatialReference()
    # destSR.ImportFromEPSG(int(destEPSG))
    #
    # Transform the clip coordinates, if necessary.
    # xformUl = [ulx, uly]
    # xformLr = [lrx, lry]
    #
    # if not sourceSR.IsSame(clipSR):
    #
    #     xform   = CoordinateTransformation(clipSR, sourceSR)
    #     xformUl = xform.TransformPoint(ulx, uly)
    #     xformLr = xform.TransformPoint(lrx, lry)
    #
    #---
    # Clip first then reproject, to avoid reprojecting more pixels than
    # necessary.  Reproject the clip coordinates to the source EPSG, if needed.
    #---
    # name, ext = os.path.splitext(destFile)
    # clipFile = name + '-clip' + ext
    # clip(xformUl[0], xformUl[1], xformLr[0], xformLr[1], sourceFile, clipFile)
    #
    # # Reproject, if necessary.
    # destSR = SpatialReference()
    # destSR.ImportFromEPSG(int(destEPSG))
    #
    # if not sourceSR.IsSame(destSR):
    #
    #   reproj(clipFile, destFile, destEPSG)
    #   os.remove(clipFile)
    #
    # else:
    #   os.rename(clipFile, destFile)

#-------------------------------------------------------------------------------
# clipReprojFile
#-------------------------------------------------------------------------------
# def clipReprojFile(sourceFile, destFile, destEPSG, \
#                  ulx, uly, lrx, lry, clipEPSG):
#
#   print 'Clipping and reprojecting ' + str(sourceFile)
#
#   # Get the spatial reference of the source file.
#   dataset    = gdal.Open(sourceFile, GA_ReadOnly )
#   sourceProj = dataset.GetProjection()
#   sourceSR   = SpatialReference()
#   sourceSR.ImportFromWkt(sourceProj)
#
#   # Reproject, if necessary.
#   destSR = SpatialReference()
#   destSR.ImportFromEPSG(int(destEPSG))
#
#   name, ext = os.path.splitext(destFile)
#   reprojFile = name + '-reproj' + ext
#
#   if not sourceSR.IsSame(destSR):
#       reproj(sourceFile, reprojFile, destEPSG)
#
#   else:
#       reprojFile = sourceFile
#
#   # Get the spatial reference of the clip coordinates.
#   clipSR = SpatialReference()
#   clipSR.ImportFromEPSG(int(clipEPSG))
#
#   # Transform the clip coordinates, if necessary.
#   xformUl = [ulx, uly]
#   xformLr = [lrx, lry]
#
#   if not destSR.IsSame(clipSR):
#
#       xform   = CoordinateTransformation(clipSR, destSR)
#       xformUl = xform.TransformPoint(ulx, uly)
#       xformLr = xform.TransformPoint(lrx, lry)
#
#   # Clip
#   clip(xformUl[0], xformUl[1], xformLr[0], xformLr[1], reprojFile, destFile)
#   os.remove(reprojFile)
    
#-------------------------------------------------------------------------------
# clip
# gdal requires source != dest
#-------------------------------------------------------------------------------
def clip(ulx, uly, lrx, lry, source, dest):
    
    # gdal_translate -projwin -77 39.5 -76 38.4 01ndvi_greenup_avg.tif 07clip.tif
    print "Clipping..."
    cmd = "gdal_translate -projwin " + str(ulx) + " " + str(uly) + " " + str(lrx) + " " + str(lry) + " " + source + " " + dest
    print cmd
    sys.stdout.flush()
    result = os.system(cmd)
    
    if result != 0: return False;
    
    # Check for the output file, ensuring gdal_translate succeeded.
    if not os.path.exists(dest):
        
        print "gdal_translate did not produce output.  The command was " + cmd
        return False
    
    return True

#-------------------------------------------------------------------------------
# reproj
# gdal requires source != dest
#-------------------------------------------------------------------------------
def reproj(source, dest, destEPSG):
    
    if not destEPSG:
        raise RuntimeError('A destination EPSG code must be specified.')
    
    print 'Reprojecting...'

    if not ':' in destEPSG:
        destEPSG = 'EPSG:' + str(destEPSG)

    # gdalwarp -t_srs EPSG:26918 07clip.tif 07clip-utm.tif
    cmd = 'gdalwarp -t_srs ' + destEPSG + ' ' + source + ' ' + dest
    print cmd
    sys.stdout.flush()
    result = os.system(cmd)
    
    if result != 0: 
        raise RuntimeError('Command failed: ' + cmd)
    
    # Check for the output file, ensuring gdal_translate succeeded.
    if not os.path.exists(dest):
        
        raise RuntimeError('gdal_translate did not produce output.  ' + \
                           'The command was ' + cmd)

##############################################
# validateDirs
##############################################
def validateDirs(sourceDir, destDir):
    
    if not os.path.exists(sourceDir):
        print "Error:  source directory, " + sourceDir + ", does not exist."
        sys.exit(1)
    
    if not os.path.isdir(sourceDir):
        print "Error:  source directory, " + sourceDir + ", is not a directory."
        sys.exit(1)
    
    if not os.path.exists(destDir):
        print "Error:  destination directory, " + destDir + ", does not exist."
        sys.exit(1)
    
    if not os.path.isdir(destDir):
        print "Error:  destination directory, " + destDir + ", is not a directory."
        sys.exit(1)
    
    if sourceDir == destDir:
        print "GDAL requires that the source directory is different from the destination directory."
        sys.exit(1)

