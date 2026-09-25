from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class NagiosTest( TestCase ):
	
	name = "Control Cluster nagios"
	description = "Tests control_cluster.py nagios command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
		
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

		
	def runTest( self ):
		self.cc.start()
		ret, output = run_cc_command( "nagios", [] )
		patterns = [("BIGWORLD OK:", 1),
					("num_processes=8", 2),
					("baseapps=1", 4),
					("cellapps=1", 4),
					("dbapps=1", 4),
					("num_proxies=0", 2),
					("cellapp_load_avg=", 2),
					("baseapp_load_avg=", 2),
					("num_cell_entities=", 2)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios: %s" \
						% output )
		
		snippet = """
		for i in range(2000):
			BigWorld.createEntity( "TestEntity" )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		ret, output = run_cc_command( "nagios", ["-w", "0.0001"],
									ignoreErrors = True )
		patterns = [("BIGWORLD WARNING:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios -w 0.0001: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["-w", "0.5"] )
		patterns = [("BIGWORLD OK:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios -w 0.5: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["-c", "0.0001"],
									ignoreErrors = True )
		patterns = [("BIGWORLD CRITICAL:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios -c 0.0001: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["-c", "0.5"] )
		patterns = [("BIGWORLD OK:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios -c 0.5: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["--num-baseapps-warning", "2"],
									ignoreErrors = True )
		patterns = [("BIGWORLD WARNING:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios --num-baseapps-warning 2: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["--num-baseapps-critical", "2"],
									ignoreErrors = True )
		patterns = [("BIGWORLD CRITICAL:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios --num-baseapps-critical 2: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["--num-cellapps-warning", "2", 
								"--num-baseapps-critical", "2"],
									ignoreErrors = True )
		patterns = [("BIGWORLD CRITICAL:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios --num-cellapps-warning 2"\
						" --num-baseapps-critical 2: %s" \
						% output )
		
		ret, output = run_cc_command( "nagios", ["--num-baseapps-warning", "2", 
								"--num-baseapps-critical", "1"],
									ignoreErrors = True )
		patterns = [("BIGWORLD WARNING:", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios --num-baseapps-warning 2"\
						" --num-baseapps-critical 2: %s" \
						% output )
		
		self.cc.stop()
		ret, output = run_cc_command( "nagios", [], ignoreErrors = True )
		patterns = [("BIGWORLD CRITICAL: No server running", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from nagios: %s" \
						% output )