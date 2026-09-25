import bwtest
from helpers.cluster import ClusterController


class DelTaggedEntitiesTest( bwtest.TestCase ):
	name = "delTaggedEntities test"
	description = "Test ability to delete bots with delTaggedEntities method"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.addCleanup( self.cc.clean )
		self.cc.start()
		self.addCleanup( self.cc.stop )
		self.cc.startProc( "bots", 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def numBots( self ):
		snippet = """
		srvtest.finish( len( BigWorld.bots.values() ) )
		""" 
		return self.cc.sendAndCallOnApp( "bots", snippet = snippet )


	def runTest( self ):		
		# Add 10 bots
		self.cc.bots.add( 10 )

		# Tag 7
		snippet = """
		for i in range(0, 7):
			BigWorld.bots.values()[i].tag = 'DeleteMe'
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", snippet = snippet )

		# Delete tagged
		snippet = """
		BigWorld.delTaggedEntities( 'DeleteMe' )
		srvtest.finish( len( BigWorld.bots.values() ) )
		"""
		numBots = self.cc.sendAndCallOnApp( "bots", snippet = snippet )

		# Check 3 left
		self.assertEqual( numBots, 3 )
