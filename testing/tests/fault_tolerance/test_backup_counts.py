import bwtest
from helpers.cluster import ClusterController
import time


BACKUP_PERIOD = 1
NUM_BASES = 50
NUM_BASEAPPS = 7
NUM_SERVICEAPPS = 5
BACKUP_WATCHER = "backedUpBaseApps/numEntitiesBackedUp"

class BackUpCountTest( bwtest.TestCase ):
	name = "Back up count test" 
	description = "Test bases have backups and backup are on BaseApps only" 
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "baseApp/backupPeriod", str( BACKUP_PERIOD ) )

		self.cc.start()
		self.cc.startProc( "baseapp", NUM_BASEAPPS - 1 )
		self.cc.startProc( "serviceapp", NUM_SERVICEAPPS - 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		# Starting number of bases
		numBaseAppBasesStart = 0
		numServiceAppBasesStart = 0
		for i in range( 1, NUM_BASEAPPS + 1 ):
			v = self.cc.getWatcherValue( "numBases", "baseapp", i )
			numBaseAppBasesStart += int( v )
		for i in range( 1, NUM_SERVICEAPPS + 1 ):
			v = self.cc.getWatcherValue( "numBases", "serviceapp", i )
			numServiceAppBasesStart += int( v )

		# Create bases
		snippet = """
		for i in range( {numBases} ):
			BigWorld.createEntity( "Simple", name = "Simple%s" % i )
		srvtest.finish()
		"""

		for i in range( 1, NUM_BASEAPPS + 1 ):
			self.cc.sendAndCallOnApp(
					"baseapp", i, snippet, numBases = NUM_BASES )
		for i in range( 1, NUM_SERVICEAPPS + 1 ):
			self.cc.sendAndCallOnApp(
					"serviceapp", i, snippet, numBases = NUM_BASES )

		# Ensure backup period has elapsed
		time.sleep( BACKUP_PERIOD * 2 )

		# Backups for entities created on BaseApp should be on other BaseApps
		numBackups = 0
		for i in range( 1, NUM_BASEAPPS + 1 ):
			v = self.cc.getWatcherValue( BACKUP_WATCHER, "baseapp", i )
			numBackups += int( v )
		self.assertEqual( numBackups,
				numBaseAppBasesStart + NUM_BASEAPPS * NUM_BASES )

		# Backups for entities created on ServiceApp should be on other ServiceApps
		numBackups = 0
		for i in range( 1, NUM_SERVICEAPPS + 1 ):
			v = self.cc.getWatcherValue( BACKUP_WATCHER, "serviceapp", i )
			numBackups += int( v )
		self.assertEqual( numBackups,
				numServiceAppBasesStart + NUM_SERVICEAPPS * NUM_BASES )
