import re
from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class MercuryProfileTest( TestCase ):
	
	name = "Control Cluster mercuryprofile"
	description = "Tests control_cluster.py mercuryprofile command"
	tags = []
	
	columnOrder = [ "id", "name", "bytesReceived", "messagesReceived",
					"maxBytesReceived", "avgMessageLength",
					"avgBytesPerSecond", "avgMessagesPerSecond" ]
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
		
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

		
	def runTest( self ):
		self.cc.start()
		pattern = "\d+\s+\w*\s+\d+\s+\d+\s+\d+\s+\d+\.\d\s+\d+\.\d\s+\d+\.\d\n"
		
		ret, output = run_cc_command( "mercuryprofile", ["cellapp01"] )
		patterns = [("cellapp01\s+-\s+Internal\s+Nub", 1),
					("id\s+name\s+br\s+mr\s+max\s+br\s+aml\s+abps\s+amps", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mercuryprofile cellapp01: %s" \
						% output )
		self.assertTrue( checkIfSorted( output, "id", 
									self.columnOrder, pattern, reverse = False ),
							"mercuryrofile cellapp01 was not sorted correctly" )
		
		ret, output = run_cc_command( "mercuryprofile", ["baseapp01", "-r"] )
		patterns = [("baseapp01\s+-\s+Internal\s+Nub", 1),
					("id\s+name\s+br\s+mr\s+max\s+br\s+aml\s+abps\s+amps", 2)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mercuryprofile baseapp01 -r: %s" \
						% output )
		self.assertTrue( checkIfSorted( output, "id", 
									self.columnOrder, pattern ),
							"mercuryrofile baseapp01 -r was not sorted correctly" )
		
		ret, output = run_cc_command( "mercuryprofile", ["cellapp01", 
														"--no-skip-unused"] )
		patterns = [(pattern, 256)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from mercuryprofile cellapp01 --no-skip-unused: %s" \
						% output )
		
		for column in self.columnOrder:
			ret, output = run_cc_command( "mercuryprofile", 
										["serviceapp", "-s", column] )
			self.assertTrue( checkIfSorted( output, column, 
									self.columnOrder, pattern, reverse = False ),
							"mercuryrofile baseapp01 -s %s was not sorted correctly" \
							% column )
			
			
		
	
	