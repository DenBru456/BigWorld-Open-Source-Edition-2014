"This module implements the Creature entity."

# BigWorld Modules
import BigWorld
import Avatar
import Math
from GameData import CreatureData

import bwdecorators

# Python modules
import random
import math

MAX_RANGE = 25
MIN_RANGE = 1

#todo: replace this with math module
def distance(v1, v2):
	"Returns the distance between two 3d vectors"
	x = v2[0] - v1[0]
	z = v2[2] - v1[2]
	#ignore y value due to the current 13k hack
	return math.sqrt(x * x + z * z)

def angleDist(a1, a2):
	d = math.fabs(a1 - a2)
	if d > math.pi:
		return (math.pi * 2) - d
	else:
		return d

def normaliseAngle(a):
	if a > math.pi:
		return a - (math.pi * 2)
	elif a < -math.pi:
		return a + (math.pi * 2)
	else:
		return a


# ------------------------------------------------------------------------------
# Section: class Creature Brains
# ------------------------------------------------------------------------------
class StriffBrain:
	def __init__( self ):
		pass

	def think( self, creature ):
		decision = random.random()
		creatureType = creature.creatureType
		canGraze = CreatureData.GRAZE in CreatureData.allowedActions[creatureType]
		canStretch = CreatureData.STRETCH in CreatureData.allowedActions[creatureType]

		if decision < 0.15 and canGraze:
			creature.otherClients.performAction( CreatureData.GRAZE )
		elif decision < 0.2 and canStretch:
			creature.otherClients.performAction( CreatureData.STRETCH )
		elif decision < 0.5:
			creature.doMove()


class SpiderBrain:
	def __init__( self ):
		pass

	def think( self, creature ):
		decision = random.random()
		creatureState = creature.creatureState

		if creatureState == CreatureData.HIDDEN:
			if decision < 0.5:
				creature.creatureState = CreatureData.ALIVE
		else:
			if decision < 0.07:
				creature.creatureState = CreatureData.HIDDEN
				creature.doWait( 10.0 )
			elif decision < 0.5:
				creature.doMove()


# ----------------------------------------------------------------------------
# Section: class Creature
# ----------------------------------------------------------------------------
class Creature( BigWorld.Entity ):
	"A Creature entity."

	WAIT_TIMER		= 0
	DEATH_TIMER		= 1

	#If a creature type has no brain entry, the brain type for UNKNOWN is used.
	brain = \
	{
		CreatureData.UNKNOWN: StriffBrain(),
		CreatureData.STRIFF: StriffBrain(),
		CreatureData.SPIDER: SpiderBrain(),
	}

	#------------------------------------------------------------------------
	# Constructor
	#------------------------------------------------------------------------

	def __init__( self ):
		BigWorld.Entity.__init__( self )

		self.initHealthFromType()
		self.updateHealth()
		self.enemyList = []
		self.friendList = []

		self.xorigin = self.position[0]
		self.zorigin = self.position[2]

		self.creatureName = self.getNameFromType()

		# random yaw
		yaw = random.uniform(-math.pi, math.pi)

		self.direction = (0.0, 0.0, yaw)

		self.moveRange = MAX_RANGE

		# Striff will flee if another non-Creature Entity moves into this Trap
		self.addProximity( CreatureData.FLEE_RANGE )

		self.think()

		# TODO: Should handle the case where creatureState is not ALIVE during
		# recovery. Should probably destroy immediately.


	#------------------------------------------------------------------------
	# These functions implement fleeing from Avatar
	#------------------------------------------------------------------------

	def onLeaveTrap( self, pEntity, trapRange, trapID ):
		if self.enemyList.count( pEntity.id ):
			self.enemyList.remove( pEntity.id )


	def onEnterTrap( self, pEntity, trapRange, trapID ):

		# If Entity that triggered Trap is an Avatar and
		# Creature is not in use by any Avatar
		if pEntity.__class__ == Avatar.Avatar and self.ownerId != pEntity.id:
			if not self.enemyList.count( pEntity.id ):
				self.enemyList.append( pEntity.id )
			self.think()


	#------------------------------------------------------------------------
	# die
	#------------------------------------------------------------------------
	def die( self, source ):
		"client"
		self.destroy()


	#------------------------------------------------------------------------
	# getNameFromType
	#------------------------------------------------------------------------
	@bwdecorators.callableOnGhost
	def getNameFromType( self ):
		try:
			return CreatureData.displayNames[ self.creatureType ]
		except KeyError:
			return CreatureData.displayNames[ CreatureData.UNKOWN ]


	#------------------------------------------------------------------------
	# This method cancels the current action
	#------------------------------------------------------------------------
	def cancelCurrent(self):
		if (self.controllerId != 0):
			self.cancel(self.controllerId)
			self.controllerId = 0


	#------------------------------------------------------------------------
	# This method spawns some body parts.
	#------------------------------------------------------------------------
	def spawnBodyParts(self):
		(item,number) = CreatureData.bodyPartsItem[ self.creatureType ]
		if item != None:
			args = {"classType" : item, "timeToLive" : 120, "onGround" : 1}
			for i in range(number):
				try:
					pos = BigWorld.findRandomNeighbourPoint( self.spaceID, self.position, 0.25 )
				except ValueError, e:
					pos = self.position
				BigWorld.createEntity("DroppedItem", self.spaceID, pos,
						self.direction, args)

		assert( 1 or i ) # To stop warning

	#------------------------------------------------------------------------
	# This method initialises the cell view of our health.
	#------------------------------------------------------------------------
	def initHealthFromType(self):
		(health, maxHealth) = CreatureData.healthTable[ self.creatureType ]
		self.health = health
		self.maxHealth = maxHealth

	#------------------------------------------------------------------------
	# This method updates the client view of our health.
	#------------------------------------------------------------------------
	def updateHealth(self):
		self.healthPercent = int(100.0 * self.health / self.maxHealth)


	#------------------------------------------------------------------------
	# Cell method to let us know we got hit.
	#------------------------------------------------------------------------
	def rangedHit( self, shooterID, damage ):

		# If hidden or dead, we can't be hit right now.
		canBeHit = self.creatureState != CreatureData.HIDDEN and \
					self.creatureState != CreatureData.DEAD_GIBBED and \
					self.creatureState != CreatureData.DEAD
		if not canBeHit: return

		# We are a wild striff again!
		self.ownerId = 0
		shooter = BigWorld.entities[ shooterID ]

		if damage < 1: return

		decision = random.random()

		canHide = CreatureData.HIDE in CreatureData.allowedActions[self.creatureType]
		if decision < 0.5 and canHide:
			canHide = False


		newHealth = self.health - damage
		if newHealth <= 0:
			self.handleDeath()
			canGib = (CreatureData.DIE_GIBBED in CreatureData.allowedActions[self.creatureType])
			if self.health == self.maxHealth and canGib:
				self.otherClients.performAction( CreatureData.DIE_GIBBED )
				self.creatureState = CreatureData.DEAD_GIBBED
				self.spawnBodyParts()
			else:
				self.otherClients.performAction( CreatureData.DIE_KILLED )
				if decision < 0.3:
					self.spawnBodyParts()
			self.health = 0
			self.volatileInfo = (None, None, None, None)
			shooter.gotFrag( self.id )
		else:
			self.health = int( newHealth )
			if canHide:
				self.creatureState = CreatureData.HIDDEN
				self.doWait( 10.0 )
			else:
				self.doFlee(shooter.position, True)

		self.updateHealth()

	#------------------------------------------------------------------------
	# This method is called when we die.
	#------------------------------------------------------------------------
	def handleDeath( self ):
		self.creatureState = CreatureData.DEAD
		self.cancelCurrent()
		self.controllerId = self.addTimer( 180, 0, self.DEATH_TIMER )

		# Warn our buddies

		for id in self.friendList:
			friend = BigWorld.entities[id]
			if friend:
				friend.fearEntity(self.id)
			else:
				self.friendList.remove(id)

	#------------------------------------------------------------------------
	# This method transfers a striff into our enemyList. It is not perfect,
	# if they leave our AoI and return, we will forget. But good enough
	# to give the impression of fleeing from a dead buddy.
	#------------------------------------------------------------------------
	def fearEntity( self, id ):
		if self.friendList.count(id):
			self.friendList.remove(id)
		if not self.enemyList.count(id):
			self.enemyList.append(id)


	#------------------------------------------------------------------------
	# This method returns the closest enemy and their distance from us.
	#------------------------------------------------------------------------
	def findClosestEnemy(self):
		closestEntity = None
		closestDistance = 0

		for id in self.enemyList:
			if not BigWorld.entities.has_key(id):
				self.enemyList.remove(id)
			else:
				entity = BigWorld.entities[id]
				dist = distance(entity.position, self.position)
				if closestEntity == None or dist < closestDistance:
					closestEntity = entity
					closestDistance = dist

		return (closestEntity, closestDistance)


	#------------------------------------------------------------------------
	# This method checks our owner is still valid, and if so, returns
	# our owner and the distance between him and us.
	#------------------------------------------------------------------------
	def getOwner(self):
		owner = None
		dist = 0

		if not BigWorld.entities.has_key(self.ownerId):
			self.ownerId = 0

		if self.ownerId:
			owner = BigWorld.entities[self.ownerId]
			if owner:
				dist = distance(self.position, owner.position)

		if not owner or dist > CreatureData.FORGET_OWNER_RANGE:
			self.ownerId = 0
			return (None, 0)

		if self.lookAtTarget != self.ownerId:
			self.lookAtTarget = self.ownerId

		return (owner, dist)


	#------------------------------------------------------------------------
	# This method is called whenever our inputs change.
	#------------------------------------------------------------------------
	def think(self):

		self.position = (self.position[0], self.position[1], self.position[2])

		# Dead striffs (and fleeing striffs!) don't think
		if self.creatureState == CreatureData.DEAD or \
			self.creatureState == CreatureData.DEAD_GIBBED:
			return

		# If we have an owner, and he is out of range, try to find him.
		(owner, dist) = self.getOwner()

		if owner:
			if dist > CreatureData.CHASE_OWNER_RANGE:
				self.doChase(owner)
			else:
				self.facePosition(owner.position)
				self.doWait(0.5)
			return

		(enemy, dist) = self.findClosestEnemy()

		# If we have an enemy in our AOI, we don't follow normal
		# striff thought patterns. If it is real close then flee,
		# otherwise there is a random chance we will face it.

		if enemy and not owner:
			if dist < CreatureData.FLEE_RANGE:
				self.doFlee(enemy.position)
				return
			elif dist < CreatureData.ATTENTION_RANGE:
				self.facePosition(enemy.position)
				if self.lookAtTarget != enemy.id:
					self.lookAtTarget = enemy.id
				self.doWait(1)
				return

		# Otherwise, if we were doing something else, don't interrupt.
		if self.controllerId:
			return

		# Nobody nearby, we are a happy creature, so do happy creature-like
		# things.
		if self.lookAtTarget:
			self.lookAtTarget = 0

		try:
			brain = Creature.brain[self.creatureType]
		except KeyError:
			brain = Creature.brain[CreatureData.UNKNOWN]

		if brain:
			brain.think( self )

		# If we have nothing else to do, just wait.
		# Note creatures think slower when nobody is around.
		if self.controllerId == 0:
			self.doWait(3)


	#------------------------------------------------------------------------
	# Run for your LIVES!
	#------------------------------------------------------------------------
	def doFlee(self, enemyPos, scared = False):
		self.cancelCurrent()

		if self.lookAtTarget:
			self.lookAtTarget = 0

		if self.ownerId:
			self.ownerId = 0

		enemyYaw = math.atan2(enemyPos[0] - self.position[0],
				enemyPos[2] - self.position[2])
		myYaw = self.direction[2]
		idealYaw = normaliseAngle(enemyYaw + math.pi)

		if scared or angleDist(idealYaw, myYaw) < CreatureData.MAX_YAW_DELTA:
			if scared:
				factor = CreatureData.FLEE_SCARED_FACTOR
			else:
				factor = 1
			zd = math.cos(idealYaw) * CreatureData.FLEE_RUN_DISTANCE * factor
			xd = math.sin(idealYaw) * CreatureData.FLEE_RUN_DISTANCE * factor
			newYaw = idealYaw
		else:
			yaw1 = normaliseAngle(myYaw + CreatureData.MAX_YAW_DELTA)
			yaw2 = normaliseAngle(myYaw - CreatureData.MAX_YAW_DELTA)
			diff1 = angleDist(idealYaw, yaw1)
			diff2 = angleDist(idealYaw, yaw2)

			if diff1 < diff2:
				newYaw = yaw1
			else:
				newYaw = yaw2

			zd = math.cos(newYaw) * CreatureData.FLEE_TURN_DISTANCE
			xd = math.sin(newYaw) * CreatureData.FLEE_TURN_DISTANCE

		try:
			pos = BigWorld.findRandomNeighbourPoint(self.spaceID,
					(self.position[0] + xd, 0, self.position[2] + zd),
					CreatureData.FLEE_RANGE / 6)
			if distance( pos, enemyPos ) < distance( self.position, enemyPos ):
				# Don't try and move closer...
				self.doWait( 0.1 )
				return
		except ValueError, e:
			# Nowhere to run...
			self.doWait( 0.1 )
			return

		self.moveTowardsPoint(pos, self.runVelocity())


	#------------------------------------------------------------------------
	# This method moves to a random point.
	#------------------------------------------------------------------------
	def doMove(self):
		self.cancelCurrent()

		try:
			newPosition = BigWorld.findRandomNeighbourPoint(self.spaceID,
															(self.xorigin, self.position[1], self.zorigin),
															self.moveRange )
		except ValueError, e:
			try:
				newPosition = BigWorld.findRandomNeighbourPoint(self.spaceID,
																self.position,
																self.moveRange )
			except ValueError, e:
				self.doWait( 2.0 )
				return

		velocity = self.randomVelocity()
		self.moveTowardsPoint(newPosition, velocity)


	#------------------------------------------------------------------------
	# This method chases somebody.
	#------------------------------------------------------------------------
	def doChase(self, target):
		self.cancelCurrent()

		d = distance(target.position, self.position)
		self.facePosition(target.position)

		if (d > CreatureData.CHASE_STOP_RANGE):
			try:
				pos = BigWorld.findRandomNeighbourPoint( self.spaceID, target.position, CreatureData.CHASE_STOP_RANGE )

				self.moveTowardsPoint(pos, self.runVelocity())
			except ValueError, e:
				self.doWait( 0.1 )



	#------------------------------------------------------------------------
	# Wrapper around navigate.
	#------------------------------------------------------------------------
	def moveTowardsPoint(self, position, velocity):
		canMove = True
		try:
			self.controllerId = self.navigateStep(position, velocity, 5)
			if self.moving != 1:
				self.moving = 1
		except:
			canMove = False
			self.doWait(5)

		if canMove:
			if self.moveRange < MAX_RANGE:
				self.moveRange *= 2
		else:
			if self.moveRange > MIN_RANGE:
				self.moveRange *= 0.5


	#------------------------------------------------------------------------
	# This method waits for a period of time.
	#------------------------------------------------------------------------
	def doWait(self, seconds):
		self.cancelCurrent()
		self.controllerId = self.addTimer(seconds, 0, Creature.WAIT_TIMER)
		if self.moving != 0:
			self.moving = 0


	#-------------------------------------------------------------------------
	# This method faces towards a position.
	#-------------------------------------------------------------------------
	def facePosition(self, pos):
		vector = (pos[0] - self.position[0], 0, pos[2] - self.position[2])
		yaw = math.atan2(vector[0], vector[2])
		self.direction = (0, 0, yaw)


	#------------------------------------------------------------------------
	# This method is called when we've finished moving to a point.
	#------------------------------------------------------------------------
	def onMove(self, controllerId, userId):
		assert( 1 or controllerId or userId ) # Not used
		self.controllerId = 0
		self.think()


	def onTimer(self, timerId, userId):
		assert( 1 or timerId ) # Not used

		if userId == Creature.WAIT_TIMER:
			self.controllerId = 0
			self.think()
		if userId == Creature.DEATH_TIMER:
			self.destroy()
			return


	@bwdecorators.callableOnGhost
	def runVelocity(self):
		(minVelocity, maxVelocity) = CreatureData.runSpeed[self.creatureType]
		return maxVelocity


	@bwdecorators.callableOnGhost
	def randomVelocity(self):
		try:
			(minVelocity, maxVelocity) = CreatureData.runSpeed[self.creatureType]
		except KeyError:
			(minVelocity, maxVelocity) = CreatureData.runSpeed[CreatureData.UNKNOWN]

		return random.uniform( minVelocity, maxVelocity )

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
			self.ownerId = 0

		self.think()


	@bwdecorators.callableOnGhost
	def isDead( self ):
		return self.creatureState == CreatureData.DEAD or \
		   self.creatureState == CreatureData.DEAD_GIBBED


	def onNoise( self, entity, propRange, distance, event, info):
		if not self.enemyList.count(entity.id):
			self.enemyList.append(entity.id)
			self.think()


# Creature.py
