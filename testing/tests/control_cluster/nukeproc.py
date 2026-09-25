import time
from bwtest import TestCase
from helpers.cluster import ClusterController, CoreDumpError
from test_common import *


class NukeProcTest( TestCase ):
	
	name = "Control Cluster Nukeproc"
	description = "Tests control_cluster.py nukeproc command"
	tags = []
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
		
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "baseapp", 1 )
		self.cc.startProc( "cellapp", 1 )
		time.sleep( 3 )
		
		ret, output = run_cc_command( "nukeproc", ["baseapp02"] )
		self.assertTrue( "WARNING:  This command is deprecated" in output,
						"Deprecation warning did not appear" )
		self.assertTrue( checkForProc( self.cc, "baseapp", "02", 
									timeout = 10, exists = False),
						"BaseApp wasn't killed")
		
		ret, output = run_cc_command( "nukeproc", ["cellapp"] )
		self.assertTrue( "WARNING:  This command is deprecated" in output,
						"Deprecation warning did not appear" )
		self.assertTrue( checkForProc( self.cc, "cellapp", "01", 
									timeout = 5, exists = False) != \
						checkForProc( self.cc, "cellapp", "02", 
									timeout = 5, exists = False) , 
						"CellApp wasn't killed")
		
		didDumpCores = False
		try:
			self.cc.stop()
		except CoreDumpError, e:
			didDumpCores = True
			self.assertTrue( "baseapp" in e.failedAppList,
							"BaseApp did not dump core with -c")
			self.assertTrue( "cellapp" in e.failedAppList,
							"CellApp did not dump core with --core")
			self.assertEqual( len( e.failedAppList ), 2,
							"Other processes dumped cores: %s" % e.failedAppList)
		self.assertTrue( didDumpCores, "Neither baseapp or cellapp dumped core" )