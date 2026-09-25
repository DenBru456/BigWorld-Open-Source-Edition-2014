from test_case import TestCase
from test_case import fail_on_exception

import BigWorld

class WriteToDB( TestCase ):
	def run( self ):
		BigWorld.executeRawDatabaseCommand( "SELECT COUNT(*) FROM tbl_Simple",
			   self.step1 )

	@fail_on_exception
	def step1( self, resultSet, numAffectedRows, errorMsg ):
		self.assertTrue( errorMsg is None )
		self._initialRows = int( resultSet[0][0] )

		self._entity = BigWorld.createEntity( "Simple" )
		self.writeToDB()

	def writeToDB( self ):
		self._entity.writeToDB( self.step2 )

	@fail_on_exception
	def step2( self, isOkay, entity ):
		self.assertNotEqual( self._entity.databaseID, 0 )
		self.assertEqual( self._entity.id, entity.id )
		BigWorld.executeRawDatabaseCommand( "SELECT COUNT(*) FROM tbl_Simple",
			   self.step3 )

	@fail_on_exception
	def step3( self, resultSet, numAffectedRows, errorMsg ):
		self.assertTrue( errorMsg is None )
		finalRows = int( resultSet[0][0] )
		self.assertEqual( self._initialRows + 1, finalRows )
		self.finishTest()

class WriteToDBTwice( WriteToDB ):
	def writeToDB( self ):
		self._entity.writeToDB()
		self._entity.writeToDB( self.step2 )

class WriteToDBAndDestroy( WriteToDB ):
	def writeToDB( self ):
		self._entity.writeToDB( self.step2 )
		self._entity.destroy()

# Tests the three different result types from:
# BigWorld.lookUpBaseByDBID and BigWorld.createBaseLocallyFromDBID
class LookUpEntity( TestCase ):
	EXCLUDE_TEST = True

	def __init__( self ):
		TestCase.__init__( self )

	def run( self ):
		self._entity = self.createEntity()
		# BigWorld.createEntity( self.entityType, myIdentifier = self.id() )
		self._entity.writeToDB( self.step1 )

	@fail_on_exception
	def step1( self, isOkay, entity ):
		self.assertTrue( isOkay )
		self.assertEqual( self._entity.id, entity.id )
		self._databaseID = self._entity.databaseID
		self.onWriteToDBSuccess()
		self.lookUpFunc( self.entityType, self.id(), self.step2 )

	def onWriteToDBSuccess( self ):
		pass

	@fail_on_exception
	def step2( self, result ):
		# Should have found the active entity
		self.assertEqual( result.id, self._entity.id )
		self._entity.destroy()
		# New entity should have the biggest database id
		self.lookUpFunc( self.entityType, self.invalidID(), self.step3 )

	@fail_on_exception
	def step3( self, result ):
		# Does not exist in the database
		self.assertEqual( result, False )

		# Delay a little bit to avoid race condition
		BigWorld.addTimer( self.delayedStep4, 0.2 )

	@fail_on_exception
	def delayedStep4( self, *args ):
		self.lookUpFunc( self.entityType, self.id(), self.step4 )

	@fail_on_exception
	def step4( self, result ):
		# Exists in the database but offline
		# Note: There's a bit of a race condition between this and the call to
		# destroy the entity.
		self.assertEqual( result, True )
		self.createFunc( self.entityType, self.id(), self.step5 )

	@fail_on_exception
	def step5( self, baseRef, databaseID, wasActive ):
		self.assertNotEqual( baseRef, None )
		self.assertEqual( databaseID, self._databaseID )
		self.assertEqual( wasActive, False )

		# Try again but this time it's active
		self.createFunc( self.entityType, self.id(), self.step6 )

	@fail_on_exception
	def step6( self, baseRef, databaseID, wasActive ):
		self.assertNotEqual( baseRef, None )
		self.assertEqual( databaseID, self._databaseID )
		self.assertEqual( wasActive, True )

		# Try again but this time with an invalid database id
		self.createFunc( self.entityType, self.invalidID(), self.step7 )

	@fail_on_exception
	def step7( self, baseRef, databaseID, wasActive ):
		self.assertEqual( baseRef, None )
		self.assertEqual( databaseID, 0 )
		self.assertEqual( wasActive, False )

		self.finishTest()


class LookUpByDBID( LookUpEntity ):
	lookUpFunc = BigWorld.lookUpBaseByDBID
	createFunc = BigWorld.createBaseLocallyFromDBID

	entityType = "Simple"

	def id( self ):
		return self._databaseID

	def invalidID( self ):
		return self._databaseID + 1

	def createEntity( self ):
		return BigWorld.createEntity( self.entityType )


class LookUpByName( LookUpEntity ):
	lookUpFunc = BigWorld.lookUpBaseByName
	createFunc = BigWorld.createBaseLocallyFromDB

	entityType = "WithIdentifier"

	def onWriteToDBSuccess( self ):
		exceptionCaught = False
		try:
			self._entity.myIdentifier = "SomethingElse"
		except ValueError:
			exceptionCaught = True

		self.assertEqual( self._entity.myIdentifier, self.id() )
		self.assertTrue( exceptionCaught )

	def id( self ):
		return "myID"

	def invalidID( self ):
		return "DoesNotExist"

	def createEntity( self ):
		return BigWorld.createEntity(
				self.entityType, myIdentifier = self.id() )

# write_to_db.py
