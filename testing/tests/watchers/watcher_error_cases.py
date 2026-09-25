from bwtest import TestCase
from helpers.cluster import ClusterController
from primitives import locallog
from pycommon.watcher_call_base import WatcherCallException

class SetErrorCasesTest( TestCase ):
	
	
	name = "SetErrorCases"
	description = "Tests invalid values when setting watchers"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		result = self.cc.setWatcher( "id", "abc", "baseapp", 1 )
		id = self.cc.getWatcherValue( "id", "baseapp", 1 )
		self.assertTrue( int(id) == 1,
						"Watcher id was set with invalid value: %s" % id )
		result = self.cc.setWatcher( "some/path/to/watcher", "abc", "baseapp", 1 )
		self.assertFalse( result, "Was able to set non-existent watcher" )


class GetErrorCasesTest( TestCase ):
	
	
	name = "GetErrorCases"
	description = "Tests invalid values when getting watchers"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		watcher = self.cc.getWatcherValue( "some/path/to/watcher", "baseapp", 1 )
		self.assertTrue( watcher == None,
						"Was able to get a non-existent watcher" )


class CallErrorCasesTest( TestCase ):
	
	
	name = "CallErrorCases"
	description = "Tests invalid values when calling watchers"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		exception = False
		try:
			self.cc.callWatcher( "baseapp", "someNonsenseWatcher", 1 )
		except WatcherCallException:
			exception = True
		self.assertTrue( exception,
				"Calling non-existent watcher did not raise appropriate error" )
		
		snippet = """
		def functionWatcher( param1, param2 ):
			print "FunctionWatcher called with param1 %s, "\
				"param2 %s" % ( param1, param2 )
			return "ok:"
		BigWorld.addFunctionWatcher( "command/functionWatcher", functionWatcher,
					[("Param1", int ), ("Param2", int )], 
					BigWorld.EXPOSE_LEAST_LOADED, "" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet)
		
		exception = False
		try:
			self.cc.callWatcher( "baseapp", "functionWatcher", 1, "abc", "abc" )
		except WatcherCallException:
			exception = True
		self.assertTrue( exception,
						"Calling watcher with invalid parameter type"\
						" did not raise appropriate error" )
		exception = False
		try:
			self.cc.callWatcher( "baseapp", "functionWatcher", 1, 2 )
		except WatcherCallException:
			exception = True
		self.assertTrue( exception,
						"Calling watcher with missing parameters"\
						" did not raise appropriate error" )
		self.cc.callWatcher( "baseapp", "functionWatcher", 1, 3, 5, 7 )
		out = locallog.grepLastServerLog( 
							"FunctionWatcher called with param1 3, param2 5" )
		self.assertTrue( len( out ) > 0,
						"Watcher wasn't called with too many parameters" )
		
		
			
		
		