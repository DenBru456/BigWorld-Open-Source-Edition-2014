import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from FileUtils import extractSectionsByName

class GuiFileProcessor:
	def __init__( self ):
		pass
		
		
	def buildDatabase(self,dbEntry):		
		#SimpleGUIComponent
		self.extractTextures( dbEntry, "SimpleGUIComponent" )
				
		#GoboComponent
		self.extractTextures( dbEntry, "GoboComponent" )
				
		#FrameGUIComponent
		self.extractTextures( dbEntry, "FrameGUIComponent", True )
				
		#WindowGUIComponent
		self.extractTextures( dbEntry, "WindowGUIComponent" )
				
		#GraphGUIComponent
		self.extractTextures( dbEntry, "GraphGUIComponent" )
				
		#TextGUIComponent
		self.extractTextures( dbEntry, "TextGUIComponent" )
		
		#BoundingBoxGUIComponent
		self.extractTextures( dbEntry, "BoundingBoxGUIComponent" )
		
		#ConsoleGUIComponent
		self.extractTextures( dbEntry, "extractTextures" )
	
	
	def extractTextures( self, dbEntry, componentName, isFrame = False ):
		sect = dbEntry.section()
		
		components = extractSectionsByName( sect, componentName )
		for component in components:
			if component.readString( "textureName" ) != "":
				dbEntry.addDependency( component.readString( "textureName" ) )
			if isFrame:
				if component.readString( "edgeTextureName" ) != "":
					dbEntry.addDependency( component.readString( "edgeTextureName" ) )
				if component.readString( "cornerTextureName" ) != "":
					dbEntry.addDependency( component.readString( "cornerTextureName" ) )
		
				
	def process(self,dbEntry):
		return True
