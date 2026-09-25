from helpers.cluster import ClusterController
from bwtest import TestCase

# scenario 1: test calling client method via cellApp
class CallClientMethodViaCell( TestCase ):
	name = 'Test calling client method via cellApp'
	description = 'Will start normal server and add a bots process' \
				  'then connect to baseApp python console and issue ' \
				  'a call via cell component.'

	tags = []

	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )


	def tearDown( self ):
		if hasattr( self, "cc" ):
			self.cc.stop()
			self.cc.clean()


	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		self.cc.bots.add( 1 )
		
		statusToSend = ( 7, True )
		snippet = """
		a = BigWorld.entities["Avatar"]
		a.cell.ownClient.setFriendStatus( %s, %s )
		srvtest.finish()
		""" % statusToSend
		self.cc.sendAndCallOnApp( "baseapp", 1, snippet )

		snippet = """
		bot = BigWorld.bots.values()[0]
		srvtest.finish( bot.player.friendStatus )
		"""
		statusReceived = self.cc.sendAndCallOnApp( "bots", None, snippet )
		
		self.assertTrue( statusToSend == statusReceived,
						"setFriendStatus wasn't called" )
		
		
		

