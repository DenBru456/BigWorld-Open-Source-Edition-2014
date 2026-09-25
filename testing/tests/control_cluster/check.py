from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class CheckTest( TestCase ):
	
	name = "Control Cluster Check"
	description = "Tests control_cluster.py check command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		user = config.CLUSTER_USERNAME
		uid = config.CLUSTER_UID
		ret, out = run_cc_command( "check", [] )
		self.assertTrue( "Server running for %s (%s)" % ( user, uid ) in out,
					"Unexpected output from check when running: %s" % out )
		self.cc.stop()
		ret, out = run_cc_command( "check", [], ignoreErrors = True )
		self.assertTrue( "Server not running for %s (%s)" % ( user, uid ) in out,
					"Unexpected output from check when stopped: %s" % out )