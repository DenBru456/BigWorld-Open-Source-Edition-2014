from bwtest import TestCase
from helpers.cluster import ClusterController


class AddWatcherTest( TestCase ):
	
	
	name = "AddWatcher"
	description = "Tests the functionality of addWatcher method"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		snippet = """
		global maxBandwidth
		maxBandwidth = 20000
		def getMaxBps( ):
			return str(maxBandwidth)

		def setMaxBps( bps ):
			global maxBandwidth
			maxBandwidth = int(bps)

		BigWorld.addWatcher( "Comms/Maxbandwidth", getMaxBps, setMaxBps )
		srvtest.finish()
		"""
		
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		maxband = self.cc.getWatcherData( "Comms/Maxbandwidth", "baseapp", 1 )
		self.assertTrue( int( maxband.value ) == 20000,
						"Watcher wasn't created with addWatcher" )
		maxband.set( "30000" )		
		maxband = self.cc.getWatcherData( "Comms/Maxbandwidth", "baseapp", 1 )

		self.assertTrue( int( maxband.value ) == 30000,
						"Watcher wasn't set correctly" )