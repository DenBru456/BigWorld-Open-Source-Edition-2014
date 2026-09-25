import bwtest
from helpers.cluster import ClusterController


class DBAppRegistrationTest( bwtest.TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		"""
		Check DBAppMgr handles DBApp birth, allocates appID, and handles death
		"""

		# Check registration on startup
		numDBApps = self.cc.getWatcherValue( "numDBApps", "dbappmgr", None )
		self.assertEqual( int( numDBApps ), 1 )

		appID = self.cc.getWatcherValue( "id", "dbapp", None )
		self.assertEqual( appID, 1 )

		# Check deregistration
		self.cc.killProc( "dbapp" )

		numDBApps = self.cc.getWatcherValue( "numDBApps", "dbappmgr", None )
		self.assertEqual( int( numDBApps ), 0 )

		# Check registration
		self.cc.startProc( "dbapp" )

		numDBApps = self.cc.getWatcherValue( "numDBApps", "dbappmgr", None )
		self.assertEqual( int( numDBApps ), 1 )

		appID = self.cc.getWatcherValue( "id", "dbapp", None  )
		self.assertEqual( appID, 2 )
