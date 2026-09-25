import time

from tests.watchers.test_common import TestCommon
from bwtest import TestCase


class TestBackedUpBaseApps( TestCommon, TestCase ):
	
	
	tags = []
	name = "backedUpBaseApps"
	description = "Test functionality of the backedUpBaseApps watchers"
	process = "baseapp"
	
	ARCHIVE_PERIOD = 5
	BACKUP_PERIOD = 5
	
	
	def setUp( self ):
		self.NEEDED_CONFIGS[ "baseApp/backupPeriod" ] = str( self.BACKUP_PERIOD )
		TestCommon.setUp( self )

	def runTest( self ):
		procOrd = 1
		ret = self._cc.waitForWatcherValue( "backedUpBaseApps/numEntitiesBackedUp", "1", self.process )
		if not ret:
			procOrd = 2
			ret = self._cc.waitForWatcherValue( "backedUpBaseApps/numEntitiesBackedUp", "1", self.process, 2 )
		self.assertTrue( ret, "No backed up entities" )
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

		time.sleep( self.ARCHIVE_PERIOD * 2)
		for procOrd in range( 1, 7 ):
			apps = self._cc.getWatcherData( "backedUpBaseApps/apps", self.process, procOrd ).getChildren()
			numEntitiesBackedUp = int( self._cc.getWatcherValue( "backedUpBaseApps/numEntitiesBackedUp", self.process, procOrd ) )
			someoneUsingNew = self.checkIsUsingNew( apps )
			totalBackedUp, totalNewBackedUp = self.checkApps( apps )
			self.assertTrue( totalBackedUp + totalNewBackedUp == numEntitiesBackedUp, "Backed up entity values are inconsistent" )
			self.assertTrue( someoneUsingNew or totalNewBackedUp == 0, "New backup count and isUsingNew mismatch" )
			
			
	
	def checkIsUsingNew( self, apps):
		someoneUsingNew = False
		for app in apps:
			isUsingNew = app.getChild( "isUsingNew" ).value
			someoneUsingNew = someoneUsingNew or isUsingNew
		return someoneUsingNew

	def checkApps( self, apps ):
		totalBackedUp = 0
		totalNewBackedUp = 0
		for app in apps:
			numInCurrentBackup = app.getChild( "numInCurrentBackup" ).value
			numInNewBackup = app.getChild( "numInNewBackup" ).value
			totalBackedUp += int( numInCurrentBackup )
			totalNewBackedUp += int( numInNewBackup )
			
			currentBackup = app.getChild( "currentBackup" )
			currentBackupEntities = currentBackup.getChild( "numEntities" ).value
			self.assertTrue( int( currentBackupEntities ) == int( numInCurrentBackup ),
							 "currentBackup size did not match numInCurrentBackup" )
			numInvalids = currentBackup.getChild( "numInvalids" ).value
			self.assertTrue( int( numInvalids ) == 0,
							"numInwalids was not 0")
			
			
			hashWatcher = currentBackup.getChild( "hash" )
			hashPrime = long( hashWatcher.getChild( "prime" ).value )
			self.assertTrue( self.isPrime(hashPrime), "Hash prime value not a prime number")

			hashSize = hashWatcher.getChild( "impliedVirtualSize" ).value
			self.assertTrue( self.isPowerOfTwo( int( hashSize ) ), 
				"Hash size was not a power of two. Was %s" % hashSize )
		return totalBackedUp, totalNewBackedUp
		
		
			
		
		