from LogFile import errorLog
from FileUtils import fullName
import AssetProcessorSystem
import ResMgr

class CDataConverter:
	def __init__( self ):
		self.description = "CData File Converter"
		
	def appliesTo( self ):
		return ("chunk",)
		
	def process( self, dbEntry ):
		cdataName = dbEntry.name[:-6] + ".cdata"
		cdata = ResMgr.openSection(cdataName)
		(newSection,changed) = cdata.copyToZip()
		
		#comment this 'if' out to force update of existing zip formats:
		if changed == True:		
			newSection.save()
			return True
		return False