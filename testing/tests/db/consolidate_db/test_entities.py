import time
import test_base

from bwtest import TestCase, log
from primitives import mysql


class TestConsolidateAllEntities( test_base.TestBase, TestCase ):
	
	
	tags = []
	name = "Consolidate all entities"
	description = "All entities in the secondary databases are consolidated"


	def runTest( self ):
		self._cc.start()
		snippet = """
persistents = []
for i in range( 8 ):
	e = BigWorld.createEntity( "PersistentEntity" )
	persistents.append( e )
persistents[0].writeToDB()
persistents[1].writeToDB()
srvtest.finish( [e.id for e in persistents] )
"""
		persistentIDs = self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		time.sleep( self.ARCHIVE_PERIOD )
		
		snippet = """
persistentIDs = {persistentIDs}
persistents = []
for id in persistentIDs:
	persistents.append( BigWorld.entities[id] )
persistents[2].writeToDB()
persistents[3].writeToDB()
srvtest.finish()
"""
		self._cc.sendAndCallOnApp( "baseapp", 1, snippet, 
								persistentIDs = persistentIDs )
		self._cc.stop( timeout = 60 )
		secDBFiles = self._cc.getSecondaryDBFiles()
		self.assertTrue( len( secDBFiles ) == 0, 
						"Secondary DB files still present after shutdown" )


class TestLatestEntityUpdate( test_base.TestBase, TestCase ):

	
	tags = []
	name = "Latest entity update"
	description = "When the secondary database contains multiple entries\
				 for the same entity, the latest one is used"


	def runTest( self ):
		self._cc.start()
		snippet = """
def onCreate( *args ):
	srvtest.finish( e.databaseID )

e = BigWorld.createEntity( "PersistentEntity" )
e.writeToDB()
e.cellData[ "persistentProp" ] = 6
e.writeToDB()
e.cellData[ "persistentProp" ] = 7
e.writeToDB( onCreate, True )
"""
		log.debug( "Calling --<%s>-- on baseapp01" % snippet )
		dbId = self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		self._cc.stop( timeout = 60 )
		result = mysql.executeSQL( 
		"SELECT sm_persistentProp FROM tbl_PersistentEntity WHERE id = %s"
			 % dbId )
		self.assertTrue( int( result[0][0] ) == 7, 
				"Latest entry was not used. Expecting 7, found %s" % result[0] )
		
		
class TestConsolidateLoggedOut( test_base.TestBase, TestCase ):
	
	
	tags = []
	name = "Don't consolidate logged out entity"
	description = "Logged out entities with entries in the secondary database\
				  do not get consolidated"

	
	def runTest( self ):
		self._cc.start()
		snippet = """
def onCreate( *args ):
	e.cellData[ "persistentProp" ] = 9
	e.destroy()
	srvtest.finish( e.databaseID )
			
e = BigWorld.createEntity( "PersistentEntity" )
e.cellData[ "persistentProp" ] = 8
e.writeToDB( onCreate, True )
"""
		log.debug( "Calling --<%s>-- on baseapp01" % snippet )
		dbId = self._cc.sendAndCallOnApp("baseapp", 1, snippet)
		self._cc.stop( timeout = 60 )
		result = mysql.executeSQL( 
		"SELECT sm_persistentProp FROM tbl_PersistentEntity WHERE id = %s" 
			% dbId )
		self.assertTrue( int( result[0][0] ) == 9, 
				"Latest entry was not used. Expecting 9, found %s" % result[0] )
		
	
		
