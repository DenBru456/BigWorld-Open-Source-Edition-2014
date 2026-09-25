import time
from bwtest import TestCase
from helpers.cluster import ClusterController


class MapWatchersTest( TestCase ):
	
	name = "MapWatcher"
	description = "Tests the functionality of map watchers"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = "srvtest.finish( len(BigWorld.entities.items()) )"
		count = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		count2 = len( self.cc.getWatcherData( "entities", 
											"cellapp", 1 ).getChildren() )
		self.assertTrue( count2 == count,
						"Map watcher returned wrong values" )