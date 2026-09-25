from bwtest import TestCase, config
from test_common import *


class QueryTagsTest( TestCase ):
	
	
	name = "Control Cluster Querytags"
	description = "Tests control_cluster.py querytags command"
	tags = []
		
	
	def runTest( self ):
		m1 = config.CLUSTER_MACHINES[0]
		m2 = config.CLUSTER_MACHINES[1]
		ret, output = run_cc_command( "querytags", [] )
		patterns = [("%s/TimingMethod:(\s)*gettime" % m1, 1),
					("%s/Components:(\s)*cellApp baseApp serviceApp"% m1, 1),
					("%s/TimingMethod:(\s)*gettime" % m2, 1),
					("%s/Components:(\s)*cellApp baseApp serviceApp"% m2, 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from pyconsole querytags: %s" \
						% output )
		
		ret, output = run_cc_command( "querytags", ["-l", m1] )
		patterns2 = [("%s:(\s)*TimingMethod(\s)*(Groups)*(\s)*Components" % m1, 1)]
		self.assertTrue( checkForPatterns(patterns2, output),
						"Unexpected output from pyconsole querytags -l %s: %s" \
						% (m1, output) )
		
		ret, output = run_cc_command( "querytags", ["-a", m1] )
		patterns3 = [("%s/TimingMethod:(\s)*gettime" % m1, 1),
					("%s/Components:(\s)*cellApp baseApp serviceApp"% m1, 1)]
		self.assertTrue( checkForPatterns(patterns3, output),
						"Unexpected output from pyconsole querytags -a %s: %s" \
						% (m1, output) )
		
		ret, output = run_cc_command( "querytags", ["-a", m1, m2] )
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from pyconsole querytags -a %s %s: %s" \
						% (m1, m2, output) )
		