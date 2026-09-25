import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x

class FontFileProcessor:
	def __init__( self ):
		pass
		
	def buildDatabase(self,dbEntry):		
		sect = dbEntry.section()
		
		try:
			fontMap = sect["generated"]["map"].asString
			dbEntry.addDependency(fontMap)
		except TypeError:
			pass


	def process(self,dbEntry):
		return True
