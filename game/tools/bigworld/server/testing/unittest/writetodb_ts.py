import bwunittest


# --------------------------------------------------------------------------
# Section: Functions run server side
# --------------------------------------------------------------------------

def createSuccessFlag():
	global e
	e = BigWorld.createEntity( "TestEntity", name = "billy" )
	e.writeToDB( returnSuccessFlag )


def returnSuccessFlag( *args ):
	returnToPyUnit( args[0] )


def createEntity():
	global e
	e = BigWorld.createEntity( "TestEntity", name = "billy" )
	returnToPyUnit( e.databaseID )


def writeEntity():
	global e
	e.writeToDB( returnDBID )


def createAndWriteEntity():
	global e
	e = BigWorld.createEntity( "TestEntity", name = "billy" )
	e.writeToDB( returnDBID )


def returnDBID( *args ):
	returnToPyUnit( args[1].databaseID )


def destroy():
	global e
	e.destroy()
	returnToPyUnit( None )


# --------------------------------------------------------------------------
# Section: Test cases run bwunittest side
# --------------------------------------------------------------------------

class WriteToDBTestSuite( bwunittest.TestCase ):

	def setUp( self ):
		configs = { "dbApp/type":"mysql" }
		entities = ["TestEntity"]
		bwunittest.startServer( None, configs, entities, "layout.xml" )


	def tearDown( self ):
		bwunittest.stopServer()


	def testWriteToDBSuccessFlag( self ):
		funcs = [createSuccessFlag, returnSuccessFlag]
		success = bwunittest.runOnServer( funcs, "baseapp01" )
		self.assert_( success )

		# writeToDB() fails as name property is an identifier
		success = bwunittest.runOnServer( funcs, "baseapp01" )
		self.assert_( not success )


	def testWriteToDBDatabaseID( self ):
		dbID = bwunittest.runOnServer( [createEntity], "baseapp01" )
		self.assert_( dbID == 0 )
		funcs = [writeEntity, returnDBID]
		dbID = bwunittest.runOnServer( funcs, "baseapp01" )
		self.assert_( dbID != 0 )

		# writeToDB() fails as name property is an identifier
		funcs = [createAndWriteEntity, returnDBID]
		dbID = bwunittest.runOnServer( funcs, "baseapp01" )
		self.assert_( dbID == 0 )


	def testWriteToDBOnDestroy( self ):
		funcs = [createAndWriteEntity, returnDBID]
		dbID = bwunittest.runOnServer( funcs, "baseapp01" )

		sql = "SELECT gameTime FROM tbl_TestEntity WHERE id = %s" % dbID
		createTime = bwunittest.executeRawDatabaseCommand( sql )[0][0]

		funcs = [destroy]
		dbID = bwunittest.runOnServer( funcs, "baseapp01" )

		destroyTime = bwunittest.executeRawDatabaseCommand( sql )[0][0]
		self.assert_( createTime != destroyTime )
