from MaterialSectionProcessorBase import MaterialSectionProcessorBase
from FileUtils import extractSectionsByName

class MFMFileProcessor( MaterialSectionProcessorBase ):
	def __init__( self ):
		MaterialSectionProcessorBase.__init__( self )
		
		
	def buildDatabase( self, dbEntry ):		
		material = dbEntry.section()
		MaterialSectionProcessorBase.buildDatabase( self, material, dbEntry )
		
		
	def process( self, dbEntry ):		
		return True
