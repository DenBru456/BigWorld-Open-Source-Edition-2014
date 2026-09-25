import bwunittest
import time

BACKUP_PERIOD = 5
ARCHIVE_PERIOD = 5
SQL_INT8 = "SELECT sm_int8 FROM tbl_TestEntity where sm_name = 'billy'"
SQL_SEC_DB_COUNT = "SELECT COUNT(*) FROM bigworldSecondaryDatabases"


# --------------------------------------------------------------------------
# Section: Functions run server side
# --------------------------------------------------------------------------

INT8_VALUE = 1

def createAndWriteEntity():
	global e
	e = BigWorld.createEntity( "TestEntity", name = "billy" )
	e.writeToDB( returnDBID )


def writeEntity():
	global e
	e.int8 = 1  #INT8_VALUE
	e.writeToDB( returnInt8 )


def returnInt8( *args ):
	returnToPyUnit( args[1].int8 )


def returnDBID( *args ):
	returnToPyUnit( args[1].databaseID )


def returnHasStarted():
	returnToPyUnit( BigWorld.hasStarted() )


# --------------------------------------------------------------------------
# Section: Test cases run bwunittest side
# --------------------------------------------------------------------------

class SecondaryDBTestSuite( bwunittest.TestCase ):


	def setUp( self ):
		configs = { "dbApp/type":"mysql",
					"baseApp/secondaryDB/enable":"true",
					"baseApp/archivePeriod": str( ARCHIVE_PERIOD ),
					"baseApp/backupPeriod": str( BACKUP_PERIOD ) }
		entities = ["TestEntity"]
		bwunittest.startServer( None, configs, entities, "layout.xml" )


	def tearDown( self ):
		bwunittest.stopServer()


	def testWriteToDB( self ):
		funcs = [createAndWriteEntity, returnDBID]
		bwunittest.runOnServer( funcs, "baseapp01" )
		dbInt8 = bwunittest.executeRawDatabaseCommand( SQL_INT8 )[0][0]
		self.assert_( dbInt8 == 0 )

		funcs = [writeEntity, returnInt8]
		bwunittest.runOnServer( [writeEntity, returnInt8], "baseapp01" )
		self.assert_( bwunittest.stopProc( "baseapp01", True ) )

		# Wait for new value to be consolidated into the primary.
		while bwunittest.executeRawDatabaseCommand( SQL_SEC_DB_COUNT )[0][0]:
			time.sleep( 1 )

		dbInt8 = bwunittest.executeRawDatabaseCommand( SQL_INT8 )[0][0]
		self.assert_( dbInt8 == INT8_VALUE )

		bwunittest.restoreServer()


	def testWriteToDBDatabaseID( self ):
		funcs = [createAndWriteEntity, returnDBID]
		dbID = bwunittest.runOnServer( funcs, "baseapp01" )
		self.assert_( dbID != 0 )


	def testRegistration( self ):
		# Single registration
		while not self.hasStarted( [ "baseapp01" ] ):
			time.sleep( 1 )

		count = bwunittest.executeRawDatabaseCommand( SQL_SEC_DB_COUNT )[0][0]
		self.assert_( count == 1 )

		# Simultaneous registration
		bwunittest.startProc( "baseapp" )
		bwunittest.startProc( "baseapp" )

		while not self.hasStarted( [ "baseapp02", "baseapp03" ] ):
			time.sleep( 1 )

		count = bwunittest.executeRawDatabaseCommand( SQL_SEC_DB_COUNT )[0][0]
		self.assert_( count == 3 )


	def testDeregistration( self ):
		bwunittest.startProc( "baseapp" )
		bwunittest.startProc( "baseapp" )

		while not self.hasStarted( [ "baseapp01", "baseapp02", "baseapp03" ] ):
			time.sleep( 1 )

		# Wait for first backup cycle to complete
		time.sleep( BACKUP_PERIOD )

		# Deregistration on BaseApp retire
		self.assert_( bwunittest.stopProc( "baseapp01" ) )
		time.sleep( ARCHIVE_PERIOD )
		count = bwunittest.executeRawDatabaseCommand( SQL_SEC_DB_COUNT )[0][0]
		self.assert_( count == 2 )

		# Deregistration on BaseApp kill
		self.assert_( bwunittest.stopProc( "baseapp02", True ) )
		time.sleep( ARCHIVE_PERIOD )
		count = bwunittest.executeRawDatabaseCommand( SQL_SEC_DB_COUNT )[0][0]
		self.assert_( count == 1 )


	def hasStarted( self, procs ):
		for proc in procs:
			if not bwunittest.runOnServer( [returnHasStarted], proc ):
				return False
		return True
