import os
from bwtest import TestCase, config
from helpers.cluster import ClusterController, CoreDumpError
from helpers.command import remove 
from test_common import *


class CheckCoresTest( TestCase ):
	
	
	name = "Control Cluster checkcores"
	description = "Tests control_cluster.py checkcores command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		remove( os.path.join( config.CLUSTER_BW_ROOT, 
									config.BIGWORLD_FOLDER,
									"bin/server/*/server", "core.*" ) )
		remove( os.path.join( config.CLUSTER_BW_ROOT, 
									config.BIGWORLD_FOLDER,
									"bin/server/*/server", "assert.*" ) )
		
		
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		user = config.CLUSTER_USERNAME
		uid = config.CLUSTER_UID
		machine = config.CLUSTER_MACHINES[0]
		ret, output = run_cc_command( "checkcores", [], 
									ccParams = ["-m", machine],
									ignoreErrors = True )
		patterns = [("0 core files for %s \(%s\) on" % (user, uid), 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkcores with no cores: %s" \
						% output )
		
		self.cc.start()
		run_cc_command( "nukeproc", ["baseapp01"] )
		try:
			self.cc.stop()
		except CoreDumpError:
			pass
		ret, output = run_cc_command( "checkcores", [], 
									ccParams = ["-m", machine], )
		patterns = [("1 core files for %s \(%s\) in" % (user, uid), 1),
					("/server/core.baseapp.%s" % machine, 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkcores with cores: %s" \
						% output )
		
		ret, output = run_cc_command( "checkcores", ["-a"], 
									ccParams = ["-m", machine], )
		patterns = [("1 core files for %s \(%s\) in" % (user, uid), 1),
					("/server/core.baseapp.%s" % machine, 1),
					("Received QUIT signal", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkcores with cores: %s" \
						% output )
		