import time
from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class RetireProcTest( TestCase ):
	
	name = "Control Cluster Retireproc"
	description = "Tests control_cluster.py retireproc command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "baseapp", 1 )
		time.sleep( 3 )
		ret, output = run_cc_command( "retireproc", ["baseapp02"] )
		self.assertTrue( noUnexpectedOutput( output ),
						"retireproc had unexpected output: %s" % output )
		self.assertTrue( checkForProc( self.cc, "baseapp", "02", 
									timeout = 10, exists = False),
					"BaseApp did not retire." )