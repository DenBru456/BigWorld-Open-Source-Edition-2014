import sys
x=sys.path
sys.path=x
import ResMgr
from FileUtils import extension
from FileUtils import extractSectionsByName

class ImageFileProcessor:
	def __init__( self ):
		pass
		
	def buildDatabase(self,dbEntry):		
		if extension(dbEntry.name) == "texanim":
			sect = dbEntry.section()
			textures = extractSectionsByName(sect, "texture")
			for texture in textures:
				dbEntry.addDependency(texture.asString)
				
	def process(self,dbEntry):
		return True
		