from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class StopTest( TestCase ):
		
	name = "Control Cluster Stop"
	description = "Tests control_cluster.py stop command"
	tags = []
	

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		self.cc.start()
		ret, output = run_cc_command( "stop", [] )
		self.assertTrue( noUnexpectedOutput( output ),
						"Unexpected output from stop: %s" % output)
		ret = self.cc.waitForServerShutdown( timeout = 5 )
		self.assertTrue( ret, "Server did not shut down cleanly" )
		ret, output = run_cc_command( "stop", [] )
		self.assertTrue( "No server process is running" in output,
						"Unexpected output when trying to stop with no server" )