from LogFile import errorLog
from FileUtils import fullName
from FileUtils import extractSectionsByName
import AssetDatabase

#
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#
class RedundantEffectStatesFix:
	def __init__( self ):
		self.description = "Redundant Effect States Fix"
		self.stripList = []
		self.stripList.append( "ColorWriteEnable = RED | GREEN | BLUE;" )
		self.stripList.append( "CullMode = CCW;" )
		self.stripList.append( "ZFunc = LESSEQUAL;" )
		self.stripList.append( "PointSpriteEnable = FALSE;" )
		self.stripList.append( "StencilEnable = FALSE;" )		
		self.stripList.append( "ALPHAFUNC = GREATER;" )
		
	def appliesTo( self ):
		return ("fx")
		
		
	# Strip out any Redundant states from the effect file
	def process( self, dbEntry ):		
		output = []
		filename = fullName(dbEntry.name)
		changed = False
		
		try:
			f = open(filename,'r')
		except IOError:		
			errorLog.errorMsg("Could not open %s for reading" % (filename,))
			return False
			
		lines = f.readlines()		
		for line in lines:
			ignore = False
			for i in self.stripList:
				if i in line:
					ignore = True
					changed = True
			if not ignore:
				output.append(line)			
		f.close()
		
		#output	
		if changed and len(output) > 0:
			f = open(filename,'w+')
			if f == None:
				errorLog.errorMsg("Could not open %s for writing" % (filename,))
				changed = False
			else:
				f.writelines(output)
				f.close()
			
		return changed
			