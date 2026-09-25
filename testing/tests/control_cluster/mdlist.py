import socket
from bwtest import TestCase, config
from test_common import *


class MdListTest( TestCase ):
	
	
	name = "Control Cluster Mdlist"
	description = "Tests control_cluster.py mdlist command"
	tags = []
	
	
	def runTest( self ):
		m1 = config.CLUSTER_MACHINES[0]
		m2 = config.CLUSTER_MACHINES[1]
		m1IP = socket.gethostbyname( m1 )
		m2IP = socket.gethostbyname( m2 )
		
		ret, output = run_cc_command( "mdlist", [] )
		patterns = [("%s" % m1, 1), ("%s" % m2, 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mdlist: %s" \
						% output )
		
		ret, output = run_cc_command( "mdlist", ["-i"] )
		patterns = [("%s(?![0-9])" % m1IP, 1), ("%s(?![0-9])" % m2IP, 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mdlist -i: %s" \
						% output )
		ret, output = run_cc_command( "mdlist", ["-i", m1, m2] )
		patterns = [("%s,%s" % tuple( sorted((m1IP, m2IP)) ), 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mdlist -i %s %s: %s" \
						% ( m1, m2, output ) )
		
		ret, output = run_cc_command( "mdlist", ["-d", "---"] )
		patterns = [("(%s---)|(---%s)" % (m1, m1), 1), ("(%s---)|(---%s)" % (m2, m2), 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mdlist -d ---: %s" \
						% output )
		