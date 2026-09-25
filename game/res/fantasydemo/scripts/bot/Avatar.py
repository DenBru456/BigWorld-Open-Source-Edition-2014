import random
import time

import BigWorld
from Math import *

# Some different bots behaviours you can use
BOTS_PATROL = 0
BOTS_FIGHT_EACH_OTHER = 1
BOTS_TESTING = 2
BOTS_TEST_THROTTLED_METHODS = 3


MODE = BOTS_PATROL

class Avatar( BigWorld.Entity ):

	"""
	This method sets our class to player type. This is analogous to
	the client PlayerAvatar
	"""
	def onBecomePlayer( self ):
		if MODE == BOTS_FIGHT_EACH_OTHER:
			self.__class__ = CombatAvatar
		elif MODE == BOTS_TESTING:
			self.__class__ = TestAvatar
		elif MODE == BOTS_PATROL:
			self.__class__ = PatrolAvatar
		elif MODE == BOTS_TEST_THROTTLED_METHODS:
			self.__class__ = SpamAvatar

		self.onBecomePlayer()


# ----------------------------------------------------------------------
# Section: BOTS_FIGHT_EACH_OTHER
# ----------------------------------------------------------------------

# Bots will hunt each other down and shoot each other to death in this mode
COMBAT_RADIUS = 300

class CombatAvatar( BigWorld.Entity ):

	# Initialise the Player Avatar
	def onBecomePlayer( self ):
		print "CombatAvatar.onBecomePlayer"

		# This is the ID of the guy we're hunting down
		self.targetID = None

		# This is where we're headed
		self.dest = None

		# Draw your gun
		self.cell.setRightHand( 1 )

		# Disable movement controller
		self.clientApp.autoMove = False

		# Next time I can shoot again
		self.reloadTime = 0.0

		# Teleport somewhere
		self._randomTeleport()

		# Re-acquire targets every few seconds
		self.targetTimer = self.clientApp.addTimer( 5.0, self._chooseTarget, True )

	def onBecomeNonPlayer( self ):
		self.__class__ = Avatar

	def onTick( self, curTime ):

		# We aren't doing anything if we're dead
		if self.healthPercent <= 0:
			return

		# If our target has gone out of range, forget em
		if self.targetID and \
			   not self.clientApp.entities.has_key( self.targetID ):
			self.targetID = None

		# If we haven't found anyone to target yet, look for em
		if self.targetID is None:
			self._chooseTarget()
			if self.targetID is None:
				return

		# We have got someone to kill, so check we're near enough to them
		target = self.clientApp.entities[ self.targetID ]
		dist = Vector3( self._position() ).\
			   flatDistTo( Vector3( target.position ) )

		# If we're near enough to the target, start shooting
		if dist < 8.0:

			if self.clientApp.isMoving:
				self.clientApp.stop()

			if target.healthPercent > 0 and curTime >= self.reloadTime:
				self.cell.fireWeapon( self.targetID, 0.5 )
				self.reloadTime = curTime + random.random()

			elif target.healthPercent <= 0:
				self.targetID = None

		# If not, hunt em down
		elif dist > 12.0 and \
			 (not self.clientApp.isMoving or \
			  self.dest.flatDistTo( target.position ) > 25.0):
			self._moveTo( (target.position.x, 0, target.position.z) )

	def fragged( self, killerID ):
		self.clientApp.addTimer( 6.0, self._randomTeleport, False )
		self.clientApp.addTimer( 20.0, self.cell.reincarnate, False )

	# ----------------------------------------------------------------------
	# Section: Private and utility methods
	# ----------------------------------------------------------------------

	def _nearest( self, e1, e2 ):
		mypos = self._position()
		e1pos = e1.position
		e2pos = e2.position
		if (e1pos.x - mypos.x) ** 2 + (e1pos.z - mypos.z) ** 2 <= \
		   (e2pos.x - mypos.x) ** 2 + (e2pos.z - mypos.z) ** 2:
			return e1
		else:
			return e2

	def _position( self ): return self.clientApp.position

	def _moveTo( self, pos ):
		if pos:
			self.dest = Vector3( pos )
			self.clientApp.moveTo( self.dest )

	def _randomTeleport( self ):
		if self.isDestroyed:
			clientApp = self.clientApp
			if clientApp:
				clientApp.delTimer( self.targetTimer )
			return
		self.clientApp.snapTo(
			(random.randint( -COMBAT_RADIUS, COMBAT_RADIUS ), 0,
			 random.randint( -COMBAT_RADIUS, COMBAT_RADIUS )) )

	def _chooseTarget( self ):
		if self.isDestroyed:
			clientApp = self.clientApp
			if clientApp:
				clientApp.delTimer( self.targetTimer )
			return
		candidates = [ e for e in self.clientApp.entities.values() \
					   if e.__class__ == Avatar and e.id != self.id and \
					   e.playerName.startswith( "Bot" ) and \
					   e.healthPercent > 0 ]
		if candidates:
			tgt = reduce( self._nearest, candidates )
			self.targetID = tgt.id
			self.clientApp.faceTowards( tgt.position )
		else:
			self.targetID = None


# ----------------------------------------------------------------------
# Section: BOTS_TESTING
# ----------------------------------------------------------------------

# Test mode, drop whatever code you like in here
class TestAvatar( BigWorld.Entity ):

	# Initialise the Player Avatar
	def onBecomePlayer( self ):
		print "TestAvatar.onBecomePlayer"

		def foo(): print "foo", time.time() 
		def bar(): print "bar", time.time()
		self.clientApp.addTimer( 1.0, foo, False )
		#self.clientApp.addTimer( 3.5, bar, True )

	def onBecomeNonPlayer( self ):
		self.__class__ = Avatar


# ----------------------------------------------------------------------
# Section: BOTS_PATROL
# ----------------------------------------------------------------------

class PatrolAvatar( BigWorld.Entity ):

	# Initialise the Player Avatar
	def onBecomePlayer( self ):
		print "PatrolAvatar.onBecomePlayer"

	def onBecomeNonPlayer( self ):
		self.__class__ = Avatar


# ----------------------------------------------------------------------
# Section: BOTS_TEST_THROTTLED_METHODS
# ----------------------------------------------------------------------

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


# Avatar.py
