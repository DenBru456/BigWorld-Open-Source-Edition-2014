import time
import bwtest
from helpers.cluster import ClusterController

from pycommon.watcher_call import WatcherCall, watcherFunctions

NUM_BASE_APPS = 3
NUM_SERVICE_APPS = 4

BASE_APPS = "command/baseApps"
SERVICE_APPS = "command/serviceApps"
BASE_SERVICE_APPS = "command/baseServiceApps"
LEAST_LOADED = "command/leastLoaded"


class Watcher( object ):

	def __init__( self, user, path, procType ):
		self.results = []
		self.watcherCall = WatcherCall( user, path, procType )

	def execute( self ):
		self.watcherCall.execute( [], self )

	def addResult( self, result ):
		self.results.append( result )

	def addOutput( self, output ):
		pass

	def addErrorMessage( self, message, *args ):
		pass

	def baseAppResults( self ):
		return len( [r for r in self.results if r.startswith( "BaseApp" )] )

	def serviceAppResults( self ):
		return len( [r for r in self.results if r.startswith( "ServiceApp" )] )
	
	def baseAppIDs( self ):
		return [r.split()[1][:-1] for r in self.results if r.startswith( "BaseApp" )]


class WatcherExposeFlagTest( bwtest.TestCase ):
	name = "WatcherExposeFlagTest"
	description = "Test watcher expose flags"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "baseapp", NUM_BASE_APPS - 1 )
		self.cc.startProc( "serviceapp", NUM_SERVICE_APPS - 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		user = self.cc.getUser()

		# EXPOSE_BASE_SERVICE_APPS
		watcher = Watcher( user, BASE_SERVICE_APPS, "baseapp" )
		watcher.execute()
		self.assertEqual( watcher.baseAppResults(), NUM_BASE_APPS,
				"%s expected %s BaseApp results, recieved %s" % (
					BASE_SERVICE_APPS, NUM_BASE_APPS,
					watcher.baseAppResults() ) )

		watcher = Watcher( user, BASE_SERVICE_APPS, "serviceapp" )
		watcher.execute()
		self.assertEqual( watcher.serviceAppResults(), NUM_SERVICE_APPS,
				"%s expected %s ServiceApp results, recieved %s" % (
					BASE_SERVICE_APPS, NUM_SERVICE_APPS,
					watcher.serviceAppResults() ) )

		# EXPOSE_BASE_APPS
		watcher = Watcher( user, BASE_APPS, "baseapp" )
		watcher.execute()
		self.assertEqual( watcher.baseAppResults(), NUM_BASE_APPS,
				"%s expected %s BaseApp results, recieved %s" % (
					BASE_APPS, NUM_BASE_APPS, watcher.baseAppResults() ) )

		watcher = Watcher( user, BASE_APPS, "serviceapp" )
		watcher.execute()
		self.assertEqual( watcher.serviceAppResults(), 0,
				"%s expected %s ServiceApp results, recieved %s" % (
					BASE_APPS, 0, watcher.serviceAppResults() ) )

		# EXPOSE_SERVICE_APPS
		watcher = Watcher( user, SERVICE_APPS, "baseapp" )
		watcher.execute()
		self.assertEqual( watcher.baseAppResults(), 0,
				"%s expected %s BaseApp results, recieved %s" % (
					SERVICE_APPS, 0, watcher.baseAppResults() ) )

		watcher = Watcher( user, SERVICE_APPS, "serviceapp" )
		watcher.execute()
		self.assertEqual( watcher.serviceAppResults(), NUM_SERVICE_APPS,
				"%s expected %s ServiceApp results, recieved %s" % (
					SERVICE_APPS, NUM_SERVICE_APPS,
						watcher.serviceAppResults() ) )

		# EXPOSE_LEAST_LOADED
		# Generate some load first
		snippet = """
		for i in range(2000):
			BigWorld.createEntity( "TestEntity" )
		srvtest.finish()
		"""
		
		for i in range( 1, NUM_BASE_APPS ):
			self.cc.sendAndCallOnApp( "baseapp", i, snippet )
		time.sleep( 2 )
		#Then call the watcher
		watcher = Watcher( user, LEAST_LOADED, "baseapp" )
		watcher.execute()

		# Least loaded does not go to ServiceApps
		self.assertEqual( watcher.baseAppResults(), 1,
				"%s expected %s BaseApp results, recieved %s" % (
					LEAST_LOADED, 1, watcher.baseAppResults() ) )
		baseAppCalled = watcher.baseAppIDs()[0]
		self.assertEqual( baseAppCalled, str(NUM_BASE_APPS),
					"%s expected BaseApp %s to be called, was %s" % (
						LEAST_LOADED, NUM_BASE_APPS, baseAppCalled ))
