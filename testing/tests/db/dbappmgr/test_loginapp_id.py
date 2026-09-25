import bwtest
from helpers.cluster import ClusterController


class LoginAppIDTest( bwtest.TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		"""
		Check ID allocated to LoginApps continue across DBAppMgr death.
		"""

		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 1 )
		self.assertEqual( loginAppID, 1 )

		self.cc.startProc( "loginapp" )
		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 2 )
		self.assertEqual( loginAppID, 2 )

		self.cc.startProc( "loginapp" )
		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 3 )
		self.assertEqual( loginAppID, 3 )

		# Kill first DBAppMgr, start second DBAppMgr
		self.cc.killProc( "dbappmgr" )
		self.cc.startProc( "dbappmgr" )

		self.cc.startProc( "loginapp" )
		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 4 )
		self.assertEqual( loginAppID, 4 )

		self.cc.startProc( "loginapp" )
		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 5 )
		self.assertEqual( loginAppID, 5 )

		# Start third DBAppMgr, second DBAppMgr shutdowns via birth listener
		self.cc.startProc( "dbappmgr" )

		self.cc.startProc( "loginapp" )
		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 6 )
		self.assertEqual( loginAppID, 6 )

		self.cc.startProc( "loginapp" )
		loginAppID = self.cc.getWatcherValue( "id", "loginapp", 7 )
		self.assertEqual( loginAppID, 7 )
