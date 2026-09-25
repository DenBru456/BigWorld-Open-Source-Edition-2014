import time
from bwtest import TestCase
from bwtest import config
from pycommon import command_util
from primitives import WebConsoleAPI
from helpers.cluster import ClusterController

class ShutDownApp( TestCase ):


	name = "ShutDownApp"
	description = "Tests the functionality of BigWorld.shutDownApp \
		method, to shutdown the App"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "baseApp/backupPeriod", "5" )

	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	def doTest( self, procName ):
		self.cc.startProc( procName, 2 )
		waitTime = self.cc.getConfig( "baseApp/backupPeriod" )
		time.sleep( float(waitTime) * 2)
		snippet = """
		def onTimer( *args ):
			BigWorld.shutDownApp()
		BigWorld.addTimer( onTimer, 1 )
		srvtest.finish()
		"""

		self.cc.sendAndCallOnApp( procName, 1, snippet )
		self.assertTrue( self.cc.waitForAppStop( procName, 1 ) ) 

	def runTest( self ):
		self.cc.start()
		self.doTest( "baseapp" )
		self.doTest( "cellapp" )
