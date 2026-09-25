from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class CheckLayoutTest( TestCase ):
	
	
	name = "Control Cluster CheckLayout"
	description = "Tests control_cluster.py checklayout command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "baseapp" )
		path = self.cc._tempTree + "/layout1"
		run_cc_command( "save", [path] )
		self.cc.stop()
		
		ret, output = run_cc_command( "checklayout", [path], ignoreErrors = True)
		self.assertTrue( 'Server not running according to layout' in output,
						"Unexpected output from checklayout: %s" % output)
		run_cc_command( "load", [path] )
		ret, output = run_cc_command( "checklayout", [path])
		self.assertTrue( 'Server running according to layout' in output,
						"Unexpected output from checklayout: %s" % output)
		self.cc.startProc( "cellapp" )
		ret, output = run_cc_command( "checklayout", [path], ignoreErrors = True)
		self.assertTrue( 'Server not running according to layout' in output,
						"Unexpected output from checklayout: %s" % output)