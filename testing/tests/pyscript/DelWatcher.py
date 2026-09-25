from bwtest import TestCase
from helpers.cluster import ClusterController


class DelWatcherTest( TestCase ):
	
	
	name = "DelWatcher"
	description = "Tests the functionality of delWatcher method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		allowDebug = self.cc.getWatcherValue( "config/allowInteractiveDebugging",
											"baseapp", 1 )
		self.assertTrue( allowDebug != None,
						"Watcher allowInteractiveDebugging didn't exist")
		archivePeriod = self.cc.getWatcherValue( "config/archivePeriodInTicks",
											"baseapp", 1 )
		self.assertTrue( archivePeriod != None,
						"Watcher archivePeriodInTicks didn't exist")
		snippet = """
		BigWorld.delWatcher( "config/allowInteractiveDebugging" )
		BigWorld.delWatcher( "config/archivePeriodInTicks" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		allowDebug = self.cc.getWatcherValue( "config/allowInteractiveDebugging",
											"baseapp", 1 )
		self.assertTrue( allowDebug == None,
						"Watcher allowInteractiveDebugging wasn't deleted")
		archivePeriod = self.cc.getWatcherValue( "config/archivePeriodInTicks",
											"baseapp", 1 )
		self.assertTrue( archivePeriod == None,
						"Watcher archivePeriodInTicks wasn't deleted")