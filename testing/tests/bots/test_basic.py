import time
from bwtest import TestCase
from helpers.cluster import ClusterController


class BasicBotsTest( TestCase ):
	
	name = "BasicBots"
	tags = []
	description = "Simple smoke test of basic bot functionality"
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()
	
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots", 1 )
		self.cc.bots.add( 1 )
		
		snippet = """
		bot = [e for e in BigWorld.entities.values() if e.className == "Avatar"][0]
		srvtest.assertFalse( bot.isDestroyed )
		srvtest.finish( (bot.position.x, bot.position.y, bot.position.z) )
		"""
		previousBotPosition = None
		for i in range( 5 ):
			botPosition = self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
			if previousBotPosition:
				self.assertTrue( botPosition[0] > previousBotPosition[0],
								"Bot didn't move on the x-axis" )
				self.assertTrue( int(botPosition[1]) == 0, 
								"Bot moved on the y-axis" )
				self.assertTrue( int(botPosition[2]) == 0, 
								"Bot moved on the z-axis" )
			previousBotPosition = botPosition
			time.sleep( 6 )
		
		self.cc.bots.delete( 1 )
		snippet = """
		bots = [e for e in BigWorld.entities.values() if e.className == "Avatar"]
		if bots:
			srvtest.assertTrue( bots[0].isDestroyed )
		srvtest.finish()
		"""
		
		self.cc.sendAndCallOnApp( "cellapp", 1, snippet )
		
		
		
class BotParamsTest( TestCase ):
	
	name = "BotParams"
	tags = []
	description = "Tests the accessibility of basic bot parameters"\
				" such as player and loginName"
	
	
	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()

	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots" )
		self.cc.bots.add( 10 )
		snippet = """
		import re
		import Avatar
		for bot in BigWorld.bots.values():
			m = re.match( "Bot_\d+_%s:\d+", bot.loginName )
			srvtest.assertTrue( m != None, \
								"Bot loginName didn't have the correct pattern")
			srvtest.assertTrue( isinstance( bot.player, Avatar.PlayerAvatar ), \
								"Bot player wasn't the correct class")
		srvtest.finish()
		""" % self.cc._machines[0]
		self.cc.sendAndCallOnApp( "bots", None, snippet )
		
		