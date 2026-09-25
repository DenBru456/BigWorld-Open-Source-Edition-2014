import time

from tests.watchers.test_common import TestCommon
from bwtest import TestCase
from helpers.command import Command, CommandError

from primitives import locallog


class TestGeneral( TestCommon, TestCase ):
	
	
	tags = []
	name = "Test general watchers"
	description = "Tests the functionality of the following watchers:\
	id, isProduction, isServiceApp, load, numBases, numProxies, \
	pythonServerPort, backedUpBaseApps/numEntitiesBackedUp, version"
	process = "baseapp"
	
	
	def runTest( self ):
		appId = self._cc.getWatcherValue( "id", self.process, 1 )
		self.assertTrue( int( appId ) == 1, "id watcher at incorrect value" )
		isProduction = self._cc.getWatcherValue( "isProduction", self.process )
		self.assertFalse( isProduction,
						"isProduction watcher at incorrect value" )
		isServiceApp = self._cc.getWatcherValue( "isServiceApp", self.process )
		self.assertFalse( isServiceApp,
						"isServiceApp watcher at incorrect value" )
		
		pythonServerPort = self._cc.getWatcherValue( "pythonServerPort",
													 self.process )
		cmd = Command()
		try:
			cmd.call( "nc -z %s %s" % ( self._cc._machines[0], 
									pythonServerPort ) )
		except CommandError:
			self.assertTrue( False, "pythonServerPort was not open" )
		procOrd = 1
		numBases = self._cc.waitForWatcherValue( "numBases", "1", 
												self.process, procOrd )
		if not numBases:
			procOrd = 2
			numBases = self._cc.waitForWatcherValue( "numBases", "1", 
													self.process, procOrd )
		numEntitiesBackedUp = self._cc.waitForWatcherValue( 
								"backedUpBaseApps/numEntitiesBackedUp", "1", 
								self.process, (procOrd % 2 ) + 1 )
		self.assertTrue( numBases and numEntitiesBackedUp,
			"numBases watcher and numEntitiesBackedUp watcher didn't match" )
		
		self._cc.killProc( "baseapp", 2 )
		oldLoad = self._cc.getWatcherValue( "load", self.process )
		oldNumProxies = self._cc.getWatcherValue("numProxies", self.process)
		self.assertTrue( int( oldNumProxies ) == 0,
						"numProxies watcher value was not 0")
		self._cc.startProc( "bots" )
		self._cc.bots.add( 20 )
		newLoad = self._cc.getWatcherValue( "load", self.process )
		newNumProxies = self._cc.getWatcherValue("numProxies", self.process)
		self.assertTrue( float( newLoad ) > float( oldLoad ),
						"Load watcher didn't increase when adding bots" )
		self.assertTrue( int( newNumProxies ) == 20,
						"numProxies value was not 20")
		
		versionMajor = self._cc.getWatcherValue( "version/major", self.process, 1 )
		versionMinor = self._cc.getWatcherValue( "version/minor", self.process, 1 )
		versionPatch = self._cc.getWatcherValue( "version/patch", self.process, 1 )
		versionString = self._cc.getWatcherValue( 
												"version/string", self.process, 1 )
		
		composedString = ".".join( [versionMajor, versionMinor, versionPatch] )
		self.assertTrue( versionString == composedString, 
						"Unexpected values in versions" )
		
		
class TestNubOutput( TestCommon, TestCase):
	
	
	tags = []
	name = "Test isVerbose nub watcher"
	description = "Test that setting isVerbose has an impact on log output"
	process = "baseapp"


	def runTest( self ):
		isVerbose = self._cc.getWatcherData( "nub/isVerbose", self.process, 1 )
		dropPerMillion = self._cc.getWatcherData(
										"nub/artificialLoss/dropPerMillion", 
										self.process, 1)
		dropPerMillion.set( 100000 )
		
		isVerbose.set( "True" )
		time.sleep( 12 )
		output = locallog.grepLastServerLog( 
							"Resent unacked packet", 10, "BaseApp" )
		self.assertTrue( len( output ) > 0, 
						"No log output when verbose set to True")
		
		isVerbose.set( "False" )
		time.sleep( 12 )
		output = locallog.grepLastServerLog( 
							"Resent unacked packet", 10, "BaseApp" )
		self.assertTrue( len( output ) == 0, 
						"Log output when verbose set to False")
		dropPerMillion.set( 0 )
		
		
class TestProfilerWatcher( TestCommon, TestCase ):
	
	
	tags = []
	name = "Profiler watcher"
	description = "Tests that enabling the profiler generates statistics"
	
	
	def runTest( self ):
		time.sleep(3)
		enabled = self._cc.getWatcherData("profiler/enabled", "baseapp")
		statistics = self._cc.getWatcherData(
							"profiler/statistics", "baseapp").getChildren()
		
		originalLength = len( statistics )
		timeVal = statistics[-3].value.strip().split()[-1]
		profiles = statistics[-2].value.strip().split()[0]
		displays = statistics[-1].value.strip().split()[0]
		self.assertTrue( timeVal == "0.00ms", 
						"Disabled profiler spent time profiling" )
		self.assertTrue( profiles == "0",
						"Disabled profiler had profile entries" )
		self.assertTrue( displays == "0", 
						"Disabled profiled had display entries" )

		enabled.set( "True" )
		time.sleep( 3 )
		statistics = self._cc.getWatcherData(
							"profiler/statistics", "baseapp").getChildren()
		newLength = len( statistics )
		timeVal = statistics[-3].value.strip().split()[-1]
		profiles = statistics[-2].value.strip().split()[0]
		displays = statistics[-1].value.strip().split()[0]
		self.assertTrue( timeVal != "0.00ms", 
						"Enabled profiler spent no time profiling" )
		self.assertTrue( profiles != "0",
						"Enabled profiler had no profile entries" )
		self.assertTrue( displays != "0", 
						"Enabled profiled had no display entries" )
		self.assertTrue( newLength > originalLength,
						"Statistics not refreshed when profiler enabled" )
		
		
class TestProxiesWatcher( TestCommon, TestCase ):
	
	
	tags = []
	name = "Proxies watcher"
	description = "Test that adding a bunch of bots creates watchers for them"
	
	
	def runTest( self ):
		proxies = self._cc.getWatcherData( "proxies", "baseapp").getChildren()
		self.assertTrue( len( proxies ) == 0,
						"Proxies existed on a freshly started server")
		self._cc.startProc( "bots", 1)
		self._cc.bots.add( 10 )
		time.sleep( 3 )
		proxies = self._cc.getWatcherData( "proxies", "baseapp").getChildren()
		self.assertTrue( len( proxies ) != 0,
						"Proxies watchers not created after adding bots")
		

		