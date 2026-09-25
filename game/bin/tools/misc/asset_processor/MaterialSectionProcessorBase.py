from LogFile import errorLog
from FileUtils import fullName
from FileUtils import extractSectionsByName
import AssetDatabase

# This class provides a base class for those that processes material sections,
# it is only meant to be derived from, not used on its own.
class MaterialSectionProcessorBase:

	def __init__( self ):
		pass
		
		
	def appliesTo( self ):
		#note : remove "chunk" because we no longer edit materials in chunks
		return ("model","visual","mfm")
		
		
	def buildDatabase( self, material, dbEntry ):
		fxs = extractSectionsByName( material , "fx" )
		for fx in fxs: 
			if fx.asString != "":
				dbEntry.addDependency( fx.asString )
		if len(fxs) > 1: 
			dbEntry.flagHasMoreThanOneFX(fxs)
		
		properties = extractSectionsByName( material, "property" )
		for property in properties:
			if property.has_key("Texture"):
				if property.readString("Texture") != "":
					dbEntry.addDependency( property.readString("Texture") )
			elif property.has_key("TextureFeed"):
				if property.readString("TextureFeed/default") != "":
					dbEntry.addDependency( property.readString("TextureFeed/default") )	
	
		
	# Process material section and call derived class "processMaterialSection"
	def process( self, dbEntry ):
		dbEntrySection = dbEntry.section()
		changed = False
				
		if ".mfm" in dbEntry.name:
			changed = self.processMaterialSection(dbEntrySection,dbEntry)
		elif ".chunk" in dbEntry.name:			
			models = extractSectionsByName(dbEntrySection,"model")
			for model in models:				
				materials = extractSectionsByName(model,"material")
				for material in materials:										
					changed = self.processMaterialSection(material,dbEntry) or changed
		elif ".model" in dbEntry.name:
			dyes = extractSectionsByName(dbEntrySection,"dye")
			for dye in dyes:
				tints = extractSectionsByName(dye,"tint")
				for tint in tints:
					matSect = tint["material"]
					if matSect != None:
						fxName = matSect["fx"]
						if fxName != "":
							changed = self.processMaterialSection(matSect,dbEntry) or changed
							
		else:			
			renderSets = extractSectionsByName(dbEntrySection,"renderSet")
			for rs in renderSets:				
				geometries = extractSectionsByName(rs,"geometry")
				for g in geometries:					
					primitiveGroups = extractSectionsByName(g,"primitiveGroup")
					for pg in primitiveGroups:
						matSect = pg["material"]
						if matSect:
							changed = self.processMaterialSection(matSect,dbEntry) or changed
							
		if changed: dbEntrySection.save()			
		return changed
		