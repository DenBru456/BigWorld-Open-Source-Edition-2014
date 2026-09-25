import time

from tests.watchers.test_common import TestCommon
from bwtest import TestCase

EXPECTED_ARCHIVE_SIZES = [48, 63]
EXPECTED_BACKUP_SIZE = 82
BASE_PROP_VALUE = 8

class TestEntitiesWatcher( TestCommon, TestCase ):
	
	
	tags = []
	name = "Test of entities watcher"
	description = "Test that the profile of an entity updates \
	when it is given load"
	
	
	def setUp( self ):
		self.NEEDED_CONFIGS[ "allowInteractiveDebugging" ] = "true"
		TestCommon.setUp( self )
		

	def runTest( self ):
		self.assertTrue( self._cc.getConfig( "dbApp/type", "mysql") == "mysql",
						"This test requires MySQL DB configuration" )
		self._cc.waitForServerSettle()
		
		snippet = \
"""
def onCreate( *args ):
	import time
	startTime = time.time()
	x = 0
	while True:
		x += 1
		time.sleep( 0.1 )
		if time.time() - startTime > 5:
			break

e = BigWorld.createEntity( "PersistentEntity" )
e.baseProp = %s
srvtest.finish()
e.writeToDB( onCreate, True )
""" % BASE_PROP_VALUE
		self._cc.sendAndCallOnApp("baseapp", 1, snippet)
		
		loads = { 0.0: 1 }
		maxLoads = { 0.0: 1 }
		for i in range( 30 ):
			entities = self._cc.getWatcherData( "entities", "baseapp", 1 )
			entities = entities.getChildren()
			persistentEntity = None
			for entity in entities:
				entityType = entity.getChild( "type" ).value
				if entityType == "PersistentEntity":
					persistentEntity = entity
		
			self.assertTrue( persistentEntity, 
						"Entity not created or type incorrect")
		
			profile = persistentEntity.getChild( "profile" )
			load, maxLoad = self.getLoads( profile )
			loads[ load ] = 1
			maxLoads[ maxLoad ] = 1
			
			
			properties = persistentEntity.getChild( "properties" )
			persistentProp = properties.getChild( "baseProp" ).value
			self.assertTrue( int( persistentProp ) == BASE_PROP_VALUE, 
							"Property persistentProp watcher incorrect")
			archiveSize = persistentEntity.getChild( "archiveSize" ).value
			backupSize = persistentEntity.getChild( "backupSize" ).value
			self.assertTrue( int( archiveSize ) in EXPECTED_ARCHIVE_SIZES,
							"Archive different size than expected. Was %s"
							% archiveSize)
			self.assertTrue( int( backupSize ) == EXPECTED_BACKUP_SIZE,
							"Backup different size than expected. Was %s" 
							% backupSize )
			time.sleep( 0.1 )
		
		self.assertTrue( len( loads ) > 1, "Load watcher never updated")
		self.assertTrue( len( maxLoads ) > 1, "Maxload watcher never updated")
			
		
		
	def getLoads( self, profile ):
		load = profile.getChild( "load" ).value
		maxLoad = profile.getChild( "maxLoad" ).value
		
		return load, maxLoad
	

class TestEntityTypesWatcher( TestCommon, TestCase ):
	
	
	tags = []
	name = "Test of entity types watcher"
	description = "Test the various entity type watcher values"
	

	def runTest( self ):
		self._cc.waitForServerSettle()
		self.assertTrue( self._cc.getConfig( "dbApp/type", "mysql") == "mysql",
						"This test requires MySQL DB configuration" )
		
		snippet = \
"""
e = BigWorld.createEntity( "PersistentEntity" )
e.baseProp = %s
e.writeToDB()
srvtest.finish()
""" % BASE_PROP_VALUE
		self._cc.sendAndCallOnApp("baseapp", 1, snippet)
		
		persistentEntityData = self._cc.getWatcherData( 
											"entityTypes/PersistentEntity", 
											"baseapp", 1 )
		averageArchiveSize = int( persistentEntityData.getChild( 
												"averageArchiveSize" ).value )
		self.assertTrue( averageArchiveSize in EXPECTED_ARCHIVE_SIZES,
						"Average archive size was not of expected value. Was %s"
						% averageArchiveSize )
		averageBackupSize = int( persistentEntityData.getChild( 
												"averageBackupSize" ).value )
		self.assertTrue( averageBackupSize == EXPECTED_BACKUP_SIZE,
						"Average backup size was not of expected value" )
		
		backupSize = int( persistentEntityData.getChild( 
												"backupSize" ).value )
		self.assertTrue( backupSize == EXPECTED_BACKUP_SIZE,
						"Average backup size was not of expected value. Was %s" )
		isProxy = persistentEntityData.getChild( "isProxy" ).value
		self.assertFalse( bool( isProxy ), 
						"isProxy set to true when it shouldn't" )
		numberOfInstances = int( persistentEntityData.getChild( 
												"numberOfInstances" ).value )
		self.assertTrue( numberOfInstances == 1,
						"Unexpected number of instances found" )
		totalArchiveSize = int( persistentEntityData.getChild( 
												"totalArchiveSize" ).value )
		self.assertTrue( totalArchiveSize in EXPECTED_ARCHIVE_SIZES,
						"Total archive size was not of expected value" )
		typeID = int( persistentEntityData.getChild( "typeID" ).value )
		self.assertTrue( typeID == 2, "Unexpected type ID" )
		
		methodTypes = persistentEntityData.getChild( "methods" ).getChildren()
		for methodType in methodTypes:
			methods = methodType.getChildren()
			self.assertTrue( len( methods ) == 0, 
					"Found method watchers when no methods should be defined")
		
		
		
		

