import bwunittest
import os
import time

ARCHIVE_PERIOD = 100
SEC_DB_DIR = "/tmp/"
SQL_COUNT = "SELECT sm_count FROM tbl_SimpleTestEntity"

# --------------------------------------------------------------------------
# Section: Functions run server side
# --------------------------------------------------------------------------

def createEntity():
	global e
	e = BigWorld.createEntity( "SimpleTestEntity" )
	e.writeToDB( createCB )


def writeEntity():
	global e
	e.count = 10
	e.writeToDB( writeCB )


def destroyEntity():
	global e
	e.destroy()
	returnToPyUnit( None )


def createCB( *args ):
	returnToPyUnit( None )


def writeCB( *args ):
	returnToPyUnit( args[1].count )


def returnHasStarted():
	returnToPyUnit( BigWorld.hasStarted() )

# --------------------------------------------------------------------------
# Section: Test cases run bwunittest side
# --------------------------------------------------------------------------

class SecondaryDBMiscTestSuite( bwunittest.TestCase ):

	def testXMLAndSecondaryEnabled( self ):
		startNumFiles = len( os.listdir( SEC_DB_DIR ) )

		configs = { "dbApp/type":"xml",
					"baseApp/secondaryDB/enable":"true",
					"baseApp/secondaryDB/directory":SEC_DB_DIR }
		bwunittest.startServer( None, configs, None, "layout.xml" )

		while not self.hasStarted( [ "baseapp01" ] ):
			time.sleep( 1 )

		endNumFiles = len( os.listdir( SEC_DB_DIR ) )
		self.assert_( startNumFiles == endNumFiles )


	def testWriteToDBOnDestroy( self ):
		configs = { "dbApp/type":"mysql",
					"baseApp/secondaryDB/enable":"true",
					"baseApp/archivePeriod": str( ARCHIVE_PERIOD ) }
		entities = ["SimpleTestEntity"]
		bwunittest.startServer( None, configs, entities, "layout.xml" )

		bwunittest.runOnServer( [createEntity, createCB], "baseapp01" )
		count = bwunittest.runOnServer( [writeEntity, writeCB], "baseapp01" )
		bwunittest.runOnServer( [destroyEntity], "baseapp01" )

		bwunittest.stopServer( False )

		dbCount = bwunittest.executeRawDatabaseCommand( SQL_COUNT )[0][0]
		self.assert_( dbCount == count )


	def hasStarted( self, procs ):
		for proc in procs:
			if not bwunittest.runOnServer( [returnHasStarted], proc ):
				return False
		return True
