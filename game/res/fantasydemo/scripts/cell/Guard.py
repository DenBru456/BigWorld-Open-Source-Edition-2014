"This module implements the Guard entity."

# Blacklist: Creature.Creature

import BigWorld
import FantasyDemo
import math
import random
import AvatarMode as Mode
import Math
from bwdebug import *
from GameData import GuardData

from Math import Vector3
from Math import Vector4

from Avatar import Avatar
import Creature

# Make striffs run when being shot

def pointsEqual(v1, v2):
	return math.fabs(v1[0]-v2[0]) < 0.1 and math.fabs(v1[2]-v2[2]) < 0.1

# TODO: get these from Item.py
DRUMSTICK_TYPE = 4
GOBLET_TYPE = 17

def isFoodItem(item):
	return item == DRUMSTICK_TYPE or item == GOBLET_TYPE


class GuardNavigationException( Exception ):
	def __init__( self, id, sourceLocation, destination, reason ):
		self.id = id
		self.sourceLocation = sourceLocation
		self.destination = destination
		self.reason = reason

	def __str__( self ):
		return repr( self.id, self.sourceLocation, self.destination, self.reason )


# ------------------------------------------------------------------------------
# Section: Guard
#
#	Sometimes when facing our enemy at point blank, we can't see them.
#	For random movement, favour direction we didn't come from.
# ------------------------------------------------------------------------------

class Guard(Avatar):
	"A Guard entity."

	VISION_FOV = math.pi/3
	VISION_RANGE = 50.0
	VISION_HEIGHT = 1.85
	VISION_PERIOD = 10

	# Vision height on an entity to check if it is visible
	ENTITY_VISION_TARGET_HEIGHT = 1.0

	WAIT_TIMER = Avatar.LAST_TIMER + 1
	DEATH_TIMER = Avatar.LAST_TIMER + 2
	STUCK_TIMER = Avatar.LAST_TIMER + 3

	ENABLE_PATROL_TESTING = 0

	PATROL_VELOCITY = 0.0
	CHASE_VELOCITY = 6.0
	FLEE_VELOCITY = 6.0
	MARCH_VELOCITY = 3.0
	SPRINT_VELOCITY = 7.0

	FORGET_RANGE = 50			# Go outside this range and we will forget.
	COMBAT_RANGE = 25			# Minimum distance before we take a shot.
	STOP_RANGE = 4				# Stop this far from entity.
	HATE_TRANSFER_RANGE = 20	# Range for transferring hate to friends.
	FLEE_HEALTH = 25			# Flee when less than this much health.
	FLEE_DURATION = 60			# Number of seconds for which to flee
	OWNER_WALK_RANGE = 6		# Walk to catch up if this far behind owner.

	AIM_TO_SHOOT = 0.2			# Minimum aim before we take a shot.
	AIM_LOCK_DELTA = 0.3		# Change per second when locked on target.
	AIM_SHOOT_DELTA = -0.4		# Change when we take a shot.
	AIM_HIT_DELTA = -0.2		# Change when we are hit.

	DAMAGE_MULTIPLIER = 1.0		# Scale guard damage.

	GESTURE_CHANCE = 5			# Percent chance of gesture
	EAT_CHANCE = 40
	GESTURES = range(1,20)		# List of valid gestures

	MAX_MOVE = 5.0


	# Spoken when fleeing.
	flightLines = [
		"I will return with reinforcements!",
		"I will return! Mark my words!",
		"I will return!",
		"We shall meet again!",
		"I need help!",
		"To me, sentries! To me!",
		"To me! To me!"
	]

	# Spoken when killed.
	deathLines = [
		"Damn you!",
		"Curse you!",
		"No!",
		"Nooo!",
		"It cannot be!",
		"This cannot be!",
		"Run while you can!",
		"My death will not go unnoticed!",
		"Murderer!"
	]

	#deathLines = [
	#	"Killing me does nothing to help your cause!",
	#	"Killing me will be your last mistake.",
	#	"My comrades will avenge my death!",
	#	"You'll have all the guards after you for killing me!",
	#	"You'll never get away with this!",
	#	"My eyes are submissible as evidence of your crimes!",
	#	"Run while you can, we will hunt you down for this.",
	#]


	# Spoken when attacked or sighted an enemy.
	alertLines = [
		"Halt!",
		"Alarm!",
		"Raise the alarm!",
		"Intruders!",
		"We're under attack!",
		"Help!",
		"Have at you!"
	]

	# Spoken when hate-list has been transferred.
	awakeLines = [
		"I come!",
		"Coming!",
		"At once!",
		"To arms! To arms!",
		"For Bree!",
		"For the protection of Bree!",
		"Charge!"
	]


	# Spoken after the enemy has been slain.
	tauntLines = [
		"May your death bring you peace.",
		"A fitting end for one such as you.",
		"I claim another villain.",
		"It seems you were not as good as I expected.",
		"A little too late to regret your actions?",
		"You have only yourself to blame.",
		"Apology accepted.",
		"Justice has been done."
	]

	#tauntLines = [
	#	"I warned you!",
	#	"Release the hounds!",
	#	"Psst... wanna buy a tv?",
	#	"Get lost!",
	#	"You're going to pay for that.",
	#	"This is going to hurt you a lot and me not at all.",
	#	"I'm going to enjoy killing you.",
	#	"That's it. Time to die, fool!",
	#	"Oh, that was bad mistake!",
	#	"You're going to regret that.",
	#	"Oh, you are -SO- dead.",
	#	"Now you've done it.",
	#	"Come here!",
	#	"That was a bad move.",
	#	"Somebody's going to pay for that.",
	#	"Somebody's going to be hurting."
	#]

	stuckGuards = []

	#-------------------------------------------------------------------------
	# Constructor.
	#-------------------------------------------------------------------------

	def __init__( self ):
		Avatar.__init__( self, None )

		# AOIs are disabled because the current implementation is
		# way too slow with 100 or more guards.

		#	self.setAoIRadius(50)
		#	self.setAoIUpdates(0)

		self.hateList = {}
		self.visibleList = []
		self.visionController = 0


		if Guard.ENABLE_PATROL_TESTING:
			self.stopOffsetX = 0.0
			self.stopOffsetZ = 0.0
		else:
			self.stopOffsetX = random.uniform(0.3, 2.0)
			self.stopOffsetZ = random.uniform(0.3, 2.0)

		# Save the initial camp pos, and pick a random offset from it.
		# Also remember the original rightHand item so we can restore it
		# when we leave our camp.

		self.campCentre = self.position
		self.campCentre = self.position
		self.campPosition = list(self.campCentre)
		angle = random.uniform(-math.pi, math.pi)
		self.campPosition[0] += math.sin(angle) * 2.0
		self.campPosition[2] += math.cos(angle) * 2.0
		self.campItem = self.rightHand
		self.newFleePos()

		self.modelNumber = 0 # use orc model

		self.canBeSeen = 0
		self.startVisionSystem()

		if self.timeToLive > 0.0 and not Guard.ENABLE_PATROL_TESTING:
			self.addTimer( self.timeToLive, 0, Guard.DEATH_TIMER )

		self.modelScale = random.uniform( 0.9, 1.1 )

		self.lastStuckPosition = (0, 0, 0)

		self.cachedPosition = [ (0, 0, 0), (1, 1, 1) ]
		self.isStuck = False

		#if self.initialWait != 0:
			#self.doWait(self.initialWait)
		#else:
			#self.think()
		self.doWait( 1 )

		if FantasyDemo.hasLoadedAllGeometry( self.spaceID ):
			self.addTimer( 0, 2, Guard.STUCK_TIMER )

	#-------------------------------------------------------------------------
	# This method adds an entity to this entity's hate list.
	#
	# @param target		The entity to add
	# @param amount		The amount of hate, as a float
	#-------------------------------------------------------------------------

	def hate( self, target, amount ):
		if self.hateList.has_key(target):
			self.hateList[target] += amount
		else:
			self.hateList[target] = amount

	#-------------------------------------------------------------------------
	# This method is called when somebody enters our AoI.
	#
	# @param id	The ID of the entity that has entered.
	#-------------------------------------------------------------------------

	def enterAoI( self, id ):
		entity = BigWorld.entities[id]
		if entity.__class__ == Guard or entity.__class__ == Creature.Creature:
			self.addTarget(id)

	#-------------------------------------------------------------------------
	# This method is called when somebody leaves our AoI.
	#
	# @param id	The ID of the entity that has left.
	#-------------------------------------------------------------------------

	def leaveAoI( self, id ):
		self.delTarget(id)

	#-------------------------------------------------------------------------
	# This method is called when we are scared.
	#-------------------------------------------------------------------------

	def panic( self ):
		if not self.scaredTime > BigWorld.time():
			self.newFleePos()

		self.scaredTime = BigWorld.time() + Guard.FLEE_DURATION


	def haveWeapon( self ):
		return self.rightHand != -1

	#-------------------------------------------------------------------------
	# This method is called when we take damage.
	# It makes us hate the shooter more.
	#
	# @param shooterId	The ID of the entity that hurt us.
	#-------------------------------------------------------------------------

	def handleHit(self, shooterId):

		if self.mode == Mode.DEAD:
			return

		self.hate(shooterId, 1.0)
		self.transferHateList()
		self.slowTransferHateList()
		self.aim += Guard.AIM_HIT_DELTA

		if(random.random() > 0.5):
			randomLine = random.randint( 0, len( Guard.alertLines ) - 1  )
			self.otherClients.chat( unicode(Guard.alertLines[ randomLine ]) )

		# If we are low health, or unarmed, flee for a while.
		# Strictly speaking, we should check to see if we actually
		# are holding a weapon or not.

		if self.health < Guard.FLEE_HEALTH or not self.haveWeapon():
			self.panic()

		self.think()

	#-------------------------------------------------------------------------
	# This method returns our preferred combat range, given our weapon.
	#-------------------------------------------------------------------------

	def combatRange(self):
		if self.rightHand == 1: # BLASTER
			return self.COMBAT_RANGE
		elif self.rightHand == 2: # STAFF
			return self.COMBAT_RANGE * 2
		elif self.rightHand == 0: # SHREDDER
			return self.COMBAT_RANGE * 2
		elif self.rightHand == 7: # SWORD
			return 2
		elif self.rightHand == 8: # CROSSBOW
			return self.COMBAT_RANGE
		else:
			return 0

	#-------------------------------------------------------------------------
	# This method chooses our attack target. It is based on both hate
	# and distance.
	#-------------------------------------------------------------------------

	def chooseTarget(self):
		bestTarget = -1
		bestValue = 0

		# If we stashed our weapon while around the campfire,
		# its time to bear arms again.
		if self.rightHand != self.campItem:
			self.rightHand = self.campItem

		# If we have a camp spot, and we are too far from it, forget about our
		# hateList.
		if self.campRadius and \
				self.position.distTo( self.campPosition ) > self.campRadius:
			self.target = -1
			self.hateList = {}
			return

		for id in self.hateList.keys():
			try:
				entity = BigWorld.entities[id]
			except:
				del self.hateList[id]
			else:
				dist = self.position.distTo( entity.position )
				value = self.hateList[id] / max(dist, 1.0)

				# If they are not within the hate range, ok forgive em.
				if dist > Guard.FORGET_RANGE:
					del self.hateList[id]

				# If they are dead, forgive em also.
				elif entity.isDead():
					del self.hateList[id]

				elif value > bestValue:
					bestTarget = id
					bestValue = value

		self.target = bestTarget

	#-------------------------------------------------------------------------
	# This method decides what to do next. It should be called whenever
	# our inputs change.
	#-------------------------------------------------------------------------

	def think(self):
		try:

			# Dead guys don't think.
			if self.mode == Mode.DEAD:
				return

			# If we hate, then keep our weapon ready.

			if len(self.hateList):
				self.chooseTarget()
				self.transferHateList()
				if self.haveWeapon():
						mode = Mode.COMBAT_UNLOCKED
				else:
						mode = Mode.NONE
			else:
				self.target = -1
				mode = Mode.NONE

			# If we have a target that we want to pursue, either chase
			# it or shoot it, depending on its distance from us.

			if self.scaredTime > BigWorld.time():
				self.doFlee()

			elif self.target != -1 and self.haveWeapon():
				entity = BigWorld.entities[self.target]
				d = self.position.distTo( entity.position )

				if d < self.combatRange() and self.visibleList.count(self.target):
					mode = Mode.COMBAT_LOCKED
					self.doCombat()
				else:
					self.gotoEntity(BigWorld.entities[self.target], Guard.CHASE_VELOCITY)

			# If we have a patrol path, then patrol.

			elif self.ownerId != -1:
				self.gotoOwner()

			elif self.initialPatrolNode != None:
				self.doPatrol()
			elif self.campRadius != 0:
				self.doCamp()

			# If we hate somebody, or we have an owner,
			# and we are currently doing nothing, then stay alert.

			if (len(self.hateList) > 0 or self.ownerId != -1) \
				and self.controllerId == 0:
				self.doWait(1)

			# Make sure our combat mode is correct.
			if self.mode != mode:
				self.mode = mode

			# Otherwise we have nothing to do, wait until our inputs change.
			if self.controllerId == 0:
				self.doWait(5)

		except GuardNavigationException, e:
			return

	#-------------------------------------------------------------------------
	# This method is called when we die.
	#-------------------------------------------------------------------------

	def handleDeath(self):
		self.cancelCurrent()
#		self.otherClients.scanForTargets(0.0, 0.0, 0.0)
		randomLine = random.randint( 0, len( Guard.deathLines ) - 1  )
		self.otherClients.chat( unicode(Guard.deathLines[ randomLine ]) )
		self.controllerId = self.addTimer(300, 0, Guard.DEATH_TIMER)
		self.cancel(self.visionController)

	#-------------------------------------------------------------------------
	# This method faces towards a position.
	#-------------------------------------------------------------------------

	def facePosition(self, pos):
		vector = (pos[0] - self.position[0], 0, pos[2] - self.position[2])
		yaw = math.atan2(vector[0], vector[2])
		self.direction = (0, 0, yaw)

	#-------------------------------------------------------------------------
	# This method cancels whatever action we were previously doing.
	#-------------------------------------------------------------------------

	def cancelCurrent(self):
		if(self.controllerId != 0):
			self.cancel(self.controllerId)
			self.controllerId = 0
			self.stopTime = BigWorld.time()
			self.patrolling = 0

	#-------------------------------------------------------------------------
	# This method moves us to a certain position.
	#-------------------------------------------------------------------------

	def moveToPosition(self, position, velocity, maxMove = MAX_MOVE):
		self.cancelCurrent()

		try:
			self.controllerId = self.navigateStep(position, velocity, maxMove)

			if not self.moving:
				self.moving = 1

		except Exception, e:
			print "Guard", self.id, "unable to move from", self.position, "to", position, ":", e
			if not Guard.ENABLE_PATROL_TESTING:
				self.doTeleport( self.campCentre, self.direction )
				self.nextPatrolNode = self.initialPatrolNode
				self.doWait( 5 )

			if self.moving:
				self.moving = 0

		return self.moving

	#-------------------------------------------------------------------------
	# Some sort of a damage curve approximating what the client does.
	#-------------------------------------------------------------------------

	def aimToDamage(self, aim):
		if aim < 0.15:
			return 0
		elif aim < 0.575:
			return (aim - 0.15) / (0.575 - 0.15) * 0.3
		else:
			return (aim - 0.575) / (1.0 - 0.575) * 0.5 + 0.5

	#-------------------------------------------------------------------------
	# This method is called to handle combat. It should shoot if we are
	# able. Or set a timer to wait, if our weapon is not ready to shoot yet.
	#-------------------------------------------------------------------------

	def doCombat(self):

		# Always face the target.
		entity = BigWorld.entities[self.target]
		self.facePosition(entity.position)

		# If this is the first time we've been called since we stopped
		# moving, then aim is zero. Otherwise increase the aim based on
		# the amount of time that has passed since we last aimed.
		now = BigWorld.time()

		if self.aimTime < self.stopTime:
			self.aim = 0.0
		else:
			timePassed = now  - self.aimTime
			self.aim += (timePassed * Guard.AIM_LOCK_DELTA)

		# Cap the aim
		if self.aim > 1.0:
			self.aim = 1.0

		self.aimTime = now

		# If we are ready to take a shot, then take one.
		if self.aim > Guard.AIM_TO_SHOOT:
			self.fireWeapon(self.id, self.target, self.aimToDamage(self.aim))
			self.aim += Guard.AIM_SHOOT_DELTA
			if self.aim < 0.0:
				self.aim = 0.0

		# Wait a random amount of time before the next combat round,
		# up to 2 seconds.
		self.doWait(random.random() * 1.5 + 0.5)

	#-------------------------------------------------------------------------
	# This method returns the amount of damage we do.
	# Should really call the base method to determine the weapon type,
	# but can't do this just yet.
	#-------------------------------------------------------------------------

	def getDamage(self):
		return 25.0 * Guard.DAMAGE_MULTIPLIER

	#-------------------------------------------------------------------------
	# This method is called to chase our target. If we can't get any closer,
	# then stop and face the target.
	#-------------------------------------------------------------------------

	def doChase(self):
#		self.otherClients.scanForTargets(0.0, 0.0, 0.0)
		entity = BigWorld.entities[self.target]

		if not self.moveToPosition(entity.position, Guard.CHASE_VELOCITY):
			self.cancelCurrent()
			self.facePosition(entity.position)

	#-------------------------------------------------------------------------
	# Calculate a new flee position
	#-------------------------------------------------------------------------

	def newFleePos(self):
		try:
			roughFleePosition = self.position + Math.Vector3( random.uniform( -75, 75 ), 0, random.uniform( -75, 75 ) )

			self.fleePos = BigWorld.findRandomNeighbourPoint( self.spaceID, roughFleePosition, 25 )

		except:
			# NavMesh not be loaded yet
			self.fleePos = None
			self.doWait( 2.0 )

	#-------------------------------------------------------------------------
	# This method is called to run from our target. If we can't get any
	# further away, run in a random direction.
	#-------------------------------------------------------------------------

	def doFlee(self):
		if self.fleePos is None or self.position.distTo( self.fleePos ) < 10.0:
			self.newFleePos()

		if self.fleePos is not None:
			if not self.moveToPosition(self.fleePos, Guard.FLEE_VELOCITY):
				self.newFleePos()

	#-------------------------------------------------------------------------
	# This method waits for a period of time.
	# And maybe does a gesture too.
	#-------------------------------------------------------------------------

	def doWait(self, seconds):
		self.cancelCurrent()
		self.controllerId = self.addTimer(seconds, 0, Guard.WAIT_TIMER)

		if self.moving:
			self.moving = 0

		if isFoodItem(self.rightHand) and random.randrange(100) < self.EAT_CHANCE:
			self.eat(self.rightHand)
			return

		if random.randrange(100) < self.GESTURE_CHANCE:
			i = random.randrange(len(self.GESTURES))
			self.didGesture( self.id, self.GESTURES[i] )

	#-------------------------------------------------------------------------
	# This method gets the next node to traverse to on a patrol list
	#-------------------------------------------------------------------------

	def getNextPatrolNode( self, currentNode, lastNode ):
		# pick a node from the linked list, by importance
		return currentNode.nextPatrolNodeByImportance( lastNode )


	def setDestinationAndSpeed( self ):

		if Guard.ENABLE_PATROL_TESTING:
			destinationPoint = self.nextPatrolNode.position
		else:
			try:
				destinationPoint = BigWorld.findRandomNeighbourPoint(	self.spaceID,
																		self.nextPatrolNode.position,
																		self.nextPatrolNode.radius )
			except ValueError, e:
				e = GuardNavigationException( self.id, self.position, self.nextPatrolNode.position, "findRandomNeighbourPoint failed" )
				raise e


		try:
			destination = self.canNavigateTo( destinationPoint )

			if destination is None:
				raise ValueError
			self.destination = destination

			if Guard.PATROL_VELOCITY > 0:
				self.speed = Guard.PATROL_VELOCITY
			else:
				self.speed = self.lastPatrolNode.departureSpeed
		except Exception:
			e = GuardNavigationException( self.id, self.position, destinationPoint, "canNavigateTo failed" )
			raise e



	#-------------------------------------------------------------------------
	# This method is called to continue our patrol. Either for the first
	# time, or when we reach a waypoint along the route.
	#-------------------------------------------------------------------------

	def doPatrol(self):
		if self.nextPatrolNode == None and \
					self.initialPatrolNode != None:
			try:
				self.nextPatrolNode = self.initialPatrolNode
				self.lastPatrolNode = self.initialPatrolNode
				self.doTeleport( self.nextPatrolNode.position, ( 0, 0, 1 ) )
				self.setDestinationAndSpeed()
			except BigWorld.UnresolvedUDORefException:
				self.nextPatrolNode = None
				self.lastPatrolNode = None
				self.doWait( random.uniform( 9, 11 ) )
				return
			except GuardNavigationException, e:
				if FantasyDemo.hasLoadedAllGeometry( self.spaceID ):
					if self.lastStuckPosition != self.position:
						# Potential Causes:
						#  - initialPartrolNode is not on a waypoint
						print "Guard", self.id, "in space", self.spaceID, \
							"failed to restart navigation from", \
							self.initialPatrolNode.guid, "at position", \
							self.position, "to", \
							e.destination, "with reason", e.reason
					self.lastStuckPosition = Vector3( self.position )
				self.nextPatrolNode = None
				self.lastPatrolNode = None
				self.doWait( 0.1 )
				return


		closeEnough = 2.0
		dist = self.destination.flatDistTo( self.position )
		if (dist > closeEnough):
			# we haven't arrived yet, so keep moving

			# filter the destination again through canNavigateTo
			filteredDest = self.canNavigateTo( self.destination )

			if filteredDest is None and \
				self.lastPatrolNode is not None:

				self.lastPatrolNode, self.nextPatrolNode = self.nextPatrolNode, self.lastPatrolNode

				try:
					self.setDestinationAndSpeed()
				except BigWorld.UnresolvedUDORefException:
					self.lastPatrolNode = self.nextPatrolNode
					self.nextPatrolNode = None
				except GuardNavigationException, e:
					if FantasyDemo.hasLoadedAllGeometry( self.spaceID ):
						print "Guard", self.id, "in space", self.spaceID, \
							"failed to navigate from", \
							self.nextPatrolNode.guid, "at position", \
							self.position, "to", e.destination, \
							"with reason", e.reason
					self.nextPatrolNode = None
					self.lastPatrolNode = None

				self.doWait( 0.1 )
				return

			self.destination = filteredDest
			self.moveToPosition( self.destination, self.speed, 50 )
			return

		# We have arrived at our destination. If we have to wait, then wait.
		waitSecs = 0.0
		try:
			waitSecs = self.nextPatrolNode.waitSecs
		except BigWorld.UnresolvedUDORefException:
			pass

		# Get the next node here, in case we have to wait
		try:
			newLastPatrolNode = self.nextPatrolNode
			self.nextPatrolNode  = self.getNextPatrolNode(self.nextPatrolNode, self.lastPatrolNode)
			self.lastPatrolNode = newLastPatrolNode
			if self.nextPatrolNode != None:
				self.setDestinationAndSpeed()
			else:
				print "Guard", self.id, "reached a dead end in node", \
					newLastPatrolNode.guid, "at position", self.position
		except BigWorld.UnresolvedUDORefException:
			self.doWait( random.uniform( 9, 11 ) )
			return
		except GuardNavigationException, e:
			if FantasyDemo.hasLoadedAllGeometry( self.spaceID ):
				# Potential Causes:
				# - The guard can not navigate from its current position 
				#   to nextPatrolNode, either no path, or no waypoint
				print "Guard", self.id, "in space", self.spaceID, \
					"failed to navigate from", self.nextPatrolNode.guid, \
					"at position", self.position, "to", e.destination, \
					"with reason", e.reason
			self.nextPatrolNode = None
			self.lastPatrolNode = None
			self.doWait( 0.1 )
			return

		if waitSecs > 0.0:
			# Wait 'waitSecs' seconds
			self.doWait( waitSecs )
		else:
			# No need to wait, so keep moving to the next patrol node
			if self.nextPatrolNode != None:
				self.moveToPosition(self.destination, self.speed, 50)
				self.patrolling = 1
			else:
				self.patrolling = 0

	#-------------------------------------------------------------------------
	# This method is called to return us to our camp.
	#-------------------------------------------------------------------------

	def doCamp(self):
		d = self.position.distTo( self.campPosition )

		if d > 0.1:
			self.moveToPosition(self.campPosition, Guard.SPRINT_VELOCITY)
		else:
			self.facePosition(self.campCentre)

			if not isFoodItem(self.rightHand):
				possibleItems = [GOBLET_TYPE, DRUMSTICK_TYPE]
				itemIndex = random.randrange(len(possibleItems))
				self.rightHand = possibleItems[itemIndex]


	def doTeleport( self, position, direction ):
		self.teleport( None, position, direction )

		# Workaround for Bug 10961 - Send teleport message to client when teleporting
		self.allClients.resetFilter()

	#-------------------------------------------------------------------------
	# gotoEntity
	#-------------------------------------------------------------------------

	def gotoEntity(self, entity, velocity):
		self.cancelCurrent()

		nearPos = (entity.position[0] + self.stopOffsetX,
				entity.position[1], entity.position[2] + self.stopOffsetZ)

		# Get valid target position
		collideResult = BigWorld.collide(	self.spaceID,
											entity.position,
											nearPos )
		if collideResult:
			nearPos = collideResult[0]

		entityVision = (entity.position[0],
					entity.position[1] + self.ENTITY_VISION_TARGET_HEIGHT,
					entity.position[2])

		guardVision = (self.position[0],
					self.position[1] + self.seeingHeight,
					self.position[2])

		# Check if guard can see the entity
		collideResult = BigWorld.collide(	self.spaceID,
											guardVision,
											entityVision )

		if collideResult or self.position.distTo( entity.position ) > 3.0:
			self.moveToPosition(nearPos, velocity)
		else:
			self.facePosition(entity.position)

	#-------------------------------------------------------------------------
	# gotoOwner
	#-------------------------------------------------------------------------

	def gotoOwner(self):
		try:
			owner = BigWorld.entities[self.ownerId]
		except KeyError:
			self.ownerId = -1
			return

		if not owner or owner.isDead() or \
			( self.position.distTo( owner.position ) > Guard.FORGET_RANGE \
			and not Guard.ENABLE_PATROL_TESTING ):
			self.ownerId = -1
			return

		return self.gotoEntity(owner, Guard.MARCH_VELOCITY)

	#-------------------------------------------------------------------------
	# transferHateList
	#-------------------------------------------------------------------------

	def transferHateList(self):
		hated = self.hateList.keys()
		for id in self.visibleList:
			try:
				e = BigWorld.entities[id]
			except KeyError:
				e = None
			if isinstance(e, Guard) and e.modelNumber == self.modelNumber:
				d = self.position.distTo( e.position )
				if d < Guard.HATE_TRANSFER_RANGE:
					for id in hated:
						e.hate(id, 1.0)

	#-------------------------------------------------------------------------
	# slowTransferHateList
	# Same as transferHateList, but doesn't use AoI. Iterates through
	# every entity in the cell. So don't do this often.
	#-------------------------------------------------------------------------

	def slowTransferHateList(self):
		hated = self.hateList.keys()
		for e in BigWorld.entities.values():
			if isinstance(e, Guard) and e.modelNumber == self.modelNumber:
				d = self.position.distTo( e.position )
				if d < Guard.HATE_TRANSFER_RANGE:
					for id in hated:
						e.hate(id, 1.0)

	#-------------------------------------------------------------------------
	# This method is called when we've finished moving to a point.
	#-------------------------------------------------------------------------

	def onMove(self, controllerId, userId):
		assert( 1 or controllerId or userId )

		self.controllerId = 0
		self.aim = 0.0
		self.patrolling = 0

		# Record the time in seconds that we arrived,
		# to use for accuracy, and for patrolling.
		self.stopTime = BigWorld.time()
		self.think()

	#-------------------------------------------------------------------------
	# This method is called when a guard fails to move enough
	#-------------------------------------------------------------------------

	def onMoveFailure(self, controllerId, userId):
		assert( 1 or controllerId or userId )

		self.controllerId = 0
		self.aim = 0.0
		self.patrolling = 0

		# Continue to think
		self.doWait( 1.0 )

	#-------------------------------------------------------------------------
	# This method is called when a timer expires.
	#-------------------------------------------------------------------------

	def onTimer(self, timerId, userId):
		assert( 1 or timerId ) # Not used

		if userId == Guard.WAIT_TIMER:
			self.controllerId = 0
			self.think()
		elif userId == Guard.DEATH_TIMER:
			self.destroy()
		elif userId == Guard.STUCK_TIMER:

			# Check to see if the guard is stuck
			self.setStuck( \
					self.position == self.cachedPosition[ 0 ] and \
					self.position == self.cachedPosition[ 1 ] )
			self.cachedPosition[ 1 ] = Math.Vector3( self.cachedPosition[ 0 ] )
			self.cachedPosition[ 0 ] = Math.Vector3( self.position )
		else:
			Avatar.onTimer( self, timerId, userId )

	#-------------------------------------------------------------------------
	# This method is called when a player wants us to start following.
	#-------------------------------------------------------------------------

	def startFollow(self, playerId):
		player = BigWorld.entities[playerId]
		if not player:
			return

		self.ownerId = playerId
		self.think()

	#-------------------------------------------------------------------------
	# This method is called when a player wants us to stop following.
	#-------------------------------------------------------------------------

	def stopFollow(self, playerId):
		if self.ownerId == playerId:
			self.ownerId = -1

		self.think()

	#-------------------------------------------------------------------------
	# Prevent people from engaging guards in melee.
	#-------------------------------------------------------------------------

	def isInCloseCombat(self, other):
		raise AssertionError, "Guards can't melee yet!"

	def startVisionSystem( self ):
		self.visionChangesInProgress = 1
		if self.visionController:
			self.cancel( self.visionController )
			self.visionController = 0

		self.visionController = self.addVision( self.VISION_FOV,
			self.VISION_RANGE, self.VISION_HEIGHT * self.modelScale,
			self.VISION_PERIOD )

		self.visionChangesInProgress = 0

	# callback method from vision controller
	def onStartSeeing(self, who):
		self.addTarget( who.id )

	# callback method from vision controller
	def onStopSeeing(self, who):
		self.delTarget( who.id )

	#-------------------------------------------------------------------------
	# This method is called by the client when this NPC can see an avatar.
	# It adds the target to the visible list, and also the hate list if
	# we are aggro.
	#
	# @param targetId	The ID of the target that can be seen.
	#-------------------------------------------------------------------------

	def addTarget( self, targetId ):
		entity = BigWorld.entities[targetId]
		self.visibleList.append(targetId)

		# If we are aggro, add it to the hate list.
		if(self.aggro):
			if isinstance(entity, Avatar) and \
				entity.modelNumber == self.modelNumber:
				pass
			else:
				self.hate(targetId, 1.0)

		if not self.visionChangesInProgress:
			self.think()

	#-------------------------------------------------------------------------
	# This method is called by the client when this NPC can no longer
	# see an avatar.
	#
	# @param targetId	The ID of the target that has vanished
	#-------------------------------------------------------------------------

	def delTarget( self, targetId ):
		if self.visibleList.count(targetId):
			self.visibleList.remove(targetId)

		if(targetId == self.target):
			self.aim = 0.0

		if not self.visionChangesInProgress:
			self.think()


	@staticmethod
	def generateColoursFromRanges( colourRanges ):
		assert len( colourRanges ) == 4
		result = []
		for colourRange in colourRanges:
			assert len( colourRange ) < 256
			result.append( random.randint( 0, len( colourRange ) - 1 ) )
		return tuple( result )

	def setStuck( self, isStuck ):

		if isStuck == self.isStuck:
			return

		if isStuck:
			if Guard.stuckGuards.count( self.id ) == 0:
				Guard.stuckGuards.append( self.id )
				Guard.stuckGuards.sort()
		else:
			try:
				Guard.stuckGuards.remove( self.id )
			except ValueError:
				pass

		self.isStuck = isStuck

	def onAllSpaceGeometryLoaded( self, spaceID, isBootStrap, mapping ):
		if spaceID == self.spaceID:
			self.addTimer( 0, 2, Guard.STUCK_TIMER )


# Guard watchers

# Patrol velocity
def setPatrolVelocity( x ):
	Guard.PATROL_VELOCITY = float( x )

def getPatrolVelocity():
	return Guard.PATROL_VELOCITY

BigWorld.addWatcher( 'script/Guard/patrolVelocity', getPatrolVelocity,\
		setPatrolVelocity )


# March velocity
def setMarchVelocity( x ):
	Guard.MARCH_VELOCITY = float( x )

def getMarchVelocity():
	return Guard.MARCH_VELOCITY

BigWorld.addWatcher( 'script/Guard/marchVelocity', getMarchVelocity,\
		setMarchVelocity )


# Stuck guards
def getStuckGuards():
	return Guard.stuckGuards

BigWorld.addWatcher( 'script/Guard/notMoving', getStuckGuards )


# Guard.py



