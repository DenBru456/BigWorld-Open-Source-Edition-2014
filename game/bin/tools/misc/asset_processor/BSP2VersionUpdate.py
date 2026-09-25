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


#This class converts old bsp data to bsp2 data
class BSP2VersionUpdate:
	def __init__( self ):
		self.description = "BSP to BSP2 version update"
		
	def appliesTo( self ):
		return ("visual",)
		
	def process( self, dbEntry ):				
		ret = AssetProcessorSystem.updateBSPVersion( dbEntry.name )
		if ret == "":
			return True
		else:
			errorLog.errorMsg(ret)
			return False		