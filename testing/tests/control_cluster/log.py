import socket, time
from bwtest import TestCase, config
from helpers.cluster import ClusterController
from primitives import locallog
from primitives import WebConsoleAPI#import this to read the config
from test_common import *


class LogTest( TestCase ):
	
	
	name = "Control Cluster Log"
	description = "Tests control_cluster.py log command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
		
	def tearDown( self ):
		self.cc.clean()


	def runTest( self ):
		host = socket.gethostname()
		count = 1
		if host == config.WCAPI_WCHOST:
			count = 2
		host2 = config.CLUSTER_MACHINES[1]
		ret, output = run_cc_command( "log", ["hellomessage"] )
		patterns = [("Sent(\s)*to(\s)*message_logger(\s)*on(\s)*%s" % host, count)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from log hellomessage: %s" \
						% output )
		output = locallog.grepLastServerLog( "hellomessage", 
											lastSeconds = 2 )
		patterns = [("INFO(\s)*hellomessage", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected amount of log messages received: %s" % \
						output )
		
		ret, output = run_cc_command( "log", ["hellomessage2", host2],
									ignoreErrors = True )
		patterns = [("WARNING:(\s)*No MessageLogger process appears to be running", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from log hellomessage2 %s: %s" \
						% (host2, output) )

		ret, output = run_cc_command( "log", ["hellomessage3", host2, host],
									ignoreErrors = True )
		patterns = [("WARNING:(\s)*No MessageLogger process appears to be running", 1),
					("Sent(\s)*to(\s)*message_logger(\s)*on(\s)*%s" % host, count)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from log hellomessage3 %s %s: %s" \
						% (host2, host, output) )
		
		output = locallog.grepLastServerLog( "hellomessage3", 
											lastSeconds = 2 )
		patterns = [("INFO(\s)*hellomessage3", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected amount of log messages received: %s" % \
						output )
		
		ret, output = run_cc_command( "log", 
								["-s", "CRITICAL", "hellomessage4", host] )
		patterns = [("Sent(\s)*to(\s)*message_logger(\s)*on(\s)*%s" % host, count)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from log -s CRITITCAL hellomessage4 %s: %s" \
						% (host, output) )
		output = locallog.grepLastServerLog( "hellomessage4", 
											lastSeconds = 2 )
		patterns = [("CRITICAL(\s)*hellomessage4", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected amount of log messages received: %s" % \
						output )
		
		ret, output = run_cc_command( "log", 
								["-s", "CRITICAT", "hellomessage5", host],
								ignoreErrors = True )
		patterns = [("KeyError: 'CRITICAT'", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from log hellomessage5: %s" \
						% output )
		
		
		