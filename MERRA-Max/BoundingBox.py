
from osgeo import ogr
from osgeo.osr import SpatialReference

#-------------------------------------------------------------------------------
# class BoundingBox
#-------------------------------------------------------------------------------
class BoundingBox():

	#---------------------------------------------------------------------------
	# __init__
	#---------------------------------------------------------------------------
	def __init__(self, pointList, epsg):

		crs = SpatialReference()
		crs.ImportFromEPSG(int(epsg))
		
		multipoint = ogr.Geometry(ogr.wkbMultiPoint)
		multipoint.AssignSpatialReference(crs)

		for point in pointList:
			
			ogrPt = ogr.Geometry(ogr.wkbPoint)
			ogrPt.AddPoint(float(point[0]), float(point[1]))
			multipoint.AddGeometry(ogrPt)
			
		self.boundingBox = multipoint.GetEnvelope()
		self.epsg = epsg

	#---------------------------------------------------------------------------
	# getBoundingBox
	#---------------------------------------------------------------------------
	def getBoundingBox(self):
		return self.boundingBox

	#---------------------------------------------------------------------------
	# getEpsg
	#---------------------------------------------------------------------------
	def getEpsg(self):
		return self.epsg
		
	#---------------------------------------------------------------------------
	# getLrx
	#---------------------------------------------------------------------------
	def getLrx(self):
		return self.getBoundingBox()[1]
		
	#---------------------------------------------------------------------------
	# getLry
	#---------------------------------------------------------------------------
	def getLry(self):
		return self.getBoundingBox()[2]
				
	#---------------------------------------------------------------------------
	# getUlx
	#---------------------------------------------------------------------------
	def getUlx(self):
		return self.getBoundingBox()[0]
		
	#---------------------------------------------------------------------------
	# getUly
	#---------------------------------------------------------------------------
	def getUly(self):
		return self.getBoundingBox()[3]
