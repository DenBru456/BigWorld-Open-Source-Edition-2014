import logging

import BigWorld

class Avatar( BigWorld.Entity ):

	def onBecomePlayer( self ):
		self.__class__ = SpamAvatar
		self.onBecomePlayer()

gSpamBot = None

class Spammer():
	def __init__( self, bot, dts, period ):
		clientApp = bot.clientApp

		def spamTestOwnClient():
			bot.cell.testThrottlingOwnClient()

		def spamTestAllClients():
			for ent in clientApp.entities.values():
				if type( ent ) == type( bot ):
					ent.cell.testThrottlingAllClients()

		def spamTestBase():
			bot.base.testThrottlingBase()


		t1 = clientApp.addTimer( dts[ 0 ], spamTestOwnClient, True )
		t2 = clientApp.addTimer( dts[ 0 ], spamTestAllClients, True )
		t3 = clientApp.addTimer( dts[ 0 ], spamTestBase, True )

		def killTimer0():
			clientApp.delTimer( t1 )
			clientApp.delTimer( t2 )
			clientApp.delTimer( t3 )

			tt1 = clientApp.addTimer( dts[ 1 ], spamTestOwnClient, True )
			tt2 = clientApp.addTimer( dts[ 1 ], spamTestAllClients, True )
			tt3 = clientApp.addTimer( dts[ 1 ], spamTestBase, True )

			def killTimer1():
				clientApp.delTimer( tt1 )
				clientApp.delTimer( tt2 )
				clientApp.delTimer( tt3 )

				ttt1 = clientApp.addTimer( dts[ 2 ], spamTestOwnClient, True )
				ttt2 = clientApp.addTimer( dts[ 2 ], spamTestAllClients, True )
				ttt3 = clientApp.addTimer( dts[ 2 ], spamTestBase, True )


			clientApp.addTimer( period, killTimer1, False )

		clientApp.addTimer( period, killTimer0, False )


class SpamAvatar( BigWorld.Entity ):

	def onBecomePlayer( self ):
		print "SpamAvatar.onBecomePlayer"
		global gSpamBot

		if gSpamBot is None:
			gSpamBot = Spammer( self, [4.0, 1.5, 0.3], 30.0 )

	def onBecomeNonPlayer( self ):
		self.__class__ = Avatar
