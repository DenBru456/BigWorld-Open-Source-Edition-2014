from bwtest import TestCase, config
from test_common import *


class NetInfoTest( TestCase ):
	
	
	name = "Control Cluster NetInfo"
	description = "Tests control_cluster.py netinfo command"
	tags = []
	
	
	def runTest( self ):
		ret, output = run_cc_command( "netinfo", [config.CLUSTER_MACHINES[0]] )
		patterns = [("%s( )*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}( )*\d+ process" % config.CLUSTER_MACHINES[0], 1),
				("eth0:", 1), ("sit0:", 1), ("loss", 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected output from netinfo <machine>: %s" % output )
		ret, output = run_cc_command( "netinfo", [] )
		patterns = [("%s( )*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}( )*\d+ process" % config.CLUSTER_MACHINES[0], 1),
				("%s( )*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}( )*\d+ process" % config.CLUSTER_MACHINES[1], 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected output from netinfo: %s" % output )