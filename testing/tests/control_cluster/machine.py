import socket, os
from bwtest import TestCase, config
from helpers.cluster import ClusterController
from helpers.command import remove
from test_common import *


class MachineTest( TestCase ):
	
	
	name = "Control Cluster --machine"
	description = "Tests control_cluster.py --machine option"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		remove( os.path.join( config.CLUSTER_BW_ROOT, config.BIGWORLD_FOLDER,
									"bin/server/*/server", "core.*" ) )
		remove( os.path.join( config.CLUSTER_BW_ROOT, config.BIGWORLD_FOLDER,
									"bin/server/*/server", "assert.*" ) )
		
		
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		user = config.CLUSTER_USERNAME
		uid = config.CLUSTER_UID
		machine = config.CLUSTER_MACHINES[0]
		machineIP = socket.gethostbyname( machine )
		ret, output = run_cc_command( "checkcores", [], 
									ccParams = ["-m", machine],
									ignoreErrors = True )
		patterns = [("0 core files for %s \(%s\) on" % (user, uid), 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkcores with no cores: %s" \
						% output )
		
		ret, output = run_cc_command( "checkcores", [], 
									ccParams = ["--machine", machine],
									ignoreErrors = True )
		patterns = [("0 core files for %s \(%s\) on" % (user, uid), 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkcores with no cores: %s" \
						% output )
		ret, output = run_cc_command( "checkcores", [], 
									ccParams = ["-m", machineIP],
									ignoreErrors = True )
		patterns = [("0 core files for %s \(%s\) on" % (user, uid), 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkcores with no cores: %s" \
						% output )