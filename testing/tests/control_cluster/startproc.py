import time

from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class StartProcTest( TestCase ):
	
	name = "Control Cluster Startproc"
	description = "Tests control_cluster.py startproc command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def runTest( self ):
		self.cc.start()
		self.cc.waitForServerSettle()
		ret, out = run_cc_command( "startproc", 
								["cellapp", config.CLUSTER_MACHINES[0]] )
		patterns = [("cellapp02(\s)+on %s" % config.CLUSTER_MACHINES[0], 1)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Cellapp02 process was not created.")
		
		ret, out = run_cc_command( "startproc", 
								["cellapp", config.CLUSTER_MACHINES[1]] )
		patterns = [("cellapp03(\s)+on %s" % config.CLUSTER_MACHINES[1], 1)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Cellapp03 process was not created.")
		
		ret, out = run_cc_command( "startproc", 
								["baseapp", config.CLUSTER_MACHINES[0], "-n", "2"] )
		patterns = [("baseapp02(\s)+on %s" % config.CLUSTER_MACHINES[0], 1)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Baseapp02 process was not created.")
		patterns = [("baseapp03(\s)+on %s" % config.CLUSTER_MACHINES[0], 1)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Baseapp03 process was not created.")
		
		ret, out = run_cc_command( "startproc", 
								["cellapp", config.CLUSTER_MACHINES[0], 
								config.CLUSTER_MACHINES[1]] )
		patterns = [("cellapp0[4-5](\s)+on %s" % config.CLUSTER_MACHINES[0], 1)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Cellapp process on %s was not created." % config.CLUSTER_MACHINES[0])
		patterns = [("cellapp0[4-5](\s)+on %s" % config.CLUSTER_MACHINES[1], 1)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Cellapp0 process on %s was not created." % config.CLUSTER_MACHINES[1])
		
		ret, out = run_cc_command( "startproc", 
								["baseapp", "-n", "2", 
								config.CLUSTER_MACHINES[0], 
								config.CLUSTER_MACHINES[1]] )
		patterns = [("baseapp0[4-7](\s)+on %s" % config.CLUSTER_MACHINES[0], 2)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Baseapp processes on %s was not created." % config.CLUSTER_MACHINES[0])
		patterns = [("baseapp0[4-7](\s)+on %s" % config.CLUSTER_MACHINES[1], 2)]
		self.assertTrue(  checkForPatterns( patterns, out),
						"Baseapp processes on %s was not created." % config.CLUSTER_MACHINES[1])
		
		