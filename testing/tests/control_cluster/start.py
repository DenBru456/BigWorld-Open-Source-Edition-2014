from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *

class StartTest( TestCase ):
		
	name = "Control Cluster Start"
	description = "Tests control_cluster.py start command"
	tags = []
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		ret, output = run_cc_command( "start", [config.CLUSTER_MACHINES[0]] )
		for pattern in ['baseapp01', 'cellapp01', 'serviceapp01', 
						'dbapp', 'cellappmgr', 'baseappmgr', 
						config.CLUSTER_MACHINES[0]]:
			self.assertTrue( pattern in output, "Missing output in start: %s"
							 % pattern )
		ret = self.cc.waitForServerSettle( timeout = 5 )
		self.assertTrue( ret, "Server didn't start properly" )