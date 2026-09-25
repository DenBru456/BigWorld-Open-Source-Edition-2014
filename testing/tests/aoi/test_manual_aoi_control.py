"""
This file contains automated tests for manual AoI control logic
https://docs.bigworldtech.com/2/current/html/server_programming_guide/server_programming_guide.html#xref_Manual_AOI_Control
Basically testcases check all sensible combinations of possible actions: adding to AoI, entity moves, removing from AoI for
two global situations - when entity xml setting 'IsManualAoI' is set to True and False.
"""

from bwtest import TestCase
from helpers.cluster import ClusterController
from bwtest import log
from bwtest import addParameterizedTestCases

AOI_RADIUS = 500 # For setting AoI range explicitly
TEST_ENTITY_NAME = "TestEntity"

# This is a container for transferring entity properties between the server and a test
class EntityInfo: pass

class RemoteCaller:
	"""
	Utility class which encapsulates remote execution of scripts on the server.
	"""
	def __init__( self, clusterController ):
		self.cc = clusterController

	def cellGetEntityInfo( self, entityID ):
		log.progress( 'cellGetEntityInfo( %d )' % ( entityID ) )
		entityInfo = EntityInfo()
		snippet = """
			entity = BigWorld.entities[%d]
			srvtest.finish( (entity.id, entity.position, entity.direction, entity.spaceID) )
		"""
		entityInfo.id, entityInfo.position, entityInfo.direction, entityInfo.spaceID = \
			self.cc.sendAndCallOnApp( "cellapp", 1, snippet % entityID )
		return entityInfo
		
	def cellCreateEntity( self, name, spaceID, position, direction ):
		log.progress( 'cellCreateEntity( "%s", %d, %s, %s )' % ( name, spaceID, position, direction ) )
		strPosition = str(position)
		strDirection = str(direction)
		snippet = """
			entity = BigWorld.createEntity(	"%s", %d, %s, %s )
			srvtest.finish( entity.id )
		""" % (name, spaceID, position, direction)
		entityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		return entityID
		
	def cellEntitiesInAoI( self, entityID ):
		log.progress( 'cellEntitiesInAoI( %d )' % ( entityID ) )
		snippet = """
			entity = BigWorld.entities[%d]
			ret = entity.entitiesInAoI()
			srvtest.finish( [ e.id for e in ret ] )
		""" % entityID
		entitiesInAoI = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		return entitiesInAoI
		
	def cellEntitiesInManualAoI( self, entityID ):
		log.progress( 'cellEntitiesInManualAoI( %d )' % ( entityID ) )
		snippet = """
			entity = BigWorld.entities[%d]
			ret = entity.entitiesInManualAoI()
			srvtest.finish( [ e.id for e in ret ] )
		""" % entityID
		entitiesInManualAoI = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		return entitiesInManualAoI
		
	def cellAddToManualAoI( self, entityID, aoiEntityID ):
		log.progress( 'cellAddToManualAoI( %d, %d )' % ( entityID, aoiEntityID ) )
		snippet = """
			entity = BigWorld.entities[%d]
			entity.addToManualAoI( %d )
			srvtest.finish()
		""" % ( entityID, aoiEntityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
	def cellRemoveFromManualAoI( self, entityID, aoiEntityID ):
		log.progress( 'cellRemoveFromManualAoI( %d, %d )' % ( entityID, aoiEntityID ) )
		snippet = """
			entity = BigWorld.entities[%d]
			entity.removeFromManualAoI( %d )
			srvtest.finish()
		""" % ( entityID, aoiEntityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
	def cellUpdateManualAoI( self, entityID, aoiList ):
		log.progress( 'cellUpdateManualAoI( %d, %s )' % ( entityID, aoiList ) )
		snippet = """
			entity = BigWorld.entities[%d]
			success = entity.updateManualAoI( %s, False )
			srvtest.finish( success )
		""" % ( entityID, aoiList )
		success = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		return success
		
	def cellMoveEntity( self, entityID, newPosition ):
		log.progress( 'cellMoveEntity( %d, %s )' % ( entityID, newPosition ) )
		snippet = """
			entity = BigWorld.entities[%d]
			newPos = %s
			entity.position = newPos
			srvtest.assertTrue( abs(newPos[0] - entity.position.x) < 1.0 and
								abs(newPos[1] - entity.position.y) < 1.0 and
								abs(newPos[2] - entity.position.z) < 1.0,
								"Entity is out of position" )
			srvtest.finish()
		""" % (entityID, newPosition)
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

	def cellSetAoIRadius( self, entityID, radius ):
		log.progress( 'cellSetAoIRadius( %d, %f )' % ( entityID, radius ) )
		snippet = """
			entity = BigWorld.entities[%d]
			entity.setAoIRadius(%f)
			srvtest.finish()
		""" % (entityID, radius)
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )


class AoITestCaseBase( TestCase ):
	"""
	Base class (fixture) for all the testcases in this file.
	"""
	isManualTag = """
		<IsManualAoI> 
			true
		</IsManualAoI>
	"""
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.rc = RemoteCaller(self.cc)

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	def assertEqualsSet( self, aoiListExpected, aoiList, message ):
		self.assertEquals( sorted( aoiListExpected ), sorted( aoiList ),
							message )
	
	def addBot( self ):
		self.cc.bots.add( 1 )
		
		initBotSnippet = """
			bot = BigWorld.bots.values()[0]
			bot.stop()
			srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, initBotSnippet )

		snippet = """
			avatars = [e for e in BigWorld.entities.values()
				if e.className == 'Avatar']
			srvtest.finish( avatars[0].id )
		"""
		botID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
		# Always add a bot with a given AoI radius
		self.rc.cellSetAoIRadius( botID, AOI_RADIUS )
		
		return botID
	
	def setIsManualTag( self, entityDefName ):
		entityDefPath = "scripts/entity_defs/%s.def" % entityDefName
		def addIsManualTag( line ):
			if line.find( "</root>" ) != -1:
				return self.isManualTag + line
			else:
				return line
		self.cc.lineEditResTreeFile( entityDefPath,	addIsManualTag )

################################################################################
## Tests: Regular AoI (neither a flag nor dynamic manual control)
################################################################################
class Regular_CreateInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "Regular_CreateInAoI_MoveOutAoI"
	description = "Basic: check correctness of adding and removing entity using regular AoI logic"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty initially" )

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )

class Regular_CreateOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "Regular_CreateOutAoI_MoveInAoI"
	description = "Basic: check correctness of adding and removing entity using regular AoI logic"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty initially" )

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )

		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		
################################################################################
## Tests: xml setting IsManualAoI = True 
################################################################################
class ManualAoI_ManualFlag_Add_Remove( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_Add_Remove"
	description = "Basic: check correctness of adding and removing entities"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		# Check that AoI lists are empty initially
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty initially" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty initially" )

		bot = self.rc.cellGetEntityInfo( botID )
		
		# Create TestEntity within the bot's AoI
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		
		# Check that AoI lists are still empty
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		# Add the test entity into the manual AoI set
		self.rc.cellAddToManualAoI( botID, entityID )

		# Check that AoI lists contain the new entity
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		# Create another TestEntity within the bot's AoI
		anotherEntityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		
		self.rc.cellAddToManualAoI( botID, anotherEntityID )
		self.assertEqualsSet( [ entityID, anotherEntityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain 2 entities" )
		self.assertEqualsSet( [ entityID, anotherEntityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the 2 entities" )
		
		# Remove test entity from the manual AoI set
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [ anotherEntityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain only one entity" )
		self.assertEqualsSet( [ anotherEntityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain only one entity" )

class ManualAoI_ManualFlag_Update( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_Update"
	description = "Basic: check correctness of entities updating"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
				
		self.cc.start()
		self.cc.startProc( "bots" )
		
		botID = self.addBot()
		
		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID_A = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		entityID_B = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		entityID_C = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		
		# Add two entities to AoI: A and B
		self.rc.cellUpdateManualAoI( botID, [ entityID_A, entityID_B ] )
		
		entitiesInAoI = self.rc.cellEntitiesInAoI( botID )
		entitiesInManualAoI = self.rc.cellEntitiesInManualAoI( botID )
		self.assertEqualsSet( [ entityID_A, entityID_B ], entitiesInAoI, "AoI list should contain 2 entities" )
		self.assertEqualsSet( [ entityID_A, entityID_B ], entitiesInManualAoI, "Manual AoI list should contain the 2 entities" )
		
		# Remove A, keep B, add C
		self.rc.cellUpdateManualAoI( botID, [ entityID_B, entityID_C ] )
		
		entitiesInAoI = self.rc.cellEntitiesInAoI( botID )
		entitiesInManualAoI = self.rc.cellEntitiesInManualAoI( botID )
		self.assertEqualsSet( [ entityID_B, entityID_C ], entitiesInAoI, "AoI list should contain 2 entities" )
		self.assertEqualsSet( [ entityID_B, entityID_C ], entitiesInManualAoI, "Manual AoI list should contain the 2 entities" )
		
class ManualAoI_ManualFlag_AddInAoI_RemoveInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_AddInAoI_RemoveInAoI_MoveOutAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		
class ManualAoI_ManualFlag_AddOutAoI_RemoveOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_AddOutAoI_RemoveOutAoI_MoveInAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )

class ManualAoI_ManualFlag_AddInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_AddInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )	

class ManualAoI_ManualFlag_AddOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_AddOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )	

class ManualAoI_ManualFlag_AddInAoI_MoveOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_AddInAoI_MoveOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )	

class ManualAoI_ManualFlag_AddOutAoI_MoveInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "ManualAoI_ManualFlag_AddOutAoI_MoveInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.setIsManualTag( TEST_ENTITY_NAME )
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )	
		
################################################################################
## Tests: xml setting IsManualAoI = False (default)
################################################################################
class ManualAoI_NoManualFlag_AddInAoI_RemoveInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "ManualAoI_NoManualFlag_AddInAoI_RemoveInAoI_MoveOutAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the entity" )

		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		
class ManualAoI_NoManualFlag_AddOutAoI_RemoveOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "ManualAoI_NoManualFlag_AddOutAoI_RemoveOutAoI_MoveInAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the entity" )

		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )

class ManualAoI_NoManualFlag_AddInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "ManualAoI_NoManualFlag_AddInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )

class ManualAoI_NoManualFlag_AddOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "ManualAoI_NoManualFlag_AddOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )

class ManualAoI_NoManualFlag_AddInAoI_MoveOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI( AoITestCaseBase ):

	name = "ManualAoI_NoManualFlag_AddInAoI_MoveOutAoI_MoveInAoI_RemoveInAoI_MoveOutAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( 0.0, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the entity" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )	

class ManualAoI_NoManualFlag_AddOutAoI_MoveInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI( AoITestCaseBase ):

	name = "ManualAoI_NoManualFlag_AddOutAoI_MoveInAoI_MoveOutAoI_RemoveOutAoI_MoveInAoI"
	description = "Complex scenario"
	tags = [ "AoI" ]
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		botID = self.addBot()

		bot = self.rc.cellGetEntityInfo( botID )
		
		entityID = self.rc.cellCreateEntity( TEST_ENTITY_NAME, bot.spaceID, ( AOI_RADIUS * 2, 0.0, 0.0 ), ( 0.0, 0.0, 0.0 ) )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )

		self.rc.cellAddToManualAoI( botID, entityID )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInAoI( botID ), "AoI list should contain the new entity" )
		self.assertEqualsSet( [ entityID ], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should contain the new entity" )

		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )
		self.rc.cellMoveEntity( entityID, ( AOI_RADIUS * 2, 0.0, 0.0 ) )
		
		self.rc.cellRemoveFromManualAoI( botID, entityID )
		self.assertEqualsSet( [], self.rc.cellEntitiesInAoI( botID ), "AoI list should be empty" )
		self.assertEqualsSet( [], self.rc.cellEntitiesInManualAoI( botID ), "Manual AoI list should be empty" )
		
		self.rc.cellMoveEntity( entityID, ( 0.0, 0.0, 0.0 ) )