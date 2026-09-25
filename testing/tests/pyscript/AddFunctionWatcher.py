from bwtest import TestCase
from helpers.cluster import ClusterController
from primitives import locallog


class AddFunctionWatcherTest( TestCase ):
	
	
	name = "AddFunctionWatcher"
	description = "Tests the functionality of addWatcher method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = """
		def functionWatcher( param ):
			print "FunctionWatcher called with param %s" % param
			return "ok:"
		BigWorld.addFunctionWatcher( "command/functionWatcher", functionWatcher,
					[("Parameter", int )], BigWorld.EXPOSE_LEAST_LOADED, "" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet)
		self.cc.callWatcher( "baseapp", "functionWatcher", 1, 5 )
		output = locallog.grepLastServerLog( "FunctionWatcher called with param 5" )
		self.assertTrue( len( output ) > 0,
						"Added function watcher wasn't called" )