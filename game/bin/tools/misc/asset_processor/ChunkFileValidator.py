from LogFile import errorLog
from FileUtils import fullName
import AssetProcessorSystem

#------------------------------------------------------------------------------
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#------------------------------------------------------------------------------


#This class check chunk data to see if all position inside it in valid
class ChunkFileValidator:
	def __init__( self ):
		self.description = "Chunk File Validator"
		
	def appliesTo( self ):
		return ("chunk",)
		
	def process( self, dbEntry ):
		ret = True
		if dbEntry.name[-7:] == "o.chunk":
			for (name,sect) in dbEntry.section().items():
				position = None
				if sect.has_key( "transform" ):
					position = sect.readVector3( "transform/row3" )
				elif sect.has_key( "position" ):
					position = sect.readVector3( "position" )
				if position and ( position[0] < 0 or position[0] > 100 or position[2] < 0 or position[2] > 100 ):
					msg = "error in " + dbEntry.name + " " + sect.name + " at " + str( position )
					errorLog.errorMsg( msg )
				ret = False
		return ret