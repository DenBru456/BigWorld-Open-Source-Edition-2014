import bwtest
from helpers.cluster import ClusterController
import time


class BotAddingRemovingTest( bwtest.TestCase ):
	name = "Bot Adding and Removing"
	description = "Test bots adding and removing"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		self.cc.startProc( "bots", 1 )
		bots = self.cc.bots

		user = self.cc.getUser()

		# Adding
		bots.add( 10 )
		numBots = bots.numBots()
		self.assertEqual( numBots, 10, "Failed to add 10 bots" )

		bots.add( 11 )
		numBots = bots.numBots()
		self.assertEqual( numBots, 21, "Failed to add 11 bots" )

		bots.add( 1 )
		numBots = bots.numBots()
		self.assertEqual( numBots, 22, "Failed to add 1 bot" )

		# Removing
		bots.delete( 1 )
		time.sleep( 3 )
		numBots = bots.numBots()
		self.assertEqual( numBots, 21, "Failed to remove 1 bot" )

		bots.delete( 5 )
		time.sleep( 3 )
		numBots = bots.numBots()
		self.assertEqual( numBots, 16, "Failed to remove 5 bot" )

		bots.delete( 16 )
		time.sleep( 3 )
		numBots = bots.numBots()
		self.assertEqual( numBots, 0, "Failed to remove 16 bot" )
