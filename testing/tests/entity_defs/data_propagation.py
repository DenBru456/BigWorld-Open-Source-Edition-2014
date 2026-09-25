from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer
import time


class DataPropagationTest( TestCase ):
	
	
	name = "DataPropagation"
	tags = []
	description = "Tests propagation of different data types"
	
	
	def setUp( self ):
		self.cc = ClusterController( ["entity_def/res", "simple_space/res"] )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		self.cc.waitForServerSettle()
		snippet = """
		import TestEntity
		ret = TestEntity.test_entity_defs()
		srvtest.finish( ret )
		"""
		
		ret = self.cc.sendAndCallOnApp( "cellapp", 1 , snippet )
		self.assertTrue( ret == 0,
						"Basic test_entity_defs test failed" )
		
		self.cc.stop()
		
		self.cc.start()
		self.cc.setWatcher( "debugging/shouldLoadBalance", False, 
							"cellappmgr", None )
		self.cc.setWatcher( "debugging/shouldMetaLoadBalance", False, 
							"cellappmgr", None )
		self.cc.startProc( "cellapp", 1 )
		self.cc.startProc( "bots", 1 )
		self.cc.bots.add( 10 )
		
		snippet = """
		import Math
		for i, bot in enumerate( BigWorld.bots.values() ):
			bot.stop()
			bot.snapTo( Math.Vector3( 20, 0, 20 - (i%2)*40 ) )
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, snippet)
		
		snippet = """
		avatars = [e for e in BigWorld.entities.values() if e.__class__.__name__ == 'Avatar']
		import TestEntity
		ret = TestEntity.create_entity( avatars[0].id )
		srvtest.finish( ret )
		"""
		testEntityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
		spaces = self.cc.getWatcherData( "spaces", "cellappmgr", None )
		bsp = spaces.getChildren()[0].getChild( "bsp" )
		bsp.getChild( "isLeaf" ).set( "False" )
		bsp.getChild( "position" ).set( "0.0" )
		
		snippet = """
		for e in BigWorld.entities.values():
			if not e.isReal():
				srvtest.finish( True )
		srvtest.finish( False )
		"""
		runTimer( lambda: 
							self.cc.sendAndCallOnApp( "cellapp", 2, snippet ),
						timeout = 120, period = 10 )
		snippet = """
		import TestEntity
		srvtest.finish( TestEntity.find_ghost_entity() )
		"""
		cellAppId = None
		ghostEntity = None
		for i in range( 1, 3 ):
			ret = self.cc.sendAndCallOnApp( "cellapp", i, snippet)
			if ret != 0:
				cellAppId = i
				ghostEntity = ret
				break
		self.assertTrue( cellAppId != None, "Unable to find ghost entity" )
		
		secondCellAppId = 1 + cellAppId % 2
		print "Testing test_propagation_real_1"
		snippet = """
		import TestEntity
		ret = TestEntity.test_propagation_real_1( %s )
		srvtest.finish( ret )
		""" % ghostEntity
		newID, passed = self.cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
		self.assertTrue( passed, "Failed test_propagation_real_1" )
		
		print "Testing test_propagation_ghost_1"
		snippet = """
		import TestEntity
		ret = TestEntity.test_propagation_ghost_1( %s )
		srvtest.finish( ret )
		""" % newID
		newID, passed = self.cc.sendAndCallOnApp( "cellapp", secondCellAppId, snippet )
		self.assertTrue( passed, "Failed test_propagation_ghost_1" )
		
		print "Testing test_propagation_real_2"
		snippet = """
		import TestEntity
		ret = TestEntity.test_propagation_real_2( %s )
		srvtest.finish( ret )
		""" % newID
		newID, passed = self.cc.sendAndCallOnApp( "cellapp", secondCellAppId, snippet )
		self.assertTrue( passed, "Failed test_propagation_real_2" )
		
		print "Testing test_propagation_ghost_2"
		snippet = """
		import TestEntity
		ret = TestEntity.test_propagation_ghost_2( %s )
		srvtest.finish( ret )
		""" % newID
		newID, passed = self.cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
		self.assertTrue( passed, "Failed test_propagation_ghost_2" )
		
		
		
		
		
		