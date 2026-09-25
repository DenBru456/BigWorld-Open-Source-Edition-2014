from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class SummaryTest( TestCase ):
	
	name = "Control Cluster Summary"
	description = "Tests control_cluster.py summary command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		machine = config.CLUSTER_MACHINES[0]
		ret, output = run_cc_command( "summary", [] )
		patterns = [("misc( )*processes:", 1),
					("baseappmgr( )*on( )*%s" % machine, 1),
					("cellappmgr( )*on( )*%s" % machine, 1),
					("dbappmgr( )*on( )*%s" % machine, 1),
					("1 dbapp at \(.*\)", 1),
					("1 baseapp at \(.*\)", 1),
					("1 serviceapp at \(.*\)", 1),
					("1 cellapp at \(.*\)", 1),]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected output from summary: %s" % output)