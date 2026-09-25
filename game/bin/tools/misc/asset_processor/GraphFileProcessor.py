import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from FileUtils import extractSectionsByName
from FileUtils import stripExtension
from FileUtils import stripPath
from FileUtils import extractPath
from FileUtils import openSectionFromFolder
from LogFile import errorLog

class GraphFileProcessor:
	def __init__( self ):
		pass
		
	def buildDatabase(self,dbEntry):		
		pass		
				
	def process(self,dbEntry):
		return True