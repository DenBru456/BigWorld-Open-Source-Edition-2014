import bwtest
from helpers.cluster import ClusterController
import time

class TestClientViaBaseEvent( bwtest.TestCase ):
	name = "Client via base event Test"
	description = "Test bots can receive remote chat messages from baseapp"


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.addCleanup( self.cc.clean )
		self.cc.start()
		self.addCleanup( self.cc.stop )
		self.cc.startProc( "bots", 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def getPlayerID( self ):
		snippet = """
		clientApp = BigWorld.bots.values()[0]
		entity = clientApp.entities[clientApp.id]
		srvtest.finish( (entity.__class__.__name__, clientApp.id, entity.id) )
		"""
		className, clientAppID, entityID = self.cc.sendAndCallOnApp(
			"bots", snippet = snippet )
		
		self.assertEqual( className, "PlayerAvatar" )
		self.assertEqual( clientAppID, entityID )
		return entityID

	def getChatMsg( self ):
		snippet = """
		clientApp = BigWorld.bots.values()[0]
		entity = clientApp.entities[clientApp.id]
		chatMsg = entity.chatMsg
		entity.chatMsg = ""
		srvtest.finish( chatMsg )
		"""
		return self.cc.sendAndCallOnApp( "bots", snippet = snippet )

	def sendClientChatMsg( self, playerID, shouldExposeForReplay,
			shouldRecordOnly, shouldUseMailbox, chatMsg ):
		snippet = """
		def convertToMailbox( entity ):
			BigWorld.globalData['mailbox'] = entity
			return BigWorld.globalData['mailbox']

		playerID = %s
		shouldUseMailbox = %s

		if shouldUseMailbox:
			p = convertToMailbox( BigWorld.entities[ playerID ] )
		else:
			p = BigWorld.entities[ playerID ]

		p.client( shouldExposeForReplay=%s,
			shouldRecordOnly=%s ).chat( u'%s' )
		srvtest.finish()
		""" % ( playerID, shouldUseMailbox, shouldExposeForReplay,
			shouldRecordOnly, chatMsg )

		self.cc.sendAndCallOnApp( "baseapp", snippet = snippet )

	def checkChatMsg( self, playerID, shouldExposeForReplay,
			shouldRecordOnly, shouldUseMailbox, chatMsg, shouldReceived ):

		self.sendClientChatMsg( playerID, shouldExposeForReplay,
			shouldRecordOnly, shouldUseMailbox, chatMsg )

		# Wait a second to make sure message was received
		time.sleep( 1 )

		if shouldReceived:
			self.assertEqual( self.getChatMsg(), chatMsg )
		else:
			self.assertEqual( self.getChatMsg(), "" )

	def runTest( self ):
		self.cc.bots.add( 1 )

		playerID = self.getPlayerID()

		self.checkChatMsg( playerID, shouldExposeForReplay = False,
			shouldRecordOnly = False, shouldUseMailbox = False,
			chatMsg = "baseapp: client-via-base", shouldReceived = True )

		self.checkChatMsg( playerID, shouldExposeForReplay = False,
			shouldRecordOnly = False, shouldUseMailbox = True,
			chatMsg = "baseapp: client-via-base-mailbox", shouldReceived = True )

		self.checkChatMsg( playerID, shouldExposeForReplay = True,
			shouldRecordOnly = False, shouldUseMailbox = False,
			chatMsg = "baseapp: client-via-base expose-for-replay",
			shouldReceived = True )

		self.checkChatMsg( playerID, shouldExposeForReplay = True,
			shouldRecordOnly = False, shouldUseMailbox = True,
			chatMsg = "baseapp: client-via-base-mailbox expose-for-replay",
			shouldReceived = True )

		self.checkChatMsg( playerID, shouldExposeForReplay = True,
			shouldRecordOnly = True, shouldUseMailbox = False,
			chatMsg = "baseapp: client-via-base expose-for-replay-only",
			shouldReceived = False )

		self.checkChatMsg( playerID, shouldExposeForReplay = True,
			shouldRecordOnly = True, shouldUseMailbox = True,
			chatMsg = "baseapp: client-via-base-mailbox expose-for-replay-only",
			shouldReceived = False )

