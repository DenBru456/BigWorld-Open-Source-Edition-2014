"This module implements the LightGuard entity."

# Blacklist: Creature.Creature

import BigWorld
import math
import random
import LightGuardPatrolRoutes as Patrol


def pointsEqual(v1, v2):
	return math.fabs(v1[0]-v2[0]) < 0.1 and math.fabs(v1[2]-v2[2]) < 0.1


class LightGuard( BigWorld.Entity ):

	PATROL_VELOCITY = 1.5
	MAX_MOVE = 5.0
	LIFETIME_MIN = 19 * 60 # Seconds to live
	LIFETIME_MAX = 21 * 60 # Seconds to live

	WAIT_TIMER = 0
	LIFE_TIMER = 1

	#-------------------------------------------------------------------------
	# Constructor.
	#-------------------------------------------------------------------------

	def __init__( self ):
		BigWorld.Entity.__init__( self )

		if not Patrol.validListIndex( self.patrolListIndex ):
			print "LightGuard got bad patrol list index %d, suiciding" % self.patrolListIndex
			self.destroy()
			return

		if self.patrolNode < 0:
			self.patrolNode = 0

		self.nextPos = self.position

		self.addTimer(
			random.randrange( LightGuard.LIFETIME_MIN,
				LightGuard.LIFETIME_MAX ),
			0, LightGuard.LIFE_TIMER )

		self.think()


	#-------------------------------------------------------------------------
	# This method decides what to do next. It should be called whenever
	# our inputs change.
	#-------------------------------------------------------------------------
	def think(self):
		self.doPatrol()

	#-------------------------------------------------------------------------
	# This method is called to continue our patrol. Either for the first
	# time, or when we reach a waypoint along the route.
	#-------------------------------------------------------------------------

	def doPatrol(self):
		# If we have arrived, advance to the next point.
		# or if we can't get there
		if pointsEqual( self.position, self.nextPos ):
			self.nextPatrolNode()

		if not self.moveToPosition( self.nextPos,
						LightGuard.PATROL_VELOCITY, 50 ):
			self.doWait()

	#-------------------------------------------------------------------------
	# This method is called to wait and attempt to patrol later. This is
	# necessary for the cases where patrolling fails because the chunks are
	# not yet loaded.
	#-------------------------------------------------------------------------
	def doWait( self ):
		self.controllerId = self.addTimer( 5, 0, LightGuard.WAIT_TIMER )

	#-------------------------------------------------------------------------
	# This method handles a timer event.
	#-------------------------------------------------------------------------

	def onTimer( self, controllerId, userData ):
		if userData == LightGuard.WAIT_TIMER:
			self.controllerId = 0
			self.think()
		elif userData == LightGuard.LIFE_TIMER:
			self.destroy()
		else:
			print "LightGuard.onTimer: Unexpected timer %d expired" % userData

	#-------------------------------------------------------------------------
	# This method find the next point that this entity should walk to.
	#-------------------------------------------------------------------------

	def nextPatrolNode( self ):
		tries = 0

		while tries < 4:
			tries += 1
			self.patrolNode = Patrol.nextNodeIndex( self.patrolListIndex,
				self.patrolNode )
			nextPos = Patrol.patrolNode( self.patrolListIndex,
				self.patrolNode )

			nextPos = self.canNavigateTo( nextPos )
			if nextPos != None:
				self.nextPos = nextPos
				return

	#-------------------------------------------------------------------------
	# This method cancels whatever action we were previously doing.
	#-------------------------------------------------------------------------

	def cancelCurrent(self):
		if(self.controllerId != 0):
			self.cancel(self.controllerId)
			self.controllerId = 0

	#-------------------------------------------------------------------------
	# This method moves us to a certain position.
	#-------------------------------------------------------------------------

	def moveToPosition( self, position, velocity, maxMove = MAX_MOVE ):
		self.cancelCurrent()

		try:
			self.controllerId = self.navigateStep(position, velocity, maxMove)
		except:
			return False

		return True

	#-------------------------------------------------------------------------
	# This method is called when we've finished moving to a point.
	#-------------------------------------------------------------------------

	def onMove(self, controllerId, userId):
		assert( 1 or controllerId or userId )

		self.controllerId = 0

		# Record the time in seconds that we arrived,
		# to use for accuracy, and for patrolling.
		self.think()

# LightGuard.py
