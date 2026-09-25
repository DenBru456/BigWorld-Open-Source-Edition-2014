import bwtest
from helpers.cluster import ClusterController
import time

USER_DATA = 8

class TimersTest( bwtest.TestCase ):
	name = "Timers"
	description = "Test timers"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.cc.start()
		self.cc.startProc( "bots", 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def bigworldTimer( self, app ):
		# Add timer
		procOrd = 1
		if ( app == "bots" ):
			procOrd = None
		snippet1 = """
		BigWorld.onBigWorldTimer = 0

		global timerID

		def onTimer(*args):
			BigWorld.onBigWorldTimer += 1
			if BigWorld.onBigWorldTimer == 1:
				global timerID
				srvtest.finish( timerID )

		timerID = BigWorld.addTimer( onTimer, 0.1, 0.1 )
		"""
		timerID = self.cc.sendAndCallOnApp( app, procOrd, snippet = snippet1 )

		# Let the timer repeat
		time.sleep( 0.5 )

		# Delete the timer
		snippet2 = """
		BigWorld.delTimer( %s )
		srvtest.finish( BigWorld.onBigWorldTimer )
		""" % timerID
		beforeCount = self.cc.sendAndCallOnApp( app, procOrd, snippet = snippet2 )

		# Lets see if the deleted timer repeats
		time.sleep( 0.5 )

		snippet3 = "srvtest.finish( BigWorld.onBigWorldTimer )"
		afterCount = self.cc.sendAndCallOnApp( app, procOrd, snippet = snippet3 )

		self.assertEqual( beforeCount, afterCount )



	def entityTimer( self, app ):
		procOrd = 1
		if app == "bots":
			procOrd = None
			snippetAvatar = """
		avatar = BigWorld.bots.values()[0].player
			"""
		else:
			snippetAvatar = """
		for e in BigWorld.entities.values():
			if e.__class__.__name__ == "Avatar":
				avatar = e
				break
			"""

		if app == "cellapp":
			snippetDelTimer = """
		avatar.cancel( %s )
			"""
		else:
			snippetDelTimer = """
		avatar.delTimer( %s )
			"""

		# Trigger timers via Entity.addTimer
		snippet1 = """
		BigWorld.onEntityTimer = 0

		global timerID

		def onTimer( timerHandler, userData ):
			BigWorld.onEntityTimer += 1
			if BigWorld.onEntityTimer == 1:
				global timerID
				srvtest.finish( (userData, timerID) )

		%s
		avatar.onTimer = onTimer
		timerID = avatar.addTimer( 0.1, 0.1, %s )
		""" % (snippetAvatar, USER_DATA)
		result, timerID = self.cc.sendAndCallOnApp( app, procOrd, 
												snippet = snippet1 )
		self.assertEqual( result, USER_DATA )

		# Let the timer repeat
		time.sleep( 0.5 )

		# Delete the timer
		snippet2 = """
		%s
		%s
		srvtest.finish( BigWorld.onEntityTimer )
		""" % (snippetAvatar, snippetDelTimer) % timerID
		beforeCount = self.cc.sendAndCallOnApp( app, procOrd, 
											snippet = snippet2 )

		# Lets see if the deleted timer repeats
		time.sleep( 0.5 )

		snippet3 = "srvtest.finish( BigWorld.onEntityTimer )"
		afterCount = self.cc.sendAndCallOnApp( app, procOrd, 
											snippet = snippet3 )

		self.assertEqual( beforeCount, afterCount )


	def runTest( self ):		
		self.cc.bots.add( 1 )

		self.bigworldTimer( "bots" )
		self.bigworldTimer( "baseapp" )
		self.bigworldTimer( "cellapp" )

		self.entityTimer( "bots" )
		self.entityTimer( "baseapp" )
		self.entityTimer( "cellapp" )
