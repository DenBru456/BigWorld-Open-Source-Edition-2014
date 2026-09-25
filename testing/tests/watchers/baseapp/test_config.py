from tests.watchers.test_common import TestCommon
from bwtest import TestCase


class TestConfig( TestCommon, TestCase):
	
	
	tags = []
	name = "Test config watchers"
	description = "Test that the watcher values of config are the same\
	 as the ones we see through pycommon.bwconfig"
	
	
	def runTest( self ):
		configWatchers = self._cc.getWatcherData( "config", "baseapp" )
		self.checkWatchersRecursive( configWatchers, "baseApp" )
		
	
	def checkWatchersRecursive( self, watchers, currentPath ):
		for watcher in watchers.getChildren():
			if watcher.isDir():
				self.checkWatchersRecursive( watcher, 
										currentPath + "/" + watcher.name )
			else:
				conf = self._cc.getConfig(currentPath + "/" + watcher.name)
				if conf != None:
					ret = self.compareValues( watcher.value, conf)
					self.assertTrue( ret, 
							"Config watcher value did not match XML config: %s" 
							% watcher.name)
	
	
	def compareValues(self, watcher, config):
		if type( watcher ) == type( False ):
			config = config =="true"
		elif type( watcher ) == type( 1 ):
			config = int( config )
		elif type( watcher ) == type( long( 1 ) ):
			config = long( config )
		elif type( watcher ) == type( 1.0 ):
			return True
		return watcher == config
	
	
class TestAllowInteractiveDebugging( TestCommon, TestCase ):

	
	tags = []
	name = "Test allowInteractiveDebugging"
	description = "Check that enabling allowInteractiveDebugging increases the\
	timeouts on the server"
	
	
	def setUp( self ):
		self.NEEDED_CONFIGS[ "allowInteractiveDebugging" ] = "true"
		TestCommon.setUp( self )

	
	def runTest( self ):
		snippet = \
"""import time
time.sleep( 20 )
srvtest.finish()
"""
		
		value = self._cc.getWatcherValue("config/allowInteractiveDebugging", "baseapp", 1)
		print value
		self._cc.sendAndCallOnApp("baseapp", 1, snippet, timeout = 30)
		