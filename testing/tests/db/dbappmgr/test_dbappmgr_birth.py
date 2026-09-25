import bwtest
from helpers.cluster import ClusterController

class DBAppMgrBirthTest( bwtest.TestCase ):

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):		
		"""
		Check DBAppMgr handles DBAppMgr birth, it should shut down itself
		"""
		
		# Check birth of a new dbappmgr
		pid1 = self.cc.getPids( 'dbappmgr' )[0]
		self.cc.startProc( "dbappmgr" )
		pid2 = self.cc.getPids( 'dbappmgr' )[0]
		self.assertNotEqual( pid1, pid2 )
