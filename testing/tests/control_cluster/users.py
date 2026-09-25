from bwtest import TestCase, config
from test_common import *
from helpers.cluster import ClusterController


class UsersTest( TestCase ):
	
	
	name = "Control Cluster Users"
	description = "Tests control_cluster.py users command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		ret, output = run_cc_command( "users", [] )
		patterns = [("%s \(%s\) running \d processes" % (config.CLUSTER_USERNAME, config.CLUSTER_UID), 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected output from users: %s" % output )
	
	