import time

from bwtest import TestCase
from helpers.cluster import ClusterController, CoreDumpError
from test_common import *


class NukeTest( TestCase ):
	
	
	name = "Control Cluster Nuke"
	description = "Tests control_cluster.py nuke command"
	tags = ["STAGED"]
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		try:
			self.cc.stop()
		except:
			pass
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		run_cc_command( "nuke", [] )
		self.cc.waitForServerShutdown( timeout = 5 )
		didDumpCores = False
		try:
			self.cc.stop()
		except CoreDumpError, e:
			if "baseapp" not in e.failedAppList:
				self.fail( "BaseApp did not dump core" )
			if "cellapp" not in e.failedAppList:
				self.fail( "CellApp did not dump core" )
			if "serviceapp" not in e.failedAppList:
				self.fail( "ServiceApp did not dump core" )
			if "baseappmgr" not in e.failedAppList:
				self.fail( "BaseAppMgr did not dump core" )
			if "cellappmgr" not in e.failedAppList:
				self.fail( "CellAppMgr did not dump core" )
			if "loginapp" not in e.failedAppList:
				self.fail( "ServiceAppMgr did not dump core" )
			if "dbapp" not in e.failedAppList:
				self.fail( "DBApp did not dump core" )
			didDumpCores = True
		self.assertTrue( didDumpCores, "No cores were dumped after nuke" )