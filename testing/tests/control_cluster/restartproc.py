import time
from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class RestartProcTest( TestCase ):
	
	name = "Control Cluster Restartproc"
	description = "Tests control_cluster.py restartproc command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "baseapp", 2 )
		
		time.sleep( 3 )
		ret, output = run_cc_command( "restartproc", ["baseapp03"] )
		self.assertTrue( noUnexpectedOutput( output ),
						"restartproc had unexpected output: %s" % output )
		self.assertTrue( checkForProc( self.cc, "baseapp", "03", 
									timeout = 10, exists = False),
						"Original baseapp wasn't stopped" )
		self.assertTrue( checkForProc( self.cc, "baseapp", "04", 
									timeout = 30, exists = True),
						"Baseapp wasn't retired." )
		