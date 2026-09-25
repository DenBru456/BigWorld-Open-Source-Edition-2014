from bwtest import TestCase
from helpers.cluster import ClusterController


class EntityMethodsLod( TestCase ):
	
	
	name = "EntityMethodsLod"
	description = "Tests the behavior of level of detail settings with entity methods"
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
		bot = BigWorld.bots.values()[0]
		bot.stop()
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, snippet)
		
		snippet = """
		avatars = [e for e in BigWorld.entities.values() \
					if e.__class__.__name__ == 'Avatar']
		import TestEntity
		ret = TestEntity.create_entity( avatars[0].id )
		srvtest.finish( ret )
		"""
		testEntityID = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )

		chatMsgToSend = 'non-LOD hello1'
		chatLODMsgToSend = 'within-LOD hello1'
		snippet = """
		s = BigWorld.entities[%s]
		s.allClients.chat( '%s' )
		s.allClients.chatLOD( '%s' )
		srvtest.finish()
		""" % ( testEntityID, chatMsgToSend, chatLODMsgToSend )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet)
		
		snippet = """
		bot = BigWorld.bots.values()[0]
		s = bot.entities[%s]
		srvtest.finish( ( s.chatMsg, s.chatLODMsg ) )
		""" % testEntityID
		chatMsgReceived, chatLODMsgReceived = self.cc.sendAndCallOnApp( 
													"bots", None, snippet )
		self.assertTrue( chatMsgToSend == chatMsgReceived,
						"non-LOD method wasn't called when within LOD" )
		self.assertTrue( chatLODMsgToSend == chatLODMsgReceived,
						"LOD method wasn't called when within LOD" )
		
		snippet = """
		import Math
		bot = BigWorld.bots.values()[0]
		bot.snapTo( bot.position+Math.Vector3(101,0,0))
		srvtest.finish()
		"""
		self.cc.sendAndCallOnApp( "bots", None, snippet )
		
		chatMsgToSend = 'non-LOD hello2'
		chatLODMsgToSend = 'within-LOD hello2'
		snippet = """
		s = BigWorld.entities[%s]
		s.allClients.chat( '%s' )
		s.allClients.chatLOD( '%s' )
		srvtest.finish()
		""" % ( testEntityID, chatMsgToSend, chatLODMsgToSend )
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet)
		
		snippet = """
		bot = BigWorld.bots.values()[0]
		s = bot.entities[%s]
		srvtest.finish( (s.chatMsg, s.chatLODMsg) )
		""" % testEntityID
		chatMsgReceived, chatLODMsgReceived = self.cc.sendAndCallOnApp( 
													"bots", None, snippet )
		self.assertTrue( chatMsgToSend == chatMsgReceived,
						"non-LOD method wasn't called when out of LOD range" )
		self.assertTrue( chatLODMsgToSend != chatLODMsgReceived,
						"LOD method was called when out of LOD range" )

class PropertyLod( TestCase ):
	
	
	name = "PropertyLod"
	description = "Tests the behavior of level of detail settings with properties"
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
		bot = BigWorld.bots.values()[0]
		bot.stop()
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
		
		snippet = """
		bot = BigWorld.bots.values()[0]
		s = bot.entities[%s]
		srvtest.finish( s.lodTestProp )
		""" % testEntityID
		lodTestProp = self.cc.sendAndCallOnApp( "bots", None, snippet )
		self.assertTrue( lodTestProp == 50, "LOD Test property was not readable on bots" )
		
		snippet2 = """
		s = BigWorld.entities[%s]
		s.lodTestProp = 60
		srvtest.finish()
		""" % testEntityID
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet2 )
		
		lodTestProp = self.cc.sendAndCallOnApp( "bots", None, snippet )
		self.assertTrue( lodTestProp == 60, "LOD Test property was not updated while within LOD range" )
		
		
		snippet3 = """
		import Math
		bot = BigWorld.bots.values()[0]
		s = bot.entities[%s]
		bot.snapTo( s.position+Math.Vector3(120,0,0))
		srvtest.finish()
		""" % testEntityID
		self.cc.sendAndCallOnApp( "bots", None, snippet3 )
		
		snippet4 = """
		s = BigWorld.entities[%s]
		s.lodTestProp = 70
		srvtest.finish()
		""" % testEntityID
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet4 )
		
		lodTestProp = self.cc.sendAndCallOnApp( "bots", None, snippet )
		self.assertTrue( lodTestProp == 60, "LOD Test property was updated while out of LOD range" )
		
		snippet5 = """
		import Math
		bot = BigWorld.bots.values()[0]
		s = bot.entities[%s]
		bot.snapTo( s.position+Math.Vector3(85,0,0))
		srvtest.finish()
		""" % testEntityID
		self.cc.sendAndCallOnApp( "bots", None, snippet5 )
		
		lodTestProp = self.cc.sendAndCallOnApp( "bots", None, snippet )
		self.assertTrue( lodTestProp == 70, "LOD Test property was not updated when moving back to LOD range" )
		
		
		
		
