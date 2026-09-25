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
import AssetDatabase

		
class ChunkFileProcessor:
	def __init__( self ):
		pass
		
	def buildDatabase(self,dbEntry):		
		sect = dbEntry.section()
		
		# add the shell model as a dependency
		if sect.has_key( "shell/resource" ):
			shellName = sect.readString( "shell/resource" )
			dbEntry.addDependency( shellName )
		
		models = extractSectionsByName(sect,"model")
		for model in models:
			modelName = model.readString( "resource" )
			dbEntry.addDependency( modelName )
			
			materials = extractSectionsByName(model,"material")
			for material in materials:
				fxs = extractSectionsByName(material,"fx")
				for fx in fxs: dbEntry.addDependency( fx.asString )
				if len(fxs) > 1: dbEntry.flagHasMoreThanOneFX(fxs)		
				
		# make dependencies from the chunk to the patrol node
		# also store the patrol node's links to and from
		stations = extractSectionsByName(sect,"station")
		for station in stations:
			stationID = station.readString( "id" )
			dbEntry.addDependency( stationID )
			entry = AssetDatabase.fileDatabase.get( stationID )
			links = extractSectionsByName( station, "link" )
			for link in links:
				if link.readBool( "traversable" ):
					entry.addDependency( link.readString( "to" ) )
				else:
					entry.addUsedBy( link.readString( "to" ) )
					
		# do the same with the entity in the chunk
		entities = extractSectionsByName( sect, "entity" )
		for entity in entities:
			entityID = entity.readString( "guid" )
			if entityID == "":
				entityID = AssetProcessorSystem.getGuid()
				entity.writeString( "guid", entityID )
			dbEntry.addDependency( entityID )
			properties = entity[ "properties" ]
			if properties.has_key( "patrolPathNode" ):
				patrolNode = properties.readString( "patrolPathNode" )
				if patrolNode != "":
					entry = AssetDatabase.fileDatabase.get( patrolNode )
					entry.addUsedBy( entityID )
						
		# store which shells we have
		overlappers = extractSectionsByName( sect, "overlapper" )
		for overlapper in overlappers:
			dbEntry.addDependency( overlapper.asString + ".chunk" )
			
		# what the texture blends are now?
		cdataname = stripExtension( dbEntry.name ) + ".cdata/terrain2"
		cdata = ResMgr.openSection( cdataname )
		if cdata != None:
			layers = extractSectionsByName( cdata, "layer" )
			for layer in layers:
				layerdata = layer.asBinary
				for ld in layerdata.split('\0'):
					if "PNG" in ld:
						for pngs in ld.split('\n'):
							posdot = pngs.rfind('.')
							if posdot > 0:
								# the -5 removes the ?PNG appendage
								dbEntry.addDependency(pngs[0:-5])
				
	def process(self,dbEntry):
		return True
