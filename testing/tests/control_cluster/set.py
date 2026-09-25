from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class SetTest( TestCase ):
	
	
	name = "Control Cluster Set"
	description = "Tests control_cluster.py set command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		run_cc_command( "set", ["baseapp01", 
								"network/indexedSendWindowSizeThreshold", 
								"256"] )
		val = self.cc.getWatcherValue( "network/indexedSendWindowSizeThreshold",
								"baseapp", 1 )
		self.assertTrue( int(val) == 256,
						"Control_cluster set baseapp01 didn't work" )
		self.cc.setWatcher( "network/indexedSendWindowSizeThreshold", 128,
						"baseapp", 1 )
		
		self.cc.startProc( "baseapp", 2, machineIdx = 1 )
		run_cc_command( "set", ["baseapps", 
								"network/indexedSendWindowSizeThreshold", 
								"256"] )
		for i in range( 1, 4 ):
			val = self.cc.getWatcherValue( 
								"network/indexedSendWindowSizeThreshold",
								"baseapp", i )
			self.assertTrue( int(val) == 256,
						"Control_cluster set baseapps didn't work for baseapp0%s"\
						% i )
		