from bwtest import TestCase, config
from helpers.cluster import ClusterController
from helpers.timer import runTimer

class BotInteractionViaCellapp( TestCase ):
	
	name = "Bot Interaction Via Cellapp"
	tags = []
	description = "Tests that multiple bots can call methods"\
				" on each other via a cellapp"
	
	NUM_BOTS = 5
	def setUp( self ):
		self.cc = ClusterController( ["bot_interaction_with_cellapp/res", 
									"simple_space/res"] )
		self.cc.setConfig( "bots/serverName", config.CLUSTER_MACHINES[0] )
		self.cc.setConfig( "bots/port", str(20013+config.CLUSTER_UID) )
		self.cc.setConfig( "loginApp/shouldOffsetExternalPortByUID", "true" )
	
	
	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def checkBotTalkedWatchers( self ):
		botTalkedWatchers =  self.cc.getWatcherValue("bots/botTalked", 
													"bots", None )
		if not botTalkedWatchers:
			return False
		botTalkedWatchers = eval(botTalkedWatchers)
		if (len(botTalkedWatchers) != self.NUM_BOTS):
			return False
		for botTalked in botTalkedWatchers:
			if int( botTalked ) != 10:
				return False
		return True
	
	def runTest( self ):
		self.cc.start()
		self.cc.startProc( "bots", 1 )
		self.cc.bots.add( self.NUM_BOTS )
		runTimer( self.checkBotTalkedWatchers, timeout = 120 )
		