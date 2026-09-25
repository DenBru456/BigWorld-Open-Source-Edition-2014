from bwtest import TestCase
from helpers.cluster import ClusterController
from primitives import locallog


class GetWatcherDirTest( TestCase ):
	
	
	name = "GetWatcherDir"
	description = "Tests the functionality of getWatcherDir method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = """
		srvtest.finish( BigWorld.getWatcherDir( "config/secondaryDB" ) )
		"""
		watcherDir = self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		foundEnable = False
		directory = self.cc.getWatcherValue( "config/secondaryDB/directory",
												"baseapp", 1 )
		foundDirectory = False
		for watcher in watcherDir:
			if watcher[1] == "enable":
				self.assertTrue( watcher[2] == "true",
						"getWatcherDir returned incorrect value for enable" )
				foundEnable = True
			if watcher[1] == "directory":
				self.assertTrue( watcher[2] == directory,
						"getWatcherDir returned incorrect value for directory" )
				foundDirectory = True
		self.assertTrue( foundEnable and foundDirectory,
						"getWatcherDir did not return all expected watchers")