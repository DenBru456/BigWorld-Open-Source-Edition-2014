from bwtest import TestCase, config
from helpers.cluster import ClusterController
from test_common import *


class RunScriptTest( TestCase ):
	
	
	name = "Control Cluster RunScript"
	description = "Tests control_cluster.py runscript command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		
		path1 = self.cc._tempTree + "/test.py"
		file1 = open( path1, "w" )
		file1.write( "print 'RunScriptTest'" )
		file1.close()
		
		path2 = self.cc._tempTree + "/test.file"
		file2 = open( path2, "w" )
		file2.write( "print 'RunScriptTest'" )
		file2.close()
		
		ret, output = run_cc_command( "runscript", ["baseapp01", path1] )
		patterns = [("RunScriptTest", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from runscript baseapp01 %s: %s" \
						% (path1, output))
		
		ret, output = run_cc_command( "runscript", ["cellapp01"], 
									input = "", ignoreErrors = True )
		patterns = [("Connected to %s.bigworldtech.com" % config.CLUSTER_MACHINES[0], 1),
				("Connection closed by foreign host", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from runscript cellapp01: %s" \
						% output )
		
		ret, output = run_cc_command( "runscript", ["baseapp01", "cellapp01", path1])
		patterns = [("cellapp01:(\s)*RunScriptTest", 1),
				("baseapp01:(\s)*RunScriptTest", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
			"Unexpected output from runscript baseapp01 cellapp01 %s: %s" \
						% ( path1, output ) )
		
		ret, output = run_cc_command( "runscript", ["baseapp01", "cellapp01", path1, "-P"])
		patterns = [("RunScriptTest", 2)]
		self.assertTrue( checkForPatterns(patterns, output),
			"Unexpected output from runscript baseapp01 cellapp01 %s -P: %s" \
						% ( path1, output ) )
		
		ret, output = run_cc_command( "runscript", ["baseapp01", path2] )
		patterns = [("RunScriptTest", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from runscript baseapp01 %s: %s" \
						% (path2, output))
		
		ret, output = run_cc_command( "runscript", ["cellappmgr", path1],
									ignoreErrors = True )
		patterns = [("ERROR:(\s)*Seleted process 'cellappmgr' doesn't support Python Console", 1)]
		self.assertTrue( checkForPatterns(patterns, output),
						"Unexpected output from runscript cellappmgr %s: %s" \
						% (path1, output))
		
		