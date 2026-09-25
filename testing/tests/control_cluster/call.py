import time, pickle
from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class CallTest( TestCase ):
	
	
	name = "Control Cluster call"
	description = "Tests control_cluster.py call command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
		
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

		
	def runTest( self ):
		self.cc.start()
		ret, output = run_cc_command( "call", 
						["callTestSnippet", 
						"selfTestSnippetNoArg", 
						"'%s'" % pickle.dumps({})])
		patterns = [("\[Return Value\]", 1),
					("ServiceApp 1: ok:N\.", 1),
					("BaseApp 1: ok:N.", 1),
					("\[Console Output\]", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from call callTestSnippet: %s" \
						% output )

		ret, output = run_cc_command( "call", ["statusCheck"] )
		patterns = [("\[Return Value\]", 1),
					("True", 1),
					("\[Console Output\]", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from call statusCheck: %s" \
						% output )