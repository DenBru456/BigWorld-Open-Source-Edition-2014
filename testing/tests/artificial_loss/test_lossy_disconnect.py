from bwtest import TestCase
from helpers.cluster import ClusterController

import time

LOSS_RATIO 			= 0.1
LOSS_LATENCY_MIN 	= 0.35
LOSS_LATENCY_MAX 	= 0.5
GRACE_LATENCY 		= 10 # An eternity


class LossyDisconnectTest( TestCase ):
	"""
	The SUT is the network library's resend mechanism. We trigger
	it by using artifical loss which relies probabilities. This
	test case passing might be a false positive as we can not
	guarantee the SUT was exercised.

	Therefore, this should only be run manually with the repeat option.
	"""

	tags = [ 'MANUAL' ]


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "bots", 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def assertDisconnectionRequested( self ):
		"""
		Proxy is destroyed when it recieves a disconnection request.
		"""

		latestTime = LOSS_LATENCY_MAX * GRACE_LATENCY + time.time()

		while self.cc.numProxies() != self.cc.bots.numBots():
			if time.time() > latestTime: 
				self.fail( "Proxy did not receive disconnection request" )


	def runTest( self ):
		"""
		Lost disconnection requests should be resent.
		"""

		# Reliable client
		self.cc.bots.add( 1 )
		self.assertEqual( self.cc.numProxies(), self.cc.bots.numBots() )

		self.cc.bots.delete( 1 )
		self.assertDisconnectionRequested()

		# Lossy client
		self.cc.bots.add( 1 )
		self.assertEqual( self.cc.numProxies(), self.cc.bots.numBots() )

		snippet = """
		client = BigWorld.bots.values()[-1]
		client.setConnectionLossRatio( %s )
		client.setConnectionLatency( %s, %s )
		srvtest.finish()
		""" % (LOSS_RATIO, LOSS_LATENCY_MIN, LOSS_LATENCY_MAX)
		self.cc.sendAndCallOnApp( "bots", snippet = snippet )

		self.cc.bots.delete( 1 )
		self.assertDisconnectionRequested()
