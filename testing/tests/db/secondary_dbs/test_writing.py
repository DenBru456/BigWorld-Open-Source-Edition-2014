import bwtest
from helpers.timer import runTimer
import util
import time
from random import random

from primitives import mysql


class TestWriteToDB( util.TestBase, bwtest.TestCase  ):
	name = "BigWorld.Base.writeToDB to secondary DB"
	description = "writeToDB() goes to secondary database after commit callback"
	tags = []


	def runTest( self ):
		cc = self._cc

		entityName = "temp%f" % random()

		snippet = """
e = BigWorld.createEntity( "TestEntity", name = {entityName} )
def callback( res, ent ):
	srvtest.finish( (ent.id, ent.databaseID) )
e.writeToDB( callback )
		"""
		entityID, dbID = cc.sendAndCallOnApp( "baseapp", 1, snippet, 
										entityName = entityName )

		self.assertNotEqual( dbID, 0 )

		def getInt8():		
			res = mysql.executeSQL( 
				"SELECT sm_int8 FROM tbl_TestEntity where sm_name = '%s'" 
				% entityName )
			return res[0][0] 

		dbInt8 = getInt8()
		self.assertEqual( dbInt8, 0 )

		snippet = """
e = BigWorld.entities[{entityID}]
def callback( res, ent ):
	srvtest.finish( e.int8 )
e.int8 = 1	
e.writeToDB( callback )
		"""
		cc.sendAndCallOnApp( "baseapp", 1, snippet, entityID = entityID )

		cc.killProc( "baseapp", 1 )

		# Wait for new value to be consolidated into the primary.
		runTimer( cc.getSecondaryDBCount, 
						lambda res: res == 0 )

		dbInt8 = getInt8()
		self.assertEqual( dbInt8, 1 )


SNIPPET_CREATE_ENTITIES = """
from random import random		
createdEntities = []
def callback( res, ent ):
	srvtest.assertTrue( res )
	createdEntities.append( ent.id )
	if len( createdEntities ) == 10:
		srvtest.finish( createdEntities )

for i in range(10):		
	entityName = "temp%d%f" % (i, random())
	e = BigWorld.createEntity( "TestEntity", name = entityName )
	e.writeToDB( callback, {isPersistent} )
"""


class TestWriteToDBOnDestroy( util.TestBase, bwtest.TestCase  ):
	name = "Entity restoration writes to database"
	description = "When a base entity is restored, it is written to the database"

	tags = []


	def step1( self ):
		"""Create 10 entities on baseapp02"""
		cc = self._cc

		cc.startProc( "baseapp", 1 )

		cc.waitForApp( "baseapp", 2 )

		self.entities = cc.sendAndCallOnApp( "baseapp", 2, 
						SNIPPET_CREATE_ENTITIES,
						isPersistent = False )


	def step2( self ):
		"""Kill BaseApp where 10 entities were created"""
		cc = self._cc

		time.sleep( self.BACKUP_PERIOD )

		cc.killProc( "baseapp", 2 )

		time.sleep( self.BACKUP_PERIOD )


	def step3( self ):
		"""
		Check whether all the entities have been restored
		on the other BaseApp
		"""
		cc = self._cc

		snippet = """
dbIDs = []		
ids = {entities}

for id in ids:		
	e = BigWorld.entities[ id ]
	srvtest.assertTrue( e.databaseID > 0 )
	dbIDs.append( e.databaseID )
srvtest.finish( dbIDs )	
"""
		self.dbIds = cc.sendAndCallOnApp( "baseapp", 1, snippet,
										entities = self.entities )


	def step4( self ):
		"""Check the entities were written to the database"""

		res = mysql.executeSQL( 
				"SELECT id FROM tbl_TestEntity" )

		readIds = [ t[0] for t in res ]
		for id in self.dbIds:
			self.assertTrue( id in readIds )



