import time

from tests.watchers.test_common import TestCommon
from bwtest import TestCase


class TestBaseApps( TestCommon, TestCase ):
	
	
	tags = []
	name = "baseApps"
	description = "Test functionality of the baseApps watchers on baseappmgr"
	process = "baseappmgr"
	
	ARCHIVE_PERIOD = 5
	BACKUP_PERIOD = 5
	
	
	def setUp( self ):
		self.NEEDED_CONFIGS[ "baseApp/backupPeriod" ] = str( self.BACKUP_PERIOD )
		TestCommon.setUp( self )

	def runTest( self ):
		self._cc.startProc( "baseapp", 2 )
		snippet = """
from random import random
for i in range(20):		
	entityName = "temp%d%f" % (i, random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
srvtest.finish()
"""	
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet)
		self._cc.sendAndCallOnApp( "baseapp", 2, snippet)
		self._cc.sendAndCallOnApp( "baseapp", 3, snippet)
		self._cc.sendAndCallOnApp( "baseapp", 4, snippet)
		
		self._cc.startProc( "baseapp", 2 )
		self._cc.startProc( "bots" )
		self._cc.bots.add( 10 )

		time.sleep( self.ARCHIVE_PERIOD * 2)
		baseapps = self._cc.getWatcherData( "baseApps", self.process, None )
		numServiceApps = 0
		totalBases = int( self._cc.getWatcherValue( "numBases", self.process, None ) )
		totalProxies = int( self._cc.getWatcherValue( "numProxies", self.process, None) )
		numBases = 0
		numProxies = 0
		ids = {}
		for app in baseapps.getChildren():
			isServiceApp = app.getChild( "isServiceApp" ).value
			if isServiceApp:
				numServiceApps += 1
				continue
			nameParts = app.name.split( ":" )
			externalAddrParts = app.getChild( "externalAddr" ).value.split( ":" )
			self.assertTrue( nameParts[0] == externalAddrParts[0],
							"externalAddr does not match name" )
			
			load = app.getChild( "load" ).value
			self.assertTrue( float(load) > 0, "App did not have non-zero load")
			
			ids[app.getChild( "id" ).value] = 1
			numBases += int( app.getChild( "numBases" ).value )
			numProxies += int( app.getChild( "numProxies" ).value )
			
			backupHash = app.getChild( "backupHash" )
			backupHashPrime = int( backupHash.getChild( "prime" ).value )
			self.assertTrue( self.isPrime( backupHashPrime ))
			
			addresses = backupHash.getChild( "addresses" )
			size = backupHash.getChild( "size" ).value
			virtualSize = backupHash.getChild( "virtualSize" ).value
			
			self.assertTrue( int(size) == len( addresses.getChildren() ), 
							"Hash size doesn't match addresses length")
			self.assertTrue( int(size) <= int(virtualSize),
							"Size not smaller or equal to virtual size")
			self.assertTrue( self.isPowerOfTwo( int(virtualSize) ),
							"virtual size not a power of two" )
		
		self.assertTrue( len( ids.keys() ) == 6, "Non-unique baseapp ids")
		self.assertTrue( numServiceApps == 2, "Unexpected amount of service apps")
		self.assertTrue( numBases == totalBases, "Mismatch in numBases values")
		self.assertTrue( numProxies == totalProxies, "Mismatch in numProxies values")
		
		
			
		
		