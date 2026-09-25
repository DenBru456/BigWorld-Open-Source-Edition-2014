import socket
from bwtest import TestCase, config
from test_common import *


class CheckRingTest( TestCase ):
	
	
	name = "Control Cluster CheckRing"
	description = "Tests control_cluster.py checkring command"
	tags = []
	
	
	def runTest( self ):
		m1 = config.CLUSTER_MACHINES[0]
		m2 = config.CLUSTER_MACHINES[1]
		m1IP = socket.gethostbyname( m1 )
		m2IP = socket.gethostbyname( m2 )
		
		ret, output = run_cc_command( "checkring", [] )
		patterns = [ ("%s(\s)*%s(\s)*->" % (m1IP, m1), 1),
					("%s(\s)*%s(\s)*->" % (m2IP, m2), 1),
					("->(\s)*%s(\s)*%s" % (m1IP, m1), 1),
					("->(\s)*%s(\s)*%s" % (m2IP, m2), 1),
					("Ring is complete", 1) ]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from checkring: %s" \
						% output )