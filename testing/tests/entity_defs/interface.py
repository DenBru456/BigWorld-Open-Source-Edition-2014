from bwtest import TestCase
from helpers.cluster import ClusterController


class InterfacesTest( TestCase ):
	
	
	name = "Interfaces"
	description = "Tests using interfaces in entity_defs"
	tags = []
	
	
	def setUp( self ):
		self.cc = ClusterController( ["entity_def/res", "simple_space/res"] )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		self.cc.bots.add( 1 )
		
		snippet = """
		avatars = [e for e in BigWorld.entities.values() if e.__class__.__name__ == 'Avatar']
		import TestEntity
		ret = TestEntity.create_entity( avatars[0].id )
		srvtest.finish( ret )
		"""
		testEntityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
		snippet = """
		bot = BigWorld.bots.values()[0]
		e = bot.entities[ %s ]
		srvtest.finish( e.interfaceProp )
		""" % testEntityID
		
		interfaceProp = self.cc.sendAndCallOnApp( "bots", None, snippet )
		self.assertTrue( interfaceProp == 10,
						"Property inherited from interface was not found" )
		
		
		
		
		