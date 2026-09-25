from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class DisplayTest( TestCase ):
	
	name = "Control Cluster Display"
	description = "Tests control_cluster.py display command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		machine = config.CLUSTER_MACHINES[0]
		ret, out = run_cc_command( "display", [] )
		patterns = [("misc( )*processes:", 1),
					("baseappmgr( )*on( )*%s" % machine, 1),
					("cellappmgr( )*on( )*%s" % machine, 1),
					("dbappmgr( )*on( )*%s" % machine, 1),
					("dbapps \(1\):", 1),
					("dbapp01( )*on( )*%s" % machine, 1),
					("baseapps \(1\):", 1),
					("baseapp01( )*on( )*%s" % machine, 1),
					("cellapps \(1\):", 1),
					("cellapp01( )*on( )*%s" % machine, 1),
					("serviceapps \(1\):", 1),
					("serviceapp01( )*on( )*%s" % machine, 1),
					("loginapps \(1\):", 1),
					("loginapp01( )*on( )*%s" % machine, 1),]
		
		self.assertTrue( checkForPatterns( patterns, out ),
						"Unexpected output from display: %s" % out)
		
		self.cc.startProc( "bots", 5 )
		ret, out = run_cc_command( "display", ["bots"] )
		patterns = [("bots:%s:\d+ on %s" % ( machine, machine ), 5)]
		self.assertTrue( checkForPatterns( patterns, out ),
						"Unexpected output from display bots: %s" % out)
		
		self.cc.startProc( "cellapp", 1)
		ret, out = run_cc_command( "display", ["cellapp01"] )
		patterns = [("cellapp01( )*on( )*%s" % machine, 1)]
		self.assertTrue( checkForPatterns( patterns, out ),
						"Unexpected output from display cellapp01: %s" % out)
		
		