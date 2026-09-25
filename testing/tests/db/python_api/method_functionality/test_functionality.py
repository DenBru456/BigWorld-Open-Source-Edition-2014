import bwtest
from helpers.cluster import ClusterController

import time
from pycommon import bwconfig

class TestFunctionality( bwtest.TestCase ):
	name = "Method functionality" 
	description = "DB method functionality on a BaseApp"
	tags = []


	def setUp( self ):
		self._cc = ClusterController( [ "simple_space/res" ] )
		self._cc.start()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()


	def runTest( self ):
		self._cc.loadSnippetModule( "baseapp", 1,
			"db/python_api/method_functionality/base/functionality" )

		backupPeriod = float( bwconfig.get( "baseApp/backupPeriod" ) )

		time.sleep( backupPeriod + 1 )

		self._cc.callOnApp( "baseapp", 1, "testWriteToDB" )

