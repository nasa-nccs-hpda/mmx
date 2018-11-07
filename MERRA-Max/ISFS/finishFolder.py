#!/usr/bin/python

import fileinput
import glob
import math
import os
import shutil
import sys

from   osgeo    import gdalconst
from   osgeo    import gdal
from   optparse import OptionParser

from tif2asc    import *

nodata = -9999.0

##############################################
# main
#
# To install the GDAL Python bindings:  "sudo easy_install GDAL"
##############################################
def main():
	####
	# Process command-line args.  OptionParser treats negative numbers as options.  The way around this is to not
	# use positional arguments, giving them all flags instead.
	####
	usageStmt = "usage:  %prog [options]  <inputDirectory> <outputDirectory>"
	desc = "This application resamples the input directory such that the result has square pixels and the same extent and resolution."
	
	parser = OptionParser(usage=usageStmt, description=desc)
	(options, args) = parser.parse_args()
    
	if len(args) < 2:
		print "Input and output directories must be specified."
		sys.exit(1)
    
	resampleForTemplate(args[0], args[1])	
	ascDir = createAsc(args[1])
	fixAscNan(ascDir)

##############################################
# resampleForTemplate
##############################################
def resampleForTemplate(inDir, outDir):
    
	print "Resampling for the image with the largest resolution..."
	sys.stdout.flush()
    
	# Validate input.
	if not os.path.exists(inDir):
		print "Input directory, " + inDir + ", does not exist."
		sys.exit(1)
    
	if not os.path.exists(outDir):
		print "Input directory, " + outDir + ", does not exist."
		sys.exit(1)
    
	# Find the largest resolution.
	sourceImages = glob.glob(inDir + "/*.tif")
	if len(sourceImages) == 0:
		print "There are no images in " + inDir
		sys.exit(1)
    
	templateImage = getAnyImageWithLargestResolution(sourceImages)
	
	# Square the pixels.
	ulx, uly, lrx, lry, xScale, yScale = getSquareScale(templateImage)
	
	# Resample the directory.
	resampleDir(inDir, outDir, ulx, uly, lrx, lry, xScale, yScale)

##############################################
# getAnyImageWithLargestResolution
##############################################
def getAnyImageWithLargestResolution(sourceImages):
    
	print "Finding image with the largest resolution..."
	sys.stdout.flush()
	
	maxScale = -1.0
	templateImage = None
	
	for inFile in sourceImages:
        
		dataset = gdal.Open(inFile, gdalconst.GA_ReadOnly)
		if dataset is None:
			print "Unable to open " + inFile
			sys.exit(1)
        
		# Get the basics.
		xform  = dataset.GetGeoTransform()
		xScale = xform[1]
		yScale = xform[5]
		
		if math.fabs(xScale) > maxScale:
            
			maxScale = math.fabs(xScale)
			templateImage = inFile
        
		if math.fabs(yScale) > maxScale:
            
			maxScale = math.fabs(yScale)
			templateImage = inFile
	
	return templateImage

##############################################
# resampleDir
##############################################
def resampleDir(inDir, outDir, ulx, uly, lrx, lry, xScale, yScale):
    
	# Get the images.
	sourceImages = glob.glob(inDir + "/*.tif")
	if len(sourceImages) == 0:
		print "There are no images in " + inDir
		sys.exit(1)
    
	# Resample each source image. 
	for inFile in sourceImages:
        
		inPath, inFileNoPath = os.path.split(inFile)
		outFile = outDir + "/" + inFileNoPath
		
		resampleFile(inFile, outFile, ulx, uly, lrx, lry, xScale, yScale)

##############################################
# resampleFile
##############################################
def resampleFile(inFile, outFile, ulx, uly, lrx, lry, xScale, yScale):
    
	print "Resampling..."
	sys.stdout.flush()
    
	cmd = 'gdalwarp -te ' + str(ulx) + ' ' + str(lry) + ' ' + str(lrx) + ' ' + str(uly) + ' -tr ' + str(xScale) + ' ' + str(yScale) + ' "' + inFile + '" "' + outFile + '"'
	status = os.system(cmd)

	# Check for the output file, ensuring gdal_translate succeeded.
	if not os.path.exists(outFile):
		print "gdalwarp did not produce output.  The command was " + cmd
		return False
	else:
		return True

#############################################
# getSquareScale
#############################################
def getSquareScale(inFile):
    
	print "Computing square pixel parameters..."
	sys.stdout.flush()
    
	# Open the input file.
	dataset = gdal.Open(inFile, gdalconst.GA_ReadOnly)
	if dataset is None:
		print "Unable to open " + inFile
		sys.exit(1)
    
	# Get the basics.
	xform  = dataset.GetGeoTransform()
	xScale = xform[1]
	yScale = xform[5]
	width  = dataset.RasterXSize
	height = dataset.RasterYSize
	ulx = xform[0]
	uly = xform[3]	
	lrx = ulx + width  * xScale
	lry = uly + height * yScale
    
	if math.fabs(xScale) > math.fabs(yScale):
		yScale = xScale * -1	# xScale is bigger, so make yScale bigger
	else:
		xScale = yScale	* -1

	return ulx, uly, lrx, lry, xScale, yScale

##############################################
# Invoke the main
##############################################
if __name__ == "__main__":
	sys.exit(main())
