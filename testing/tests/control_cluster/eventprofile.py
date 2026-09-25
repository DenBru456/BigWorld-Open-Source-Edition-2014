import re, threading, time
from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class EventProfileTest( TestCase ):
	
	
	name = "Control Cluster eventprofile"
	description = "Tests control_cluster.py eventprofile command"
	tags = []
	
	columnOrder = ["count", "totalsize", "avgsize", "bandwidth" ]

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		
		
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

		
	def runTest( self ):
		self.cc.start()
		self.cc.waitForServerSettle()
		snippet = """
e = BigWorld.createEntity( "TestEntity", 2, (0, 0, 0), (0, 0, 0) )
e2 = BigWorld.createEntity( "PersistentEntity", 2, (0, 0, 0), (0, 0, 0) )

def onTimer( controllerID, userArg ):
	import random
	e = BigWorld.entities[userArg]
	e.cellArray = [ int( random.random()*100 ) ]

def onTimer2( controllerID, userArg ):
	import random
	e = BigWorld.entities[userArg]
	e.persistentProp = int( random.random()*100 )

BigWorld.addTimer( onTimer, 1, 1, e.id )
BigWorld.addTimer( onTimer2, 0.5, 0.5, e2.id )
srvtest.finish()	
"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		ret, output = run_cc_command( "eventprofile", [] )
		patterns = [("Waiting 10.0 secs for sample data ...", 1),
					("\*\*\*\* cellapp01 \*\*\*\*", 1),
					("Event Type: privateClientEvents", 1),
					("Event Type: publicClientEvents", 1),
					("Name(\s)*#(\s)*Size(\s)*AvgSize(\s)*Bandwidth", 1),
					("Event Type: totalPublicClientEvents", 1),]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from eventprofile: %s" \
						% output )
		
		pattern = "\s+\d+\s+\d+\s+\d+\.\d+\s+\d+\.\d+"
		for column in self.columnOrder:
			ret, output = run_cc_command( "eventprofile", ["-s", column] )
			self.assertTrue( checkIfSorted( output, column, 
											self.columnOrder, pattern ),
							"eventprofile -s %s was not sorted correctly" % column )
		
		ret, output = run_cc_command( "eventprofile", ["-t", "27"] )
		patterns2 = [("Waiting 27.0 secs for sample data ...", 1)]
		self.assertTrue( checkForPatterns(patterns2, output),
						"Unexpected output from eventprofile -t 27: %s" \
						% output )
		
		class EventProfileThreaded( threading.Thread ):	
			def run( self ):
				run_cc_command( "eventprofile", [] )
		
		t = EventProfileThreaded()
		t.start()
		time.sleep( 1 )
		ret, output = run_cc_command( "eventprofile", [], ignoreErrors = True )
		patterns3 = [("ERROR:\s+Event profiles are already running", 1)]
		self.assertTrue( checkForPatterns(patterns3, output),
						"Unexpected output from eventprofile: %s" \
						% output )
		t.join()
		
		t = EventProfileThreaded()
		t.start()
		time.sleep( 1 )
		ret, output = run_cc_command( "eventprofile", ["-f"] )
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from eventprofile -f: %s" \
						% output )
		t.join()
		
