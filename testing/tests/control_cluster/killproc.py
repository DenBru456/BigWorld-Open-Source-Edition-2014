import time
from bwtest import TestCase
from helpers.cluster import ClusterController, CoreDumpError
from test_common import *


class KillProcTest( TestCase ):
	
	name = "Control Cluster Killproc"
	description = "Tests control_cluster.py killproc command"
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
		ret, out = run_cc_command( "killproc", ["baseapp02"] )
		self.assertTrue( noUnexpectedOutput( out ), 
						"Unexpected output from killproc: %s" % out )
		proc = self.cc.findProc( "baseapp", "02" )
		self.assertTrue( proc == None, "BaseApp wasn't killed")
		
		ret, out = run_cc_command( "killproc", ["cellapp"] )
		self.assertTrue( noUnexpectedOutput( out ), 
						"Unexpected output from killproc: %s" % out )
		self.assertTrue( checkForProc( self.cc, "cellapp", "01", 
									timeout = 5, exists = False) != \
						checkForProc( self.cc, "cellapp", "02", 
									timeout = 5, exists = False), 
					"CellApp wasn't killed")
		
		self.cc.stop()
		self.cc.start()
		self.cc.startProc( "baseapp", 1 )
		self.cc.startProc( "cellapp", 1 )
		time.sleep( 3 )
		ret, out = run_cc_command( "killproc", ["baseapp02", "-c"] )
		self.assertTrue( noUnexpectedOutput( out ), 
						"Unexpected output from killproc -c: %s" % out )
		proc = self.cc.findProc( "baseapp", "02" )
		self.assertTrue( proc == None, "BaseApp wasn't killed")
		
		ret, out = run_cc_command( "killproc", ["cellapp", "--core"] )
		self.assertTrue( noUnexpectedOutput( out ), 
						"Unexpected output from killproc --core: %s" % out )
		proc = self.cc.findProc( "cellapp", "02" )
		self.assertTrue( checkForProc( self.cc, "cellapp", "01", 
									timeout = 5, exists = False) != \
						checkForProc( self.cc, "cellapp", "02", 
									timeout = 5, exists = False), 
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
		
		
		