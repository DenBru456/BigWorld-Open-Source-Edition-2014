from bwtest import TestCase
from helpers.cluster import ClusterController


class EntitiesInManualAoI( TestCase ):

	name = "EntitiesInManualAOI"
	description = "Tests the behaviour of entitiesInManualAoI() cell method"
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
		bot.setAoIRadius(100)
		ret = bot.entitiesInManualAoI()
		srvtest.finish( [ e.id for e in ret ] )
		""" % self.botID
		entitiesInManualAoI = self.cc.sendAndCallOnApp( "cellapp", 1,
													getManualAoISnippet )
		self.assertEquals( sorted( entitiesInManualAoI ), sorted( aoiList ),
						"Unexpected manual AoI entity set" )

	def assertAoIEquals( self, aoiList ):
		getAoISnippet = """
		bot = BigWorld.entities[%d]
		ret = bot.entitiesInAoI()
		srvtest.finish( [ e.id for e in ret ] )
		""" % self.botID
		entitiesInAoI = self.cc.sendAndCallOnApp( "cellapp", 1, getAoISnippet )
		self.assertEquals( sorted( entitiesInAoI ), sorted( aoiList ),
						"Unexpected AoI entity set" )

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
		self.cc.bots.add( 1 )
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
		self.assertAoIEquals( [] )

		#
		# Create TestEntity within the bot's AoI
		#
		snippet = """
		bot = BigWorld.entities[%d]
		entity = BigWorld.createEntity(
			"TestEntity", bot.spaceID, bot.position, bot.direction )
		srvtest.finish( entity.id )
		""" % self.botID
		self.entityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [] )
		self.assertAoIEquals( [] )

		#
		# Add the test entity into the manual AoI set
		#
		snippet = """
		bot = BigWorld.entities[%d]
		bot.addToManualAoI( %d )
		srvtest.finish()
		""" % ( self.botID, self.entityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [ self.entityID ] )
		self.assertAoIEquals( [ self.entityID ] )

		# Move the entity outside of AoI range
		snippet = """
		entity = BigWorld.entities[%d]
		newPos = entity.position;
		newPos.x += 200
		entity.position = newPos
		srvtest.assertEqual( entity.position.x, newPos.x,
			"Entity is out of position" )
		srvtest.finish()
		""" % self.entityID
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [ self.entityID ] )
		self.assertAoIEquals( [ self.entityID ] )

		# Remove test entity from the manual AoI set
		snippet = """
		bot = BigWorld.entities[%d]
		bot.removeFromManualAoI( %d )
		srvtest.finish()
		""" % ( self.botID, self.entityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [] )
		self.assertAoIEquals( [] )

		# Create another TestEntity
		snippet = """
		bot = BigWorld.entities[%d]
		entity = BigWorld.createEntity(
			"TestEntity", bot.spaceID, bot.position, bot.direction )
		srvtest.finish( entity.id )
		""" % self.botID
		self.anotherEntityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [] )
		self.assertAoIEquals( [] )

		snippet = """
		bot = BigWorld.entities[%d]
		bot.addToManualAoI( %d )
		bot.addToManualAoI( %d )
		srvtest.finish()
		""" % ( self.botID, self.entityID, self.anotherEntityID )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		self.assertManaulAoIEquals( [ self.entityID, self.anotherEntityID ] )
