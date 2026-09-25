from bwtest import TestCase, log
from helpers.cluster import ClusterController
import sys


class EntityRemovedFromClient( TestCase ):

	name = "EntityRemovedFromClient"
	description = """Tests the behaviour when one entity is removed from the
	client of a witness but remains in the witness's AoI. In this case, the
	client related state of that entity cache should be reset but server related
	state should be kept (one of which is MANUALLY_ADDED flag).
	"""

	isManualTag = """
		<IsManualAoI> 
			true
	</IsManualAoI>
	"""
	tags = []

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	def assertManaulAoIEquals( self, aoiList ):
		getManualAoISnippet = """
		bot = BigWorld.entities[%d]		
		ret = bot.entitiesInManualAoI()
		srvtest.finish( [ e.id for e in ret ] )
		""" % self.botID
		entitiesInManualAoI = self.cc.sendAndCallOnApp( "cellapp", 1,
													getManualAoISnippet )
		self.assertEquals( sorted( entitiesInManualAoI ), sorted( aoiList ),
						"Unexpected manual AoI entity set" )

	def runTest( self ):
		def addIsManualTag( line ):
			if line.find( "</root>" ) != -1:
				return self.isManualTag + line
			else:
				return line
		self.cc.lineEditResTreeFile( "scripts/entity_defs/TestEntity.def",
									addIsManualTag )
		self.cc.start()
		self.cc.startProc( "bots" )
		self.cc.waitForServerSettle()

		result = self.cc.bots.add( 1 )
		self.assertTrue( result, "Failed to add bot" )

		snippet = """
		bot = BigWorld.bots.values()[0]
		bot.stop()
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, snippet )

		snippet = """
		avatars = [e for e in BigWorld.entities.values()
			if e.className == 'Avatar']
		srvtest.finish( avatars[0].id )
		"""
		self.botID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [] )

		#
		# Create TestEntity within the bot's AoI
		#
		snippet = """
		bot = BigWorld.entities[%d]
		entity = BigWorld.createEntity(
			"TestEntity", bot.spaceID, bot.position, bot.direction )
		srvtest.finish( entity.id )
		""" % self.botID
		self.testEntityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [] )

		#
		# Add the test entity into the manual AoI set
		#
		snippet = """
		bot = BigWorld.entities[%d]
		bot.addToManualAoI( %d )
		srvtest.finish()
		""" % ( self.botID, self.testEntityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [ self.testEntityID ] )

		#
		# Remove the entity from client (withhold from client), the test entity
		# should be still in manual AoI set, or in other words the flag
		# MANUALLY_ADDED was kept
		#
		snippet = """
		bot = BigWorld.entities[%d]
		bot.withholdFromClient( %d, True )
		srvtest.finish()
		""" % ( self.botID, self.testEntityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [ self.testEntityID ] )