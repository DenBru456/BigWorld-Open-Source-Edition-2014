from bwtest import TestCase
from helpers.cluster import ClusterController
from helpers.timer import runTimer

class TestDemoLoadBalance( TestCase ):
	
	name = "Demo load balance feature test"
	description = "Tests the ability to enable demo load balance which "\
			"switches load balancing to work by number of total entities"\
			" instead of actual load"
	tags = []
	
	NUM_ENTITIES = 99
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.setConfig( "balance/demo/enable", "true" )
		self.cc.setConfig( "balance/demo/numEntitiesPerCell", 
							str( self.NUM_ENTITIES ) )
	
	
	def tearDown( self ):
		if hasattr(self, "cc"):
			self.cc.stop()
			self.cc.clean()
	
	def countRealEntities( self, appId ):
		snippet = """
		entities = [e for e in BigWorld.entities.values() if \
					( e.className =="TestEntity" and e.isReal() )]
		srvtest.finish( len(entities) )
		"""
		return self.cc.sendAndCallOnApp( "cellapp", appId, snippet )


	def runTest( self ):
		self.cc.start()
		self.cc.waitForServerSettle()
		#First create some entities
		snippet = """
		for i in range( %s ):
			pos = (190 - 180*(i%%3), 0, 190 - 180*(i%%3))
			dir = (0,0,0)
			BigWorld.createEntity( "TestEntity", 2, pos, dir)
		srvtest.finish()
		""" % self.NUM_ENTITIES
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet)
		
		#Then check real entities as 
		runTimer( lambda: self.countRealEntities( 1 ), 
				checker = lambda res: res == self.NUM_ENTITIES, timeout = 10 )
		
		self.cc.startProc( "cellapp", 1 )
		for i in range( 1, 3 ):
			runTimer( lambda: self.countRealEntities( i ), 
				checker = lambda res: 
							res in (self.NUM_ENTITIES/3, self.NUM_ENTITIES*2/3), 
				timeout = 10 )
		self.cc.startProc( "cellapp", 1 )
		for i in range( 1, 4 ):
			runTimer( lambda: self.countRealEntities( i ), 
				checker = lambda res: res == self.NUM_ENTITIES/3, 
				timeout = 10 )
