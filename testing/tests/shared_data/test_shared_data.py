import bwtest
from helpers.cluster import ClusterController
import time
from bwtest import log


class SharedBaseAppDataTest( bwtest.TestCase ):
	name = "BaseApp Shared Data" 
	description = "Test shared data between BaseApps"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "baseapp", 5 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		self.cc.waitForApp( "baseapp", 1 )
		self.cc.waitForApp( "baseapp", 2 )
		self.cc.waitForApp( "baseapp", 3 )
		self.cc.waitForApp( "baseapp", 4 )
		self.cc.waitForApp( "baseapp", 5 )
		self.cc.waitForApp( "baseapp", 6 )
		self.cc.waitForApp( "serviceapp", 1 )

		# Set value
		snippet1 = """
		BigWorld.baseAppData['base_test'] = 'IAmBaseAppData'
		srvtest.finish()
		"""

		self.cc.sendAndCallOnApp( "baseapp", 1, snippet1 )

		time.sleep( 3 )

		# Check values
		snippet2 = """
		import BWPersonality
		srvtest.finish( (BWPersonality.wasOnBaseAppDataCalled,
				BigWorld.baseAppData['base_test']) )
		"""

		for i in range( 2, 7 ):
			wasCalled, v = self.cc.sendAndCallOnApp( "baseapp", i, snippet2 )
			self.assertTrue( wasCalled )
			self.assertEqual( 'IAmBaseAppData', v )

		wasCalled, v = self.cc.sendAndCallOnApp( "serviceapp", 1, snippet2 )
		self.assertTrue( wasCalled )
		self.assertEqual( 'IAmBaseAppData', v )


class SharedCellAppDataTest( bwtest.TestCase ):
	name = "CellApp Shared Data" 
	description = "Test shared data between CellApps"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )	
		self.cc.start()
		self.cc.startProc( "cellapp", 5 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		self.cc.waitForApp( "cellapp", 1 )
		self.cc.waitForApp( "cellapp", 2 )
		self.cc.waitForApp( "cellapp", 3 )
		self.cc.waitForApp( "cellapp", 4 )
		self.cc.waitForApp( "cellapp", 5 )
		self.cc.waitForApp( "cellapp", 6 )

		snippet1 = """
		BigWorld.cellAppData['cell_test'] = 'IAmACellApp'
		srvtest.finish()
		"""

		self.cc.sendAndCallOnApp( "cellapp", 1, snippet1 )

		time.sleep( 1 )

		snippet2 = """
		srvtest.finish( BigWorld.cellAppData['cell_test'] )
		"""

		for i in range( 2, 7 ):
			v = self.cc.sendAndCallOnApp( "cellapp", i, snippet2 )
			self.assertEqual( 'IAmACellApp', v )


class SharedGlobalDataTest( bwtest.TestCase ):
	name = "Global Shared Data" 
	description = "Test shared data between all apps"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "baseapp", 2 )
		self.cc.startProc( "cellapp", 2 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def runTest( self ):
		for i in range( 1, 4 ):
			for app in ['cellapp', 'baseapp']:
				self.cc.waitForApp( app, i )

		snippet1 = """
		BigWorld.globalData['global_test_1'] = 'IAmGlobal1'
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet1 )
		time.sleep( 1 ) # TODO: Listen on BWPersonality.onGlobalData instead

		snippet2 = """
		BigWorld.globalData['global_test_2'] = 'IAmGlobal2'
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet2 )
		time.sleep( 1 ) # TODO: Listen on BWPersonality.onGlobalData instead

		snippet3 = """
		v1 = BigWorld.globalData['global_test_1']
		v2 = BigWorld.globalData['global_test_2']
		srvtest.finish( (v1, v2) )
		"""

		for i in range( 1, 4 ):
			for app in ['cellapp', 'baseapp']:
				(v1, v2) = self.cc.sendAndCallOnApp( app, i, snippet3 )
				self.assertEqual( 'IAmGlobal1', v1 )
				self.assertEqual( 'IAmGlobal2', v2 )
