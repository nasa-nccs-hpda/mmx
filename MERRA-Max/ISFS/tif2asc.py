#!/usr/bin/python

import fileinput
import glob
import math
import os
import shutil
import sys

from   optparse import OptionParser

from   osgeo    import gdalconst
from   osgeo    import gdal
	
nodata = -9999.0

##############################################
# main
##############################################
def main():
	####
	# Process command-line args.  OptionParser treats negative numbers as options.  The way around this is to not
	# use positional arguments, giving them all flags instead.
	####
	usageStmt = "usage:  %prog [options]  <inputDirectory | inputFile>"
	desc = "This application converts tifs in the input directory to ASCII/Grid format."
	
	parser = OptionParser(usage=usageStmt, description=desc)
	(options, args) = parser.parse_args()

	if len(args) < 1:
		print "An input file or directory must be specified."
		sys.exit(1)
		
	ascDir = createAsc(args[0])
	if ascDir == None: sys.exit(1)
	
	result = fixAscNan(ascDir)
	
	if result == False: sys.exit(1)
	
##############################################
# fixAscNan
##############################################
def fixAscNan(ascDir):

	print "Converting NaNs to " + str(nodata) + "..."
	
	# Loop through each .asc image, and replace 'nan' with the nodata value.
	if os.path.isdir(ascDir):
	
		ascFiles = glob.glob(ascDir + "/*.asc")

		if len(ascFiles) == 0:
			print "There are no .asc files in " + ascDir
			return False

	else:
	
		ascFiles = ascDir
	
	for line in fileinput.FileInput(ascFiles, inplace = 1):
		line = line.replace("nan", str(nodata))
		print line,

	return True
	
##############################################
# createAsc
##############################################
def createAsc(inDir):

	sourceImages = None
	
	if os.path.isdir(inDir):
	
		if not os.path.exists(inDir):
			print "Input directory, " + inDir + ", does not exist."
			return None

		sourceImages = glob.glob(inDir + "/*.tif")
		if len(sourceImages) == 0:
			print "There are no images in " + inDir
			return None

	else:
	
		fullFileName = inDir
		inDir, inFile = os.path.split(inDir)
		sourceImages = [fullFileName]
		
	# Create a subdirectory for the asc images.
	ascDir = os.path.join(inDir, 'asc')
	if not os.path.exists(ascDir): os.mkdir(ascDir)

	for inFile in sourceImages:

		print "Creating asc image from " + inFile + "..."
		
		path, inFileNameOnly = os.path.split(inFile)
		basename, extension = os.path.splitext(inFileNameOnly)
		
		outFile   = ascDir + "/" + basename + ".asc"
		squareTif = ascDir + "/" + basename + "-squared.tif"
		
		convertFile = inFile
		wasSquared = squarePixels(inFile, squareTif)
		if wasSquared: convertFile = squareTif
		
		cmd = 'gdal_translate -ot Float32 -a_nodata ' + str(nodata) + ' -of AAIGrid "' + convertFile + '" "' + outFile + '"'
		os.system(cmd)
		
		if wasSquared: os.remove(squareTif)
		
		# Check for the output file, ensuring gdal_translate succeeded.
		if not os.path.exists(outFile):
			print "gdal_translate did not produce output.  The command was " + cmd
			return False
			
	return ascDir
		
##############################################
# squarePixels
##############################################
def squarePixels(inFile, outFile):
	
	# Open the input file.
	dataset = gdal.Open(inFile, gdalconst.GA_ReadOnly)
	if dataset is None:
		print "Unable to open " + inFile
		sys.exit(1)

	# Get the basics.
	xform  = dataset.GetGeoTransform()
	xScale = xform[1]
	yScale = xform[5]
	
	if math.fabs(xScale) - math.fabs(yScale) > 0.0000001:
	
		print "Squaring pixels..."
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
			
		cmd	= "gdalwarp -te "  +    \
				str(ulx)    + " " + \
				str(lry)    + " " + \
				str(lrx)    + " " + \
				str(uly)    +       \
				" -tr "     +       \
				str(xScale) + " " + \
				str(yScale) + " " + \
				inFile      + " " + \
				outFile

		os.system(cmd)

		if not os.path.exists(outFile):
			print "gdalwarp did not produce output.  The command was " + cmd
			return False
		
		return True
	
	return False
	
##############################################
# Invoke the main
##############################################
if __name__ == "__main__":
    sys.exit(main())
