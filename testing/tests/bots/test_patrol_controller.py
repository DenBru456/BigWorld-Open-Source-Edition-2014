import bwtest
from helpers.cluster import ClusterController
import time

MAX_TIME = 60


class PatrolControllerTest( bwtest.TestCase ):
	name = "PatrolController Test"
	description = "Test bots PatrolController"
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

		self.cc.bots.setMovement( "Patrol", "server/bots/auto_test.bwp" )
		snippet2 = """
		from Math import Vector3
		clientApp = BigWorld.bots.values()[0]
		distSqrN1 = clientApp.position.distSqrTo( Vector3( 20, 0, 20 ) )
		distSqrN2 = clientApp.position.distSqrTo( Vector3( -20, 0, -20 ) )
		srvtest.finish( ( distSqrN1, distSqrN2 ) )
		"""

		start = time.time()
		reachedNode1 = False
		reachedNode2 = False

		while True:
			# Failed to reach nodes within time
			if (time.time() - start) > MAX_TIME:
				self.fail( "Bot failed to move to target within %s seconds"\
						 % MAX_TIME )

			distSqrN1, distSqrN2 = self.cc.sendAndCallOnApp( "bots", 
															snippet = snippet2 )

			if distSqrN1 < 1:
				reachedNode1 = True
			if distSqrN2 < 1:
				reachedNode2 = True

			if reachedNode1 and reachedNode2:
				break

			time.sleep( 0.5 )
