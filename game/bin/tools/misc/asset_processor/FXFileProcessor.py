from LogFile import errorLog
from FileUtils import fullName


class FXFileProcessor:

	def __init__( self ):		
		pass
		
	# FX files have no dependencies, they are the bottom of the food chain
	# However we do a preprocessing step, calulating the alpha test value
	# and whether or not alpha test is in use.
	def buildDatabase( self, dbEntry ):
		try:
			f = open(fullName(dbEntry.name),'r')
		except IOError:
			errorLog.errorMsg("Could not open %s for reading" % (dbEntry.name,))
			return False
			
		if f == None:
			errorLog.errorMsg("Could not open %s for reading" % (dbEntry.name,))
			return False
						
		lines = f.readlines()
		for line in lines:			
			ignore = False
			if "AlphaRef" in line:
				dbEntry.alphaRef = self.readAlphaRef(line)				
			if "AlphaTestEnable" in line:
				dbEntry.alphaTestEnabled = self.readAlphaTest(line)
			if "CullMode = NONE;" in line:
				dbEntry.doubleSided = True			
		f.close()
				
	def readAlphaRef(self, line):
		pos1 = line.find("=")
		pos2 = line.find(";")
		val = line[pos1+1:pos2]
		#print val
		return val
		
	def readAlphaTest(self, line):
		enabled = False
		if "True" in line:
			enabled = True
		if "TRUE" in line:
			enabled = True
		return enabled
