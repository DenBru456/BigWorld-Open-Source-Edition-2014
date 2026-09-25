from bwtest import TestCase
from helpers.cluster import ClusterController
from test_common import *


class GetManyTest( TestCase ):
	
	
	name = "Control Cluster GetMany"
	description = "Tests control_cluster.py getmany command"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "baseapp", 1 )
		ret, output = run_cc_command( "getmany", ["baseapp01",  'entityTypes/*/*'] )
		patterns = [('baseapp01', 1),
				 	('profile(\s)*typeID(\s)*methods(\s)*averageArchiveSize', 1),
				 	('totalArchiveSize(\s)*numberOfInstances', 1),
				 	('averageBackupSize(\s)*backupSize(\s)*isProxy', 1),
				 	('Space(\s)*<DIR>', 1),
				 	('Simple(\s)*<DIR>', 1),
				 	('WithIdentifier(\s)*<DIR>', 1),
				 	('TestEntity(\s)*<DIR>', 1),
				 	('Avatar(\s)*<DIR>', 1),]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from getmany baseapp01: %s" % output )
		
		ret, output = run_cc_command( "getmany", ["baseapps",  'entityTypes/*/*'] )
		patterns = [('baseapp\d{1,2}', 2),
				 	('profile(\s)*typeID(\s)*methods(\s)*averageArchiveSize', 2),
				 	('totalArchiveSize(\s)*numberOfInstances', 2),
				 	('averageBackupSize(\s)*backupSize(\s)*isProxy', 2),
				 	('Space(\s)*<DIR>', 2),
				 	('Simple(\s)*<DIR>', 2),
				 	('WithIdentifier(\s)*<DIR>', 2),
				 	('TestEntity(\s)*<DIR>', 2),
				 	('Avatar(\s)*<DIR>', 2),]
		self.assertTrue( checkForPatterns( patterns, output ),
						"Unexpected out from getmany baseapps: %s" % output )
		