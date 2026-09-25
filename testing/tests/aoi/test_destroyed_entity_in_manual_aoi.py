import time
from bwtest import TestCase
from helpers.cluster import ClusterController


class DestroyedEntityInManualAoI( TestCase ):

	name = "DestroyedEntityInManualAoI"
	description = "Tests the behaviour of addToManualAoI() on destroyed entities"
	tags = []

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "cellapp" )
		self.cc.startProc( "bots" )

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	def runTest( self ):
		self.cc.bots.add( 1 )
		snippet = """
		bot = BigWorld.bots.values()[0]
		bot.stop()
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, snippet )

		#
		# Wait for the bot to enter the world
		#
		snippet = """
		bot = BigWorld.bots.values()[0]
		srvtest.finish( bot.spaceID == 0 )
		"""
		while self.cc.sendAndCallOnApp( "bots", None, snippet ):
			time.sleep( 1 )

		snippet = """
		srvtest.finish( BigWorld.entities['Avatar'].id )
		"""
		self.botID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		#
		# Move the bot to 0, 50
		#
		snippet = """
		bot = BigWorld.bots.values()[0]
		pos = bot.position
		pos.x = 0
		pos.z = -50
		bot.position = pos
		srvtest.assertEqual( bot.position.x, 0, "Bot is out of position" )
		srvtest.assertEqual( bot.position.z, -50, "Bot is out of position" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, snippet )

		#
		# Create TestEntity at the bot position
		#
		snippet = """
		bot = BigWorld.entities[%d]
		entity = BigWorld.createEntity(
			"TestEntity", bot.spaceID, bot.position, bot.direction )
		bot.test_entity = entity
		srvtest.finish( entity.id )
		""" % self.botID
		self.entityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		#
		# Split the space in two
		#
		spaces = self.cc.getWatcherData( "spaces", "cellappmgr", None )
		debugging = self.cc.getWatcherData( "debugging", "cellappmgr", None )
		debugging.getChild( "shouldLoadBalance" ).set( "False" )
		spaceBSP = spaces.getChildren()[0].getChild( "bsp" )
		spaceBSP.getChild( "isLeaf" ).set( "False" )
		time.sleep( 2 )
		spaceBSP.getChild( "position" ).set( "0.0" )

		#
		# Move the test entity into the second split and out of the ghost distance.
		#
		ghostDistance = self.cc.getWatcherValue( "config/ghostDistance",
												"cellapp" )
		snippet = """
		test_entity = BigWorld.entities[%d]
		BigWorld.entities['Avatar'].test_entity = test_entity
		newPos = test_entity.position;
		newPos.z += %f
		test_entity.position = newPos
		srvtest.assertEqual( test_entity.position.x, newPos.x,
			"Entity is out of position" )
		srvtest.finish()
		""" % ( self.entityID, ghostDistance + 200.0 )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		time.sleep(5)

		#
		# Verify the entity is destroyed on cellapp01
		#
		snippet = """
		test_entity = BigWorld.entities['Avatar'].test_entity
		srvtest.assertTrue( test_entity.isDestroyed,
			"Test Entity should be on cellapp02" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		#
		# Add the test entity into the manual AoI set
		#
		snippet = """
		bot = BigWorld.entities[%d]
		srvtest.assertTrue( bot.test_entity.isDestroyed,
			"Test Entity should be on cellapp02" )
		# The first call will set isInAoIOffload flag
		try:
			bot.addToManualAoI( bot.test_entity )
			srvtest.finish( False )
		except ValueError:
			srvtest.finish( True )
		""" % self.botID
		self.assertTrue( self.cc.sendAndCallOnApp( "cellapp", 1, snippet ),
						"addToManualAoI should have raised an error" )

