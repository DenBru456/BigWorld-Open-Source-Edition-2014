import socket
from bwtest import TestCase, config
from test_common import *


class PingRingTest( TestCase ):
	
	
	name = "Control Cluster pingring"
	description = "Tests control_cluster.py pingring command"
	tags = []
	
	
	def runTest( self ):
		m1 = config.CLUSTER_MACHINES[0]
		m2 = config.CLUSTER_MACHINES[1]
		m1IP = socket.gethostbyname( m1 )
		m2IP = socket.gethostbyname( m2 )
		
		ret, output = run_cc_command( "pingring", [] )
		patterns = [("%s\s+%s\s+Broadcast:\s+\d\.\d+ms,\s+Direct:\s+\d\.\d+ms" \
					% (m1IP, m1), 1),
					("%s\s+%s\s+Broadcast:\s+\d\.\d+ms,\s+Direct:\s+\d\.\d+ms" \
					% (m2IP, m2), 1)]
		
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from pingring: %s" \
						% output )