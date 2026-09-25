import bwtest
from helpers.cluster import ClusterController
import time

MAX_TIME = 60

class BeelineControllerTest( bwtest.TestCase ):
	name = "BeelineController Test"
	description = "Test bots BeelineController"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "bots", 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		self.cc.bots.add( 1 )
		self.cc.bots.setMovement( "Beeline", "100,100,100" )

		start = time.time()

		snippet2 = """
		from Math import Vector3
		clientApp = BigWorld.bots.values()[0]
		distSqr = clientApp.position.distSqrTo( Vector3( 100, 100, 100 ) )
		srvtest.finish( distSqr )
		"""

		while True:
			distSqr = self.cc.sendAndCallOnApp( "bots", snippet = snippet2 )

			if distSqr < 1:
				break

			if (time.time() - start) > MAX_TIME:
				self.fail( "Bot failed to move to target within %s seconds" % MAX_TIME )

			time.sleep( 0.5 )
