from bwtest import TestCase
from test_common import *


class CInfoTest( TestCase):
	
	name = "Control Cluster CInfo"
	description = "Tests control_cluster.py cinfo command"
	tags = []
	
	
	def runTest( self ):
		ret, output = run_cc_command( "cinfo", [] )
		patterns = [("%s( )*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}( )*\d+ process" % config.CLUSTER_MACHINES[0], 1),
				("%s( )*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}( )*\d+ process" % config.CLUSTER_MACHINES[1], 1)]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected output from cinfo: %s" % output )
		ret, output = run_cc_command( "cinfo", 
					[config.CLUSTER_MACHINES[0], config.CLUSTER_MACHINES[1]] )
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected output from cinfo <machine>: %s" % output )