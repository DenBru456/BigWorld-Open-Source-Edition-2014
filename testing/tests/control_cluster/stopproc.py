from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class StopProcTest( TestCase ):
	
	name = "Control Cluster Stopproc"
	description = "Tests control_cluster.py stopproc command"
	tags = []
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "baseapp", 1 )
		ret, out = run_cc_command( "stopproc", ["cellapp02"] )
		self.assertTrue( "WARNING:  This command is deprecated" in out,
						"Deprecation warning did not appear: %s" % out )
		ret, out = run_cc_command( "stopproc", ["baseapp02"] )
		self.assertTrue( "WARNING:  This command is deprecated" in out,
						"Deprecation warning did not appear: %s" % out )