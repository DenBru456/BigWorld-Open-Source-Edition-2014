from bwtest import TestCase, log
from helpers.cluster import ClusterController

# Conservative number entities and a generous deviation keeps
# the test simple. The hash quality already has unit tests.
NUM_ENTITIES = 2000
PERCENTAGE_DEVIATION_MAX = 20

NUM_DB_APPS = 8

WATCHER_PATH = "tasks/MySqlDatabase/background/PutEntityTask/numTasks"


class DBAppDistributedWritesTest( TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "db/secondaryDB/enable", "false" )
		self.cc.start()

		for i in range( 0, NUM_DB_APPS - 1 ):
			self.cc.startProc( "dbapp" )

		self.cc.waitForServerSettle()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def writeEntities( self ):
		snippet = """
		global numCallbacks
		numCallbacks = 0

		def onWriteToDB( *args ):
			global numCallbacks
			numCallbacks -= 1
			if numCallbacks == 0:
				srvtest.finish()

		for e in BigWorld.entities.values():
			if e.className == "TestEntity":
				numCallbacks += 1
				e.int8 += 1
				e.writeToDB( onWriteToDB )
		""" 

		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )


	def numWrites( self, appIDs ):
		counts = {}

		for appID in appIDs:
			value = self.cc.getWatcherValue( WATCHER_PATH, "dbapp", appID )
			if value == None:
				counts[appID] = 0
			else:
				counts[appID] = int( value )

		return counts


	def checkWriteDistribution( self, appIDs, currNumWrites ):
		newNumWrites = self.numWrites( appIDs )

		for appID in newNumWrites.keys():
			expected = NUM_ENTITIES / len( appIDs )
			value = newNumWrites[appID]

			# Calculate delta
			if currNumWrites.has_key( appID ):
				value -= currNumWrites[appID]

			value = float( value )
			percentageDeviation = abs( value - expected ) / expected * 100

			log.debug( "DBApp0%s: writes %s, percentage deviation %s" %
					(appID, value, percentageDeviation) )

			self.assertTrue( percentageDeviation < PERCENTAGE_DEVIATION_MAX )

		return newNumWrites


	def runTest( self ):		
		"""
		Check first entity writes are on alpha DBApp.
		Subsequent writes, even across DBApp deaths and births, are distributed
		among DBApps.
		"""

		appIDs = range( 1, NUM_DB_APPS+1 )

		# Create entities
		snippet = """
		for i in range( 0, %s ):
			BigWorld.createEntity( "TestEntity", name = str( i ) )
		srvtest.finish()
		""" % NUM_ENTITIES
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )

		# First writes are all by alpha
		self.writeEntities()
		value = self.cc.getWatcherValue( WATCHER_PATH, "dbapp", 1 )
		self.assertEqual( int( value ), NUM_ENTITIES )

		numWrites = { 1 : NUM_ENTITIES }

		# Subsequent writes are distributed
		self.writeEntities()
		numWrites = self.checkWriteDistribution( appIDs, numWrites )

		# Writes remain distributed after DBApp births
		self.cc.startProc( "dbapp" )
		appIDs.append( max( appIDs ) + 1 )
		self.cc.startProc( "dbapp" )
		appIDs.append( max( appIDs ) + 1 )

		self.writeEntities()
		numWrites = self.checkWriteDistribution( appIDs, numWrites )

		# Writes remain distributed after DBApp deaths
		self.cc.killProc( "dbapp", min( appIDs ) )
		appIDs.remove( min( appIDs ) )
		self.cc.killProc( "dbapp", min( appIDs ) )
		appIDs.remove( min( appIDs ) )

		self.writeEntities()
		numWrites = self.checkWriteDistribution( appIDs, numWrites )

		# Writes remain distributed after DBApp deaths (SIGKILL)
		self.cc.killProc( "dbapp", min( appIDs ), True )
		appIDs.remove( min( appIDs ) )
		self.cc.killProc( "dbapp", min( appIDs ), True )
		appIDs.remove( min( appIDs ) )

		self.writeEntities()
		numWrites = self.checkWriteDistribution( appIDs, numWrites )
