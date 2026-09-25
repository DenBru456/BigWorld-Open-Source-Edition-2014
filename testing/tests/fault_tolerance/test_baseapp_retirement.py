import bwtest
from helpers.cluster import ClusterController
import time
from bwtest import log


BACKUP_PERIOD = 5

# This class tests a very specific condition BWT-22002 
# where after a baseapp retirement, an onBaseOffloaded message is received 
# on a cellapp after the target entity has just been destroyed. 
# This resulted in a condemned channel hanging indefinitely 
# and resending messages to the retired baseapp.
class BaseAppRetirementTest( bwtest.TestCase ):
	name = "BaseApp retirement" 
	description = "Test baseapp retirement doesn't cause issues in cell entities"
	tags = [ "MANUAL" ]


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "baseApp/backupPeriod", str( BACKUP_PERIOD ) )


		self.cc.start()
		self.cc.startProc( "baseapp", 2 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		self.cc.waitForApp( "baseapp", 1 )
		self.cc.waitForApp( "baseapp", 2 )
		self.cc.waitForApp( "cellapp", 1 )

		snippet1 = """
		import BWPersonality
		spaceID = BWPersonality.getSpaceID()
		if spaceID > 0:	
			srvtest.finish( spaceID )

		def callback( spaceID ):
			srvtest.finish( spaceID )

		BWPersonality.hookOnSpaceID( callback )
		"""

		spaceID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet1 )

		time.sleep( 1 )

		snippet2 = """
		from random import random
		def createEntity():
			entityName = "test%f" % (random())
			e = BigWorld.createEntity( "TestEntity", name = entityName )
			e.cellData[ 'spaceID' ] = {spaceID}
			e.createCellEntity()
			e.writeToDB()
			return e.id

		entities = []
		for i in xrange( 20 ):
			entities.append( createEntity() )

		srvtest.finish( entities )
		"""

		entities = self.cc.sendAndCallOnApp( "baseapp", 1, snippet2,
						  spaceID = spaceID )

		time.sleep( BACKUP_PERIOD + 1 )

		snippet3 = """
		def timerCallback( id, arg ):
			print "Destroying test entities..."
			for id in {entities}:
				e = BigWorld.entities[id]
				e.destroy()
				print "destroyed entity", e.id

		BigWorld.addTimer( timerCallback, 0.4 )

		srvtest.finish()
		"""

		self.cc.sendAndCallOnApp( "cellapp", 1, snippet3, entities = entities )
		self.cc.retireProc( "baseapp", 1 )

		time.sleep(30)

