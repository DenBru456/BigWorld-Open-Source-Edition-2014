import bwtest
from helpers.cluster import ClusterController

class TestDatatypes( bwtest.TestCase ):
	name = "DB Datatypes" 
	description = "A sequence of datatypes tests run on the server" 
	tags = []


	def setUp( self ):
		cc = ClusterController( "simple_space/res" )
		self._cc = cc
		def cleanup1():
			self._cc.clean()
		self.addCleanup( cleanup1 )

		cc.start()

		def cleanup2():
			self._cc.stop()
		self.addCleanup( cleanup2 )

		self._cc.waitForApp( "baseapp", 1 )

		cc.loadSnippetModule(
					"baseapp", 1, "db/datatypes/test_datatypes" )


	def tearDown( self ):
		self.doCleanups()


	def step1( self ):
		"""Writing to DB"""
		
		self._cc.callOnApp( "baseapp", 1, "snippetWrite" )


	def step2( self ):
		"""Reading from DB"""
		
		self._cc.callOnApp( "baseapp", 1, "snippetRead" )


	def step3( self ):
		"""Checking values"""
		
		self._cc.callOnApp( "baseapp", 1, "snippetTest" )
