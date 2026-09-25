from bwtest import TestCase
from helpers.cluster import ClusterController


class TestMaximumSpacesPerCellapp( TestCase ):
	
	tags = []
	description = "Test that the metaLoadBalncePriority/limitedSpaces setting"\
					" correctly limits the amount of spaces"
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "cellAppMgr/shouldMetaLoadBalance", "false" )
		self.cc.setConfig( 
					"cellAppMgr/metaLoadBalancePriority/limitedSpaces", "2" )
	
	
	def tearDown( self ):
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "cellapp", 1)
		
		numTotalSpaces = int( self.cc.getWatcherValue( 
										"numSpaces", "cellappmgr", None ) )
		self.assertTrue( numTotalSpaces == 1,
						"simple_space was not created with one space" )
		
		#Create spaces with limit not being reached
		snippet = """
		for i in range( 3 ):
			BigWorld.createEntity("TestEntity").createInNewSpace()
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		numTotalSpaces = int( self.cc.getWatcherValue( 
										"numSpaces", "cellappmgr", None ) )
		self.assertTrue( numTotalSpaces == 4,
						"New spaces were not created" )
		for i in range(1, 3):
			numCellAppSpaces = int( self.cc.getWatcherValue( 
												"numSpaces", "cellapp", i ) )
			self.assertTrue( numCellAppSpaces == 2,
							"New spaces were not created on correct cellapp."\
							" Found %s spaces" % numCellAppSpaces)
		
		#Try to create spaces above limited. SHould fail
		snippet = """
		for i in range( 3 ):
			BigWorld.createEntity("TestEntity").createInNewSpace()
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )
		
		numTotalSpaces = int( self.cc.getWatcherValue( 
										"numSpaces", "cellappmgr", None ) )
		self.assertTrue( numTotalSpaces == 4,
						"New spaces were created despite limt being reached" )


