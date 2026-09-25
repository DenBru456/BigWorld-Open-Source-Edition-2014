import bwtest
from helpers.cluster import ClusterController
import time

MAX_TIME = 60

class BecomePlayerTest( bwtest.TestCase ):
	name = "Become Player Test"
	description = "Test bots becomming player"
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


	def runTest( self ):		
		self.cc.bots.add( 1 )

		snippet = """
		clientApp = BigWorld.bots.values()[0]
		entity = clientApp.entities[clientApp.id]
		srvtest.finish( (entity.__class__.__name__, clientApp.id, entity.id) )
		"""
		className, clientAppID, entityID = self.cc.sendAndCallOnApp(
				"bots", snippet = snippet )

		self.assertEqual( className, "PlayerAvatar" )
		self.assertEqual( clientAppID, entityID )
