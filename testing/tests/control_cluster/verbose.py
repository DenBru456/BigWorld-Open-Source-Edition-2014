import socket
from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class VerboseTest( TestCase ):
	
	
	name = "Control Cluster -v"
	description = "Tests control_cluster.py -v option"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		machine = config.CLUSTER_MACHINES[0]
		machineIP = socket.gethostbyname( machine )
		ret, output = run_cc_command( "start", [machine], ccParams = ["-v"])
		patterns = [("Candidate machines:", 1),
					("%s\s+\(%s\)" % (machine, machineIP), 2)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from verbose start: %s" \
						% output )