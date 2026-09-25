import time

from bwtest import TestCase
from test_common import *
from helpers.cluster import ClusterController


class KillTest( TestCase ):
	
	name = "Control Cluster Kill"
	description = "Tests control_cluster.py kill command"
	tags = []
	
	def setUp( self ):
		pass


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
		
	
	def step1( self ):
		"""Kill during normal run"""
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		ret, output = run_cc_command( "kill", [] )
		self.assertTrue( noUnexpectedOutput( output ), 
						"Unexpected output from kill: %s" % output)
		ret = self.cc.waitForServerShutdown( timeout = 5 )
		self.assertTrue( ret, "Server did not shut down cleanly" )
		

	def step2( self ):
		"""Kill during shutdown"""
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		ret, output = run_cc_command( "stop", [], parallel = True )
		time.sleep( 3 )
		ret, output = run_cc_command( "kill", [] )
		self.assertTrue( noUnexpectedOutput( output ), 
						"Unexpected output from kill: %s" % output)
		ret = self.cc.waitForServerShutdown( timeout = 5 )
		self.assertTrue( ret, "Server did not shut down cleanly" )