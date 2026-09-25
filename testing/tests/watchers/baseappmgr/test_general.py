import time
from bwtest import TestCase
from tests.watchers.test_common import TestCommon
from primitives import locallog


class TestGeneral( TestCommon, TestCase ):
	
	tags = []
	name = "Test general watchers"
	description = "Tests the functionality of the following watchers:\
	isProduction, numBaseApps, numBases, numProxies, numServiceApps, \
	lastBaseAppIDAllocated, lastServiceAppIDAllocated, version, baseAppLoad"
	process = "baseappmgr"
	NUM_BASE_APPS = 2
	LAST_BASE_APP_ID = 2
	NUM_SERVICE_APPS = 2
	LAST_SERVICE_APP_ID = 2
	
	def runTest( self ):
		self._cc.waitForServerSettle()
		isProduction = self._cc.getWatcherValue( "isProduction", 
												 self.process, None )
		self.assertFalse( isProduction,
						"isProduction watcher at incorrect value" )
		
		versionMajor = self._cc.getWatcherValue( "version/major", 
												 self.process, None )
		versionMinor = self._cc.getWatcherValue( "version/minor", 
												 self.process, None )
		versionPatch = self._cc.getWatcherValue( "version/patch", 
												 self.process, None )
		versionString = self._cc.getWatcherValue( "version/string", 
												  self.process, None )
		
		composedString = ".".join( [versionMajor, versionMinor, versionPatch] )
		self.assertTrue( versionString == composedString, 
						"Unexpected values in versions" )
		
		numBaseApps =  self._cc.getWatcherValue( "numBaseApps", 
												 self.process, None )
		self.assertTrue( int( numBaseApps ) ==  self.NUM_BASE_APPS, 
						"numBaseApps Watcher incorrect" )
		numServiceApps =  self._cc.getWatcherValue( "numServiceApps", 
												 self.process, None )
		self.assertTrue( int( numServiceApps ) ==  self.NUM_SERVICE_APPS, 
						"numServiceApps Watcher incorrect" )
		numBases = self._cc.getWatcherValue( "numBases", self.process, None )
		self.assertTrue( int( numBases ) == 1, 
						"numBases watcher incorrect")
		numProxies = self._cc.getWatcherValue( "numProxies", 
											   self.process, None )
		self.assertTrue( int( numProxies ) == 0, 
						"numProxies watcher incorrect")
		lastBaseAppId = self._cc.getWatcherValue( 
										"lastBaseAppIDAllocated", 
										self.process, None )
		self.assertTrue( int( lastBaseAppId ) == self.LAST_BASE_APP_ID ,
						"lastBaseAppIDAllocated watcher incorrect" )

		lastServiceAppId = self._cc.getWatcherValue( 
										"lastServiceAppIDAllocated", 
										self.process, None )
		self.assertTrue( int( lastServiceAppId ) == self.LAST_SERVICE_APP_ID,
						"lastServiceAppIDAllocated watcher incorrect" )
		
		baseAppLoad = self._cc.getWatcherData( "baseAppLoad", 
											self.process, None )
		maxLoad = baseAppLoad.getChild( "max" ).value
		minLoad = baseAppLoad.getChild( "min" ).value	
		averageLoad = baseAppLoad.getChild( "average" ).value
		
		self._cc.startProc( "baseapp", 1 )
		self._cc.startProc( "bots", 1 )
		self._cc.bots.add( 20 )
		numBaseApps =  self._cc.getWatcherValue( "numBaseApps", 
												self.process, None )
		self.assertTrue( int( numBaseApps ) ==  (self.NUM_BASE_APPS + 1), 
						"numBaseApps Watcher incorrect" )
		numBases = self._cc.getWatcherValue( "numBases", self.process, None )
		self.assertTrue( int( numBases ) == 21, 
						"numBases watcher incorrect")
		numProxies = self._cc.getWatcherValue( "numProxies", 
											self.process, None )
		self.assertTrue( int( numProxies ) == 20, 
						"numProxies watcher incorrect")
		lastBaseAppId = self._cc.getWatcherValue( 
										"lastBaseAppIDAllocated", 
										self.process, None )
		self.assertTrue( int( lastBaseAppId ) == self.LAST_BASE_APP_ID + 1 ,
						"lastBaseAppIDAllocated watcher incorrect" )
		
		newMaxLoad = baseAppLoad.getChild( "max" ).value
		self.assertTrue( float( newMaxLoad ) > float( maxLoad ),
						"max baseAppLoad did not increase when adding bots" )
		
		newMinLoad = baseAppLoad.getChild( "min" ).value
		self.assertTrue( float( newMinLoad ) > float( minLoad ),
						"min baseAppLoad did not increase when adding bots" )

		newAverageLoad = baseAppLoad.getChild( "average" ).value
		self.assertTrue( float( newAverageLoad ) > float( averageLoad ),
					"average baseAppLoad did not increase when adding bots" )
		
		
class TestNubOutput( TestCommon, TestCase):
	
	
	tags = ["STAGED"]
	name = "Test isVerbose nub watcher"
	description = "Test that setting isVerbose has an impact on log output"
	process = "baseappmgr"


	def runTest( self ):
		isVerbose = self._cc.getWatcherData( "nub/isVerbose", 
											self.process, None )
		dropPerMillion = self._cc.getWatcherData(
										"nub/artificialLoss/dropPerMillion", 
										self.process, None)
		dropPerMillion.set( 900000 )
		
		isVerbose.set( "True" )
		time.sleep( 10 )
		dropPerMillion.set( 0 )
		time.sleep( 5 )
		output = locallog.grepLastServerLog( 
							"Resent unacked packet", 14, "BaseAppMgr" )
		self.assertTrue( len( output ) > 0, 
						"No log output when verbose set to True")
		
		dropPerMillion.set( 900000 )
		
		isVerbose.set( "False" )
		time.sleep( 10 )
		dropPerMillion.set( 0 )
		time.sleep( 5 )
		output = locallog.grepLastServerLog( 
							"Resent unacked packet", 14, "BaseAppMgr" )
		self.assertTrue( len( output ) == 0, 
						"Log output when verbose set to False")
		
		
		
