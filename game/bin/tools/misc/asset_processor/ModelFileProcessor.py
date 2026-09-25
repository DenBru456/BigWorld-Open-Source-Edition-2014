import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from LogFile import errorLog
from FileUtils import extractSectionsByName
from FileUtils import extractPath
from FileUtils import openSectionFromFolder
from MaterialSectionProcessorBase import MaterialSectionProcessorBase

class ModelFileProcessor( MaterialSectionProcessorBase ):
	def __init__( self ):
		MaterialSectionProcessorBase.__init__( self )
		
		
	def buildDatabase(self,modelEntry):		
		sect = modelEntry.section()
		
		#ADD PARENT
		parentName = ""
		if sect.has_key("Parent"):
			parentName = sect.readString("Parent")
		if sect.has_key("parent"):
			parentName = sect.readString("parent")
		if parentName != "":
			parentName = parentName + ".model"
			modelEntry.addDependency( parentName )
		
		#ADD VISUAL FROM MODEL
		sects = []
		sects.extend( extractSectionsByName(sect,"nodelessVisual") )
		sects.extend( extractSectionsByName(sect,"nodefullVisual") )
		sects.extend( extractSectionsByName(sect,"billboardVisual") )
		for i in sects:
			name = i.asString + ".visual"
			visual = ResMgr.openSection(name)
			if visual == None:
				name = i.asString + ".static.visual"
				visual = ResMgr.openSection(name)
			
			if visual != None:	
				visualPath = extractPath(name)
				if visualPath != "":					
					visualPath = visualPath.replace("\\","/")
					modelEntry.addDependency( visualPath + "/" + visual.name )					
					
		#ADD MFM,FX,TEXTURES FROM DYE
		dyes = extractSectionsByName(sect,"dye")
		for dye in dyes:
			tints = extractSectionsByName(dye,"tint")
			for tint in tints:
				material = tint["material"]
				if material != None:
					mfm = material["mfm"]
					if mfm != None:
						(mfmSect,mfmPath) = openSectionFromFolder(mfm.asString)						
						if mfmSect != None:							
							mfmPath = mfmPath.replace("\\","/")
							modelEntry.addDependency( mfmPath + "/" + mfmSect.name )							
					
					MaterialSectionProcessorBase.buildDatabase( self, material, modelEntry )
							
		#ADD ANIMATIONS
		animations = extractSectionsByName(sect,"animation")
		for animation in animations:
			nodes = animation.readString("nodes")
			if nodes != "":
				nodes = nodes + ".animation"
				modelEntry.addDependency( nodes )
				
				
	def process(self,dbEntry):
		return True
				