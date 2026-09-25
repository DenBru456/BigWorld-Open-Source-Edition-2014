import bwunittest
import time

BACKUP_PERIOD = 1

# --------------------------------------------------------------------------
# Section: Functions run server side
# --------------------------------------------------------------------------

def createEntities():
	import random
	for i in range( 0, 10 ):
		BigWorld.createEntity( "TestEntity", name = str( random.random() ) )
	returnToPyUnit( None )


def returnEntityCount():
	import util
	returnToPyUnit( len( util.entitiesOfType( "TestEntity" ) ) )


# --------------------------------------------------------------------------
# Section: Test cases run bwunittest side
# --------------------------------------------------------------------------

class RestoreEntityTestSuite( bwunittest.TestCase ):

	def setUp( self ):
		configs = { "baseApp/backupPeriod":str( BACKUP_PERIOD ) }
		bwunittest.startServer( None, configs, [ "TestEntity" ], "layout.xml" )


	def tearDown( self ):
		bwunittest.stopServer()


	def testRestore( self ):
		bwunittest.startProc( "baseapp" )
		bwunittest.startProc( "baseapp" )

		baseapps = [ "baseapp01", "baseapp02", "baseapp03" ]

		for baseapp in baseapps:
			bwunittest.runOnServer( [ createEntities ], baseapp )

		startCount = self.entityCount( baseapps )

		time.sleep( BACKUP_PERIOD )

		bwunittest.stopProc( "baseapp01" )
		baseapps.remove( "baseapp01" )
		count = self.entityCount( baseapps )
		self.assert_( count == startCount )

		time.sleep( BACKUP_PERIOD )

		bwunittest.stopProc( "baseapp02", True )
		baseapps.remove( "baseapp02" )
		count = self.entityCount( baseapps )
		self.assert_( count == startCount )


	def entityCount( self, procs ):
		count = 0
		for proc in procs:
			count += bwunittest.runOnServer( [returnEntityCount], proc )
		return count
