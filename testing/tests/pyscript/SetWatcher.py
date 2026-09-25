from bwtest import TestCase
from helpers.cluster import ClusterController


class SetWatcherTest( TestCase ):
	
	
	name = "SetWatcher"
	description = "Tests the functionality of setWatcher method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = """
		BigWorld.setWatcher( "config/channelTimeoutPeriod", 30 )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		timeoutPeriod = self.cc.getWatcherValue( "config/channelTimeoutPeriod",
												"baseapp", 1 )
		self.assertTrue( timeoutPeriod == 30.0,
						"Watcher wasn't set when calling setWatcher" )