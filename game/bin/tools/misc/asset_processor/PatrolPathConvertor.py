from LogFile import errorLog
from FileUtils import fullName
from FileUtils import extension
from FileUtils import stripExtension
from FileUtils import stripPath
from FileUtils import extractSectionsByName
import AssetProcessorSystem
import AssetDatabase
import Math

#------------------------------------------------------------------------------
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#------------------------------------------------------------------------------

class PatrolPathConvertor:
	def __init__( self ):
		self.description = "Patrol Path Convertor"
		
	def appliesTo( self ):
		return ("chunk",)

	def process( self, dbEntry ):
		stations = self.processStations( dbEntry )
		entities = self.processEntities( dbEntry )
		needsSave = stations or entities
		if needsSave:
			dbEntry.section().save()
		return needsSave

	def processStation( self, station, udo ):
		udo.writeString("type", "PatrolNode")
		udo.writeInt("Domain", 2)
		
		matrix = Math.Matrix()
		position = station.readVector3( "position" )
		if position:
			matrix.setTranslate( position )
		udo.writeMatrix( "transform", matrix )
		
		patrolNode = station.readString( "id" )
		udo.writeString( "guid", patrolNode )
		
		patrolLinks = udo.createSection( "properties/patrolLinks" )
		backLinks = udo.createSection( "backLinks" )
		
		patrolEntry = AssetDatabase.fileDatabase.get( patrolNode )
		
		for dependency in patrolEntry.dependencies:
			item = patrolLinks.createSection( "item" )
			item.writeString( "guid", dependency.name )
			item.writeString( "chunkId", self.getChunkName( dependency.name ) )
				
		for usedBy in patrolEntry.usedBys:
			if extension( usedBy.name ) != "chunk":	
				link = backLinks.createSection( "link" )
				link.writeString( "guid", usedBy.name )
				link.writeString( "chunkId", self.getChunkName( usedBy.name ) )
	
	def processStations( self, dbEntry ):
		needsSave = False
		sect = dbEntry.section()
		
		stations = extractSectionsByName( sect, "station" )
		if len(stations) > 0:
			needsSave = True
			for station in stations:
				udo = sect.createSection( "UserDataObject" )
				self.processStation( station, udo )
			
			while sect.has_key("station"):
				sect.deleteSection("station")
		return needsSave
		
	def processEntities( self, dbEntry ):
		needsSave = False
		sect = dbEntry.section()
		
		entities = extractSectionsByName( sect, "entity" )
		for entity in entities:
			properties = entity[ "properties" ]
			if properties.has_key( "patrolPathNode" ):
				# Get the wanted node id from the built-in patrol node property.
				needsSave = True
				patrolNode = properties.readString( "patrolPathNode" )
				nodeChunk = ""
				if patrolNode != "":
					nodeChunk = self.getChunkName( patrolNode )

				# No need for these old patrol node tags anymore.
				properties.deleteSection( "patrolPathNode" )

				if patrolNode != "":
					# Look for properties that point to patrol path graph files,
					# and replace the graph file id with the node guid found in
					# the previous step.
					for property in properties.items():
						propDS = property[1]
						propValue = propDS.asString
						# Check if it's a GUID first before searching the database.
						# This prevents searching every property value in the database.
						if len( propValue ) == 35 and propValue[8] == '.' and propValue[17] == '.' and propValue[26] == '.':
							# Slightly hacky, but to make sure we catch
							# all graph files no matter its case.
							graphFileLwr = propValue.lower() + ".graph"
							graphFileUpr = propValue.upper() + ".graph"
							if AssetDatabase.fileDatabase.entries.has_key( graphFileLwr ) or \
							   AssetDatabase.fileDatabase.entries.has_key( graphFileUpr ):
								# It's a reference to a graph file so it must be
								# a PATROL_PATH property. Set it to the desired
								# node as specified in "patrolPathNode".
								propDS.asString = ""
								propDS.writeString( "guid", patrolNode )
								propDS.writeString( "chunkId", nodeChunk )
					
			if entity.has_key( "backLinks" ):
				needsSave = True
				entity.deleteSection( "backLinks" )
		
		return needsSave
		
	def getChunkName( self, patrolNode ):
		chunkName = ""
		entry = AssetDatabase.fileDatabase.get( patrolNode )
		for usedBy in entry.usedBys:
			if extension( usedBy.name ) == "chunk":
				chunkName = stripExtension( usedBy.name ) 
				if chunkName[-1] == "i":
					shellEntry = AssetDatabase.fileDatabase.get( chunkName + ".chunk" )
					shellEntrySect = shellEntry.section()
					chunkName = AssetProcessorSystem.outsideChunkIdentifier( shellEntrySect.readMatrix( "transform" ).applyToOrigin() )
				
				idx = chunkName.rfind("/sep")
				if idx == -1:
					idx = chunkName.rfind("\\sep")
					if idx == -1:
						return chunkName[-9:]
				return chunkName[idx-8:]
		return chunkName
		
		