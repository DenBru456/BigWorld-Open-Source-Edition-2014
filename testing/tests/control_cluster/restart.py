import time

from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class RestartTest( TestCase ):
	
	name = "Control Cluster Restart"
	description = "Tests control_cluster.py restart command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		self.cc.waitForServerSettle()
		ret, output = run_cc_command( "restart", [] )
		for pattern in ['baseapp01', 'cellapp01', 'serviceapp01', 
						'dbapp', 'cellappmgr', 'baseappmgr', 
						config.CLUSTER_MACHINES[0]]:
			self.assertTrue( pattern in output, "Missing output in start: %s"
							 % pattern )
		self.cc.waitForServerSettle()
		
		self.cc.startProc( "baseapp" )
		ret, output = run_cc_command( "restart", [] )
		for pattern in ['baseapp01', 'baseapp02', 'cellapp01', 'serviceapp01', 
						'dbapp', 'cellappmgr', 'baseappmgr', 
						config.CLUSTER_MACHINES[0]]:
			self.assertTrue( pattern in output, "Missing output in start: %s"
							 % pattern )
		self.cc.waitForServerSettle()

		ret, output = run_cc_command( "restart", ["test"] )
		for pattern in ['baseapp01', 'baseapp02', 'cellapp01', 'serviceapp01', 
						'dbapp', 'cellappmgr', 'baseappmgr', "WARNING:  Extra arguments given", 
						config.CLUSTER_MACHINES[0]]:
			self.assertTrue( pattern in output, "Missing output in start: %s"
							 % pattern )
		self.cc.waitForServerSettle()
		
		self.cc.stop()
		self.cc.waitForServerShutdown()
		hasFailed = False
		try:
			ret, output = run_cc_command( "restart", [] )
		except:
			hasFailed = True
		self.assertTrue( hasFailed,
						"Restarting a non-running server should have failed" )