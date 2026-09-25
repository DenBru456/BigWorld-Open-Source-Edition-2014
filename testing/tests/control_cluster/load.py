from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class LoadTest( TestCase ):
	
	
	name = "Control Cluster Load"
	description = "Tests control_cluster.py load command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		path = self.cc._tempTree + "/layout1"
		run_cc_command( "save", [path] )
		
		self.cc.startProc( "baseapp", 1 )
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "cellapp", 1, machineIdx=1 )
		self.cc.startProc( "bots", 2, machineIdx=1 )
		path2 = self.cc._tempTree + "/layout2"
		run_cc_command( "save", [path2] )
		
		self.cc.stop()
		
		run_cc_command( "load",  [path] )
		for process, ord in [("baseapp", "01"), ("cellapp", "01"), 
							("serviceapp", "01"), ("baseappmgr", None),
							("cellappmgr", None), ("dbapp", None),
							("loginapp", "01")]:
			self.assertTrue( checkForProc( self.cc, process, ord, 
									timeout = 10, exists = True),
						"%s didn't start correctly" % process)
		
		self.cc.stop()
		run_cc_command( "load",  [path2] )
		for process, ord in [("baseapp", "01"), ("baseapp", "02"),
							("cellapp", "01"), ("cellapp", "02"), ("cellapp", "03"), 
							("serviceapp", "01"), ("baseappmgr", None),
							("cellappmgr", None), ("dbapp", None),
							("loginapp", "01"), ("bots", None),  ]:
			self.assertTrue( checkForProc( self.cc, process, ord, 
									timeout = 10, exists = True),
						"%s didn't start correctly" % process)
		