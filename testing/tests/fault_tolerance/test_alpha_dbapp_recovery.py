from bwtest import TestCase
from helpers.cluster import ClusterController


class AlphaDBAppRecoveryTest( TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()

		self.cc.waitForServerSettle()

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		"""
		Check recovered alpha DBApp can be started.
		"""

		self.cc.killProc( "dbapp" )
		self.cc.startProc( "dbapp" )

		self.cc.waitForServerSettle()

		isAlpha = self.cc.getWatcherValue( "isAlpha", "dbapp", 2 )
		self.assertTrue( isAlpha )

		isReady = self.cc.getWatcherValue( "isReady", "dbapp", 2 )
		self.assertTrue( isReady )
