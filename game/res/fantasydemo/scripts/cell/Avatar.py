"This module implements the Avatar entity."

import BigWorld
import CustomErrors
import math
import struct
# from Math import *
from Math import Vector3
import CombatLogic
import Merchant
import ItemBase
import AvatarMode as Mode
import random
from bwdebug import DEBUG_MSG

import bwdecorators
import ThrottledMethods

from twisted.internet import defer

# ------------------------------------------------------------------------------
# Section: class Avatar
# ------------------------------------------------------------------------------

class Avatar( BigWorld.Entity ):
	"An Avatar entity."

	combativeModes = (Mode.NONE, Mode.CROUCH, Mode.SNEAK, Mode.ALERT_SCAN)
	usingItemModes = (Mode.USING_ITEM, Mode.USING_ITEM_CROUCHED)
	crouchModes = (Mode.CROUCH, Mode.USING_ITEM_CROUCHED, Mode.THROW_CROUCHED, Mode.CATCH_CROUCHED)
	takeDownableModes = (Mode.NONE, Mode.CROUCH, Mode.SNEAK)

	STANCE_NEUTRAL = -1
	STANCE_BACKWARD = 0
	STANCE_FORWARD = 1
	STANCE_LEFT = 2
	STANCE_RIGHT = 3

	CL_HIT = 0
	CL_DESPERATE = 1
	CL_PARRY = 2
	CL_MISS = 3

	COD_SHOT = 0
	COD_SLAIN = 1
	COD_TAKEN_DOWN = 2
	COD_FELL = 3

	CAMERAMODE_NO_GUN = 1
	CAMERAMODE_WITH_GUN = 2

	CC_TIMER = 111
	LOADGEN_TIMER = 112
	CELL_BOUNDS_CAPTURE_TIMER = 113
	ENTITY_INFO_CAPTURE_TIMER = 114

	DELAYED_DAMAGE_TIMER = 120
	LAST_TIMER = 256

	CC_SWING = 1.5
	CC_ENGAGE = 2.0

	loadGenLevel = 0
	loadGenLength = 8
	loadGenPeriod = 1

	def __init__( self, nearbyEntity ):
		BigWorld.Entity.__init__( self )

		if nearbyEntity:
			# Move to the TeleportPoint
			self.position = nearbyEntity.position

		self.updateHealth()
		self.canBeSeen = 1

		if Avatar.loadGenLevel > 0:
			self.startLoadGeneration()

		DEBUG_MSG( "%s: id(%s) InitialPosition: %s" %
			( self.__class__.__name__, self.id, self.position ) )

	def setPlayerName( self, playerID, name ):
		self.playerName = name


	def onDestroy( self ):
		if self.vehicle != None and hasattr( self.vehicle, 'onPassengerDeath' ):
			self.vehicle.onPassengerDeath( self.id )

		# Clean up any mode's state
		if self.mode != Mode.NONE:
			self.exitModeInternally_m()
			self.mode = Mode.NONE


	# This method is called by the client to chat with all nearby avatars.
	def chat( self, source, msg ):
		print "playerName is", self.playerName
		print 'Got message "' + msg + '"'

		self.otherClients.chat( msg )

	def sayToMe( self, who, msg ):
		self.clientEntity( who ).chat( msg )


	def resyncServTime( self, source, spaceID ):
		todData = BigWorld.getSpaceDataFirstForKey( spaceID, 0 )
		timeOfDayInSeconds, gameSecondsPerSecond = struct.unpack("ff", todData)
		BigWorld.setSpaceTimeOfDay( spaceID, timeOfDayInSeconds, gameSecondsPerSecond )


	# This method is a dodge way to get time sync from client to server
	def syncServTime( self, source, spaceID,
			timeOfDayInSeconds, gameSecondsPerSecond ):

		BigWorld.setSpaceTimeOfDay( spaceID,
				timeOfDayInSeconds - BigWorld.time() * gameSecondsPerSecond,
				gameSecondsPerSecond )

		print 'client gameTime is', timeOfDayInSeconds
		print 'server gameTime is', BigWorld.timeOfDay( spaceID )


	def syncServWeather( self, source, spaceID, weather ):
		print "syncServWeather", spaceID, weather
		SPACE_DATA_WEATHER = 8192
		BigWorld.setSpaceData( spaceID, SPACE_DATA_WEATHER, weather )


	# This method is called when another entity is talking directly to us.
	def directedChat( self, source, msg ):
		self.clientEntity( source ).chat( msg )

	# Client method to enter an action mode
	def enterMode( self, source, mode, modeTarget, modeIntParam ):
		if self.mode != Mode.NONE:
			print self.id, ": enterMode: Already in mode ", self.mode
			# TODO: tell us
			return

		# checks on modeInt per mode
		ok = mode in (	Mode.SHONK,		Mode.HANDSHAKE,
						Mode.PULLUP,		Mode.PUSHUP,
						Mode.USING_ITEM,	Mode.CROUCH,
						Mode.SEATED )


		if not ok:
			print self.id, ": enterMode: Invalid mode ", mode
			return

		# If the target is already in this mode then we do... nothing.
		# We could arbitrate who should be the initiator here, but it's
		# much better for the clients to figure it out amongst themselves,
		# mainly so they can deal with the animation issues neatly :)

		self.modeIntParam = modeIntParam
		self.modeTarget = modeTarget
		self.mode = mode


	def _getModeTarget( self ):
		try:
			return BigWorld.entities[ self.modeTarget ]
		except KeyError:
			errorMsg = 'Avatar._getModeTarget: unknown target entity (id=%d)'
			print errorMsg % self.modeTarget
			raise


	# Private method to get out of any internal state
	# associated with the current mode
	def exitModeInternally_m( self ):
		if self.mode == Mode.SEATED:
			if self.modeTarget in BigWorld.entities.keys():
				BigWorld.entities[self.modeTarget].ownerNotSeated()
		elif self.mode == Mode.COMBAT_CLOSE:
			self.ccCancelTimer()


	# Client method to cancel an action mode
	def cancelMode( self, source ):
		if self.mode == Mode.NONE:
			print self.id, ": cancelMode: Not in any mode"
			# TODO: tell us
			return

		if self.mode == Mode.DEAD:
			# can't cancel death! :)
			return

		if self.mode == Mode.COMBAT_CLOSE and self.health == 0:
			# can't cancel dazed either
			# possible contingency on another entity's timer going
			# off ... we need to make sure this is OK
			return

		self.exitModeInternally_m()

		self.mode = Mode.NONE


	# Client method to respond to one of our modes
	def answerMode( self, source, mode, sourceID, responseParam ):
		print 'answerMode'
		if self.mode == Mode.NONE or self.mode != mode:
			print self.id, ": answerMode from ", sourceID, "failed."
			# TODO: tell responder
			return

		if self.modeTarget != sourceID:
			print self.id, ": answerMode: Waiting for ", \
				self.modeTarget, " not ", sourceID
			# TODO: tell responder
			return

		if mode == Mode.SHONK:
			self.shonkReply_m( sourceID, responseParam )
		elif mode == Mode.HANDSHAKE:
			self.handshakeReply_m( sourceID )
		elif mode == Mode.PULLUP:
			self.pullUpReply_m( sourceID )
		elif mode == Mode.PUSHUP:
			self.pushUpReply_m( sourceID )


	# Private method to decide a shonk result
	def shonkReply_m( self, targetID, targetChoice ):
		self.allClients.shonk( targetID, targetChoice, self.modeIntParam )
		self.mode = Mode.NONE

	# Private method to decide a handshake result
	def handshakeReply_m( self, targetID ):
		print 'handshakeReply_m'
		self.allClients.handshake( targetID )
		self.mode = Mode.NONE

	# Private method to decide a pull up result
	def pullUpReply_m( self, targetID ):
		self.allClients.pullUp( targetID )
		self.mode = Mode.NONE

	# Private method to decide a push up result
	def pushUpReply_m( self, targetID ):
		self.allClients.pushUp( targetID )
		self.mode = Mode.NONE

	# Client method to enter combat mode
	def enterCombat( self, source ):
		# source is not used, but is declared because the method is <Exposed/> in the def file.
		if self.mode != Mode.NONE:
			print self.id, ": enterCombat: Already in mode ", self.mode
			return
		self.mode = Mode.COMBAT_UNLOCKED

	# Client method to leave combat mode
	def leaveCombat( self, source ):
		# source is not used, but is declared because the method is <Exposed/> in the def file.
		if self.mode != Mode.COMBAT_UNLOCKED:
			print self.id, ": leaveCombat: Not in combat mode"
			return
		self.mode = Mode.NONE

	# Client method to assail an opponent
	def assail( self, source, targetID ):

		# Ensure we're not in another mode (e.g. dead)
		if self.mode != Mode.NONE:
			print self.id, ": assail: Already in mode ", self.mode
			# TODO: tell ownClient
			return
		if targetID == 0:
			self.allClients.assail()
			return
		# See if we're close enough to hit the target
		t = BigWorld.entities[targetID]
		if t == None:
			closeEnough = 0
		else:
			diff = Vector3(self.position)-Vector3(t.position)
			closeEnough = diff.length < Avatar.CC_ENGAGE

			# See if they are (recently were) in close combat against us
			try:
				inCCAtAll = (t.mode == Mode.COMBAT_CLOSE)
				# because it returns a value, this must be a ghost method
				inCCWithUs = t.isInCloseCombat( self.id )
			except:
				# this entity can't be assailed
				inCCWithUs = 0
				inCCAtAll = 0
				closeEnough = 0

			# If so that's good enough for us (hopefully they'll be seeking
			#  to the right position if they're not close enough now)
			if inCCWithUs: closeEnough = 1
			# But if they're in CC mode with someone else, our assail
			#  always fails, even if we are close enough
			elif inCCAtAll: closeEnough = 0


		# React to this decision
		if closeEnough:
			print "Succeeded assail for", self.id
			self.stance = -1
			self.modeIntParam = -1
			self.modeTarget = targetID
			self.mode = Mode.COMBAT_CLOSE

			self.ccOwnMove = -1
			self.ccOthMove = -1
			self.ccDefence = 100

			# If they don't already have a timer on us...
			if not inCCWithUs:
				# We'll be in charge then
				self.ccInCharge = 1

				# Combat starts in 1s from now. Note: It's important that it
				# waits the 1s before making its first decision so the
				# closeCombatNotify can do its stuff.
				self.ccTimerId = self.addTimer( 1, 0, Avatar.CC_TIMER )

				# And if they have a lesser ID than us then tell them to
				# cancel their timer if they started close combat against us
				# before they got the propagation of the change in our mode.
				# (This could only happen if they were on a different cell)
				try:
					t.closeCombatNotify( self.id )
				except:
					pass
			else:
				# They're already in charge
				self.ccInCharge = 0
				self.ccTimerId = 0
		else:
			# Tell others about the swing anyway, and
			#  tell ourselves we can change items again.
			print "Failed assail for", self.id
			self.allClients.assail()

		# This combination of properties and messages is optimised
		# for the current system, but it would be much better if
		# we could get a message to 'mask' a property change
		# e.g. if you deliver the assail method call, don't bother
		# with the modeTarget and mode settings. (assail would need
		# to take the targetID (0 for unsuccessful) as a parameter)

	# Cell method to resolve a concurrency issue
	def closeCombatNotify( self, assailant ):
		# See if control is being passed back to us
		if assailant == 0:
			self.ccInCharge = 1
			self.ccTimerId = 0
			# We don't allow anyone to attack us 'tho
			self.modeTarget = Mode.NO_TARGET
		# OK, we want to make sure that there aren't too many cooks then
		else:
			# If we're in close combat against the input ID already,
			# and we're running the show (we'd only have just started),
			# AND we have a lower ID than our assailant, then cancel it,
			# because the other entity is taking charge of this combat.
			if self.isInCloseCombat( assailant ):
				if self.id < assailant and self.ccInCharge:
					self.ccCancelTimer()
					self.ccInCharge = 0

	# Private method to cancel our close combat timer if set
	def ccCancelTimer( self ):
		if self.ccTimerId != 0:
			self.cancel( self.ccTimerId )
			self.ccTimerId = 0

	# Ghost method to determine whether we're already fighting other
	@bwdecorators.callableOnGhost
	def isInCloseCombat( self, other ):
		return self.mode == Mode.COMBAT_CLOSE and \
			self.modeTarget == other

	# Client method to set their stance
	def setStance( self, source, stance ):
		if self.mode != Mode.COMBAT_CLOSE: return

		if stance < 100:
			self.stance = stance
		else:
			# we want to make an attack...

			# get the other entity, and make sure we are their partner
			oe = BigWorld.entities[ self.modeTarget ]
			good = 0
			try:
				if oe.isInCloseCombat( self.id ): good = 1
			except:
				pass
			if not good: return

			# OK, let the entity that's calling the shots know about it then
			if not self.ccInCharge:
				try:
					oe.closeCombatSwing(0)
				except:
					pass
			else:
				self.closeCombatSwing(1)

	# Cell method to do a close combat swing
	def closeCombatSwing( self, ownSwing ):
		if self.mode != Mode.COMBAT_CLOSE: return
		# Make sure we're running the show. Eventually this will not be
		# able to happen, but for now it's an ignored error to get here
		if not self.ccInCharge: return

		# Set the appropriate variable
		if ownSwing:
			self.ccOwnMove = 0
		else:
			self.ccOthMove = 0

		# If we're not waiting on a timer then call the step
		#  function directly, otherwise wait for the timer.
		if self.ccTimerId == 0:
			self.closeCombatStep()
		# Unless a finishing move is being waited for,
		# and the entity making the swing isn't the dead one
		elif self.modeIntParam - 2 == (not ownSwing):
			self.closeCombatFinishingMove()

	# Private method called to decide a combat result
	def closeCombatStep( self ):
		# First clear the timer id since it's done its thing (one-shot timers)
		self.ccTimerId = 0

		# We need two to tango
		oe = BigWorld.entities[ self.modeTarget ]
		good = 0
		try:
			if oe.isInCloseCombat( self.id ):
				good = 1
				# first swing can only occur when entities are in position
				if self.modeIntParam == -1:
					dis = (Vector3(self.position)-Vector3(oe.position)).length
					rot = (self.yaw - oe.yaw) % (math.pi*2.0)
					if  dis < Avatar.CC_SWING-0.3 or rot < math.pi - 0.2 or\
						dis > Avatar.CC_SWING+0.3 or rot > math.pi + 0.2:
							good = 0
					else:
						self.modeIntParam = 0
		except:
			pass
		if not good: return

		# OK, we are good to go.

		# See if either of the combatants is dazed
		if self.health == 0 or oe.health == 0:
			self.closeCombatDazedStep( oe )
			return

		# See who has priority for this one
		ownPriority = self.modeIntParam

		# Check who's swinging (could be simplified, but this makes sense)
		ownSwing = -1
		if ownPriority:
			if self.ccOwnMove >= 0:
				ownSwing = 1
			elif self.ccOthMove >= 0:
				ownSwing = 0
		else:
			if self.ccOthMove >= 0:
				ownSwing = 0
			elif self.ccOwnMove >= 0:
				ownSwing = 1

		# If no-one's swinging then do nothing (timer went off harmlessly)
		#  (might want to start the fight with an empty msg if we were called
		#  due to the initial timer going off... but can't guarantee that
		#  yet as timer might have been absorbed in the 'need two to tango' bit)
		if ownSwing == -1: return

		# Get the move they want to do, and clear the variable
		if ownSwing:
			theMove = self.ccOwnMove
			self.ccOwnMove = -1
		else:
			theMove = self.ccOthMove
			self.ccOthMove = -1

		# Get the combat logic to calculate the result
		res = CombatLogic.swing(
			(oe,self)[ownSwing], (self,oe)[ownSwing], theMove )

		# Send the result to all the clients
		self.allClients.salida( (ownSwing << 6) | res )

		# If the combat result was a break, that entity is done
		if res == (1<<5) | 1:
			broken = [oe,self][ownSwing]
			broken.cancelMode( self.id )
			# If it was us, don't try to set the timer!
			if ownSwing:
				# And let them know they're in charge now
				oe.closeCombatNotify( 0 )
				# (This should actually also be done whenever we leave
				# this mode, in fact exitModeInt is prolly a better place
				# to put it - we definitiely want to get it when we die.
				# But for January (2002 :) it shall remain here)
				return
			# Otherwise don't allow them (or anyone) to re-engage us
			self.modeTarget = Mode.NO_TARGET

		# Whoever defended this time gets priority next time
		self.modeIntParam = not ownSwing

		# Set a timer to call us back when that animation would be finished
		atime = CombatLogic.resultAnimTimes[ res ]
		self.ccTimerId = self.addTimer( atime, 0, Avatar.CC_TIMER )


	# Private method to do a close combat step when one opponent is dazed
	def closeCombatDazedStep( self, oe ):
		# If we've not been here before, come back in 3 seconds
		if self.modeIntParam not in [2,3]:
			self.ccTimerId = self.addTimer( 3, 0, Avatar.CC_TIMER )
			self.modeIntParam = [2,3][ self.health == 0 ]
			# The move buffer is cleared at this point,
			# because you cannot queue a finishing move
			self.ccOwnMove = -1
			self.ccOthMove = -1
			return

		# If the timer set above went off, the finishing chance was missed,
		# otherwise we've been called directly from closeCombatFinishingMove
		# and the finishing move has just been sent
		ded = [oe,self][ self.modeIntParam - 2 ]
		liv = [self,oe][ self.modeIntParam - 2 ]

		# Let the victim know it's OK to die from close combat mode
		ded.deductHealth( 0, liv )

		# Reset this in case combat is restarted
		self.modeIntParam = -1


	# Private method called to choose a close combat finishing move
	def closeCombatFinishingMove( self ):
		# Find out who's dying and who's dealing
		ownDeath = self.modeIntParam - 2
		ownSwing = not ownDeath

		# Send the move to all the clients
		self.allClients.salida( (ownSwing << 6) | (1<<5) )

		# Now cancel the timer
		self.ccCancelTimer()

		# And call the step function as if the timer we just cancelled
		# had expired in order to change the mode of the dead entity
		# to be dead (so we don't repeat the two to tango bit here)
		self.closeCombatStep()



	# Private method that used to do the close combat step
	def old_closeCombatStep( self ):
		print "Combat timer went off for", self.id

		# Look at stance and BigWorld[modeTarget].stance...
		ownS = self.stance
		try:
			othE = BigWorld.entities[ self.modeTarget ]
			if othE.isInCloseCombat( self.id ):
				othS = othE.stance
			else:
				othS = -1
		except:
			othE = None
			othS = -1
		ownTurn = self.modeIntParam
		if ownS == -1 and othS == -1:
			self.modeIntParam = not ownTurn

		# Tell everyone the result
		res = ((ownS + 1) << 4) | (ownTurn << 3) | (othS + 1)
		self.allClients.salida( res )

		# Change the health as necessary
		if othE != None:
			self.old_closeHit( ownS, othS, ownTurn, othE.id )
			othE.old_closeHit( othS, ownS, not ownTurn, self.id )


	# Server method to take damage from a close combat hit
	def closeHit( self, damage, whoid ):
		self.deductHealth( damage, None ) #BigWorld.entities[whoid] )
		# the entity is not specified so that we go into dazed mode


	# Matrix of close combat damage
			# them:  neut   back    frwd	 us:
	CC_DAMAGE = (	((1,0),	0,		2),		# neut
					(0.5,	0,		0),		# back
					(0.5,	1,		2) )	# frwd

	def old_closeHit( self, ownStance, othStance, ownTurn, whoid ):
		damage = Avatar.CC_DAMAGE[ ownStance + 1 ][ othStance + 1]
		if type(damage) == type((0,0)): damage = damage[ownTurn]
		damage *= 5
		self.deductHealth( damage, BigWorld.entities[whoid] )

	def reduceDefence( self, amount ):
		d = self.ccDefence - amount
		if d < 0: d = 0
		self.ccDefence = amount

	# Client method to let us know it has changed it's colour index
	def setCustomColour( self, source, colourIndex ):
		self.customColour = colourIndex

	# Client method to let us know it's gesticulated
	def didGesture( self, source, gestureNumber ):
		self.otherClients.didGesture( gestureNumber )

	# Client method to let us know it's changed the item in its hand
	def setRightHand( self, sourceID, itemType ):
		print 'setRightHand', self.id, sourceID, itemType
		# only player itself or system can change item
		if sourceID != self.id and sourceID != 0: return
		self.rightHand = itemType # will propagate to all otherClients

	# Client method to let us know it's changed the item in its shoulder
	def setShoulder( self, source, itemType ):
		self.shoulder = itemType

	# Client method to let us know it's changed the item in its right hip
	def setRightHip( self, source, itemType ):
		self.rightHip = itemType

	# Client method to let us know it's changed the item in its left hip
	def setLeftHip( self, source, itemType ):
		self.leftHip = itemType

	# Client method to let us know it's eating
	def eat( self, source, itemType ):
		# This is naughty, but until we have a proper Item class on the
		# server, we'll give the Avatar the power to determine what effects
		# eating has on itself.
		self.health = self.health + 20
		if self.health > self.maxHealth:
			self.health = self.maxHealth
		self.updateHealth()

		self.otherClients.eat( itemType )


	# Client method to let us know it shot its weapon
	def fireWeapon( self, source, who, accuracy = 0.5 ):
		# TO DO: check if this is allowed. do a LoS check and
		# also make sure it doesn't happen more than once per second
		if self.rightHand == 7: # SWORD
			#TODO: Remove this gross hack for guard support
			self.otherClients.assail()
		else:
			self.otherClients.fireWeapon( who, self.quantiseAccuracy( accuracy ) )

		if who:
			victim = BigWorld.entities[ who ]
			if victim != None:
				damage = self.getDamage() * accuracy
				victim.rangedHit( self.id, damage )


	# Exposed method to let us know the client cast a spell
	# timeToHit gives us information about how long it will
	# take from the spell cast to when the spell 'hits' the
	# target; we wait the appropriate length of time and then
	# subtract health from the target.
	# TODO : better synchronisation than this.
	def castSpell( self, source, targetID, hitLocation, materialKind, timeToHit, explodeRadius ):
		# TO DO: check if this is allowed. do a LoS check and
		# also make sure it doesn't happen more than once per second

		# Check if there is a geometry collision between our cast position, and the
		# hitLocation calculated on the client. Draw the collision position back slightly
		# and use this as our hitLocation, and the centre of the explosion.
		# Note: This check is required due to slight variations between client and server geometry.
		if not targetID:
			castPos = Vector3( self.position )
			castPos[1] += 2
			collideResultToken = BigWorld.collide( self.spaceID, castPos.tuple(), hitLocation.tuple() )
			if collideResultToken != None:
				hitLocation = collideResultToken[0]
				# Scale the hitLocation back slightly
				vectToCollidePos = (hitLocation - castPos)
				len = vectToCollidePos.length
				if len > 0.1:
					vectToCollidePos.normalise()
					vectToCollidePos *= len-0.1
				hitLocation = castPos + vectToCollidePos

		if self.rightHand in [2,3]: # BOTH STAFFs
			self.otherClients.castSpell( targetID, hitLocation, materialKind )


		if targetID or (explodeRadius != -1):
			self.delayedDamageList.append( (targetID, BigWorld.time() + timeToHit, hitLocation, explodeRadius) )
			if not self.delayedDamageTimerID:
				self.delayedDamageTimerID =	self.addTimer( 0.2, 0.2, Avatar.DELAYED_DAMAGE_TIMER )


	#callback : process delayed damage for entities requiring it.
	def doDelayedDamage( self ):
		lagCompensation = 0.0
		now = BigWorld.time() + lagCompensation
		for targetID, time, hitLocation, explodeRadius in self.delayedDamageList:
			if now >= time:
				DEBUG_MSG("hitLocation: %s, time: %s, explodeRadius: %s" % (hitLocation, time, explodeRadius) )
				try:
					victim = BigWorld.entities[ targetID ]
				except KeyError:
					victim = None
				if victim != None and hasattr(victim, "rangedHit"):
					accuracy = 1.0
					damage = self.getDamage() * accuracy
					victim.rangedHit( self.id, damage )
				if explodeRadius != -1:
					self.doExplodeDamage( hitLocation, explodeRadius, victim )

		#filter out all old list entries
		self.delayedDamageList = filter( lambda (targetID, time, hitLocation, explodeRadius) : time > now, self.delayedDamageList )

		if len(self.delayedDamageList) == 0:
			self.cancel( self.delayedDamageTimerID )
			self.delayedDamageTimerID = 0


	def doExplodeDamage( self, explodePos, explodeRadius, directHitEntity ):
		"""
		Does splash damage to all entities in explodeRadius range of explodePos.
		The damage falls off linearly over explodeRadius distance from full damage to zero.
		The directHitEntity should have already recieved direct damage, so don't damage again.
		"""

		# If the projectile did a direct hit, move the source of the explosion up by 1 metre, so
		# we don't get insignificant ground collisions.
		if directHitEntity != None:
			explodePos[1] += 1

		entitiesInRange = self.entitiesInRange( explodeRadius, None, explodePos )
		for entity in entitiesInRange:
			# Check if the entity is occluded from the source of the explosion
			entityCollidePos = Vector3( entity.position )
			entityCollidePos[1] += 0.5	# Move half a metre up, so we don't get occlude by very small objects

			# Check if there was a collision.
			resultToken = BigWorld.collide( self.spaceID, explodePos.tuple(), entityCollidePos.tuple() )
			if resultToken != None:
				continue

			# Calculate damage falloff and deal damage
			if (entity != directHitEntity) and hasattr(entity, "rangedHit"):
				dist = explodePos.distTo( entity.position )
				damageFalloff = (explodeRadius - dist) / explodeRadius
				damage = self.getDamage() * damageFalloff
				entity.rangedHit( self.id, damage )


	# Private method to quantise accuracy
	def quantiseAccuracy( self, accuracy ):
		if accuracy < 0.15:
			return 0
		elif accuracy < 0.575:
			return 1
		else:
			return 2


	# Client method to let us know it's respawned and come back
	def reincarnate( self, source ):
		self.health = self.maxHealth
		self.mode = Mode.NONE
		self.updateHealth()
		self.volatileInfo = \
			(BigWorld.VOLATILE_ALWAYS, BigWorld.VOLATILE_ALWAYS, 20.0, None)


	# Private method, to handle dying.
	# Intended to be overridden in derived classes.
	def handleDeath(self):
		self.exitModeInternally_m()


	# Private method, to handle becoming dazed.
	# Intended to be overridden in derived classes.
	def handleDazed(self):
		pass


	# This method is intended to be overriden.
	# It inform the derived class that it has been hit.
	# A better solution would be for the derived class to
	# override the rangedHit method, and then call the base
	# class. But calling base class methods does not currently work.
	def handleHit(self, shooterID):
		pass

	# Returns the amount of damage we do
	@bwdecorators.callableOnGhost
	def getDamage(self):
		if self.rightHand == 0:		# gun
			return 10
		elif self.rightHand == 1:	# blaster
			return 25
		elif self.rightHand == 2:	# staff
			return 25
		elif self.rightHand == 3:	# lightning staff
			return 35
		elif self.rightHand == 8:	# crossbow
			return 10
		elif self.rightHand == 16:	# bulldog
			return 100
		else:
			return 0

	def updateHealth(self):
		if self.maxHealth == 0:
			nhp = 0
			print "Avatar %s has zero max health" % self.playerName
		else:
			nhp = int(100.0 * self.health / self.maxHealth)
		# If enemy has any health left then health percent doesn't
		# go to zero (this behaivour is relied on by the client)
		if nhp == 0 and self.health > 0: nhp = 1
		self.healthPercent = nhp

	# Cell method to let us know we got hit
	def rangedHit( self, shooterID, damage ):
		self.handleHit(shooterID)

		if damage < 1:
			return

		shooter = BigWorld.entities[ shooterID ]
		self.deductHealth( damage, shooter )

	# Private method to reduce our health (which might kill us)
	# If we're in close combat mode, and we would die, and the
	# dealer of the blow isn't specified, then we only get dazed
	def deductHealth( self, damage, who ):
		newHealth = self.health - damage
		if newHealth <= 0:
			# If we're in close combat mode we just get dazed
			if self.mode == Mode.COMBAT_CLOSE and not who:
				self.handleDazed()

				self.health = 0
				# Should consider doing this with a new mode, and
				# having isInCloseCombat return true for every
				# entity if we're in dazed mode. So, e.g. another
				# (different) avatar could go straight into cc mode
				# and finish this entity off. This idea prolly has
				# many other problems 'tho.
			# Otherwise we die immediately
			else:
				self.handleDeath()
				self.volatileInfo = (None, None, None, None)

				self.health = 0
				self.mode = Mode.DEAD
				self.allClients.fragged( who.id )
				who.gotFrag( self.id )
		else:
			self.health = int(newHealth)

		self.updateHealth()

	# Cell method to let us know we got a frag
	def gotFrag( self, victimID ):
		self.frags += 1

	def setPhoneNumber( self, phoneNumber ):
		self.phoneNumber = phoneNumber

	def sendSMS( self, message ):
		if len(self.phoneNumber):
			BigWorld.sendSMS(self.phoneNumber, message)
			self.chat( "Sending SMS to " + str( self.phoneNumber ) )
		else:
			self.chat( "I have no phone number" )
			print "Avatar %s has no phone number" % self.playerName

	@bwdecorators.callableOnGhost
	def isDead( self ):
		return self.mode == Mode.DEAD

	def onTimer( self, timerId, userId ):
		if userId == Avatar.CC_TIMER:
			self.closeCombatStep();
		elif userId == Avatar.LOADGEN_TIMER:
			self.doLoadGeneration()
		elif userId == Avatar.CELL_BOUNDS_CAPTURE_TIMER:
			self.captureCellBounds()
		elif userId == Avatar.ENTITY_INFO_CAPTURE_TIMER:
			self.captureEntityInfo()
		elif userId == Avatar.DELAYED_DAMAGE_TIMER:
			self.doDelayedDamage()

	# -------------------------------------------------------------------------
	# Friends list
	# -------------------------------------------------------------------------
	def getInfoForAdmirer( self, baseInfo, admirerBase ):
		info =  "[Health: " + str(self.healthPercent) + "%]"
		info += "[Frags: " + str(self.frags) + "]"
		info += "[Position: " + str(self.position) + "]"
		admirerBase.ownClient.onRcvFriendInfo( self.playerName, info + baseInfo )

	# -------------------------------------------------------------------------
	# Section: Items trading
	# -------------------------------------------------------------------------

	def tradeStartRequest( self, sourceID, partnerID ):
		'''Client is requesting to enter the trade mode. Decide
		into which mode to enter based on the partner current state.
		Params:
			sourceID				id of client entity making request (must be self.id)
			partnerID			id of target trade partner
		'''
		assert sourceID == self.id

		if self.mode != Mode.NONE:
			self.ownClient.tradeDeny()
			return

		try:
			partner = BigWorld.entities[ partnerID ]
		except KeyError:
			errorMsg = 'Avatar.tradeStartRequest: unknown partner (id=%d)'
			print errorMsg % partnerID
			self.ownClient.tradeDeny()
			return

		if partner.mode == Mode.TRADE_PASSIVE:
			if partner.modeTarget == self.id:
				self.modeTarget = partnerID
				self.mode = Mode.TRADE_ACTIVE
			else:
				self.ownClient.tradeDeny()
		else:
			self.modeTarget = partnerID
			self.mode = Mode.TRADE_PASSIVE


	def tradeCancelRequest( self, sourceID ):
		'''Client is requesting to exit the trade
		mode. Forces partner	to also exit trade mode.
		Params:
			sourceID				id of client entity making request (must be self.id)
		'''
		assert sourceID == self.id
		assert self._isInTradeMode()

		try:
			partner = self._getModeTarget()
			if partner._isInTradeMode() and partner.modeTarget == self.id:
				partner.tradeCancel()
		except KeyError:
			pass

		self.tradeCancel()


	def tradeCancel( self ):
		'''Cancels trade mode.
		'''
		self.tradeOutboundLock    = -1
		self.tradeSelfAccepted    = False
		self.tradePartnerAccepted = False
		self.modeTarget = Mode.NO_TARGET
		self.mode       = Mode.NONE


	def tradeOfferItemRequest( self, sourceID, lockHandle, itemSerial ):
		'''Client is offering an item to partner.
		Params:
			sourceID				id of client entity making request (must be self.id)
			lockHandle			handle of lock to offered item
			itemSerial			serial of item in inventory
		'''
		assert sourceID == self.id
		assert self._isInTradeMode()
		assert self.tradeOutboundLock == -1

		goldPieces = 0
		self.tradeOutboundLock = lockHandle
		self.base.itemsLockRequest( lockHandle, [itemSerial], goldPieces )


	def tradeOfferItem( self, itemType ):
		'''Partner is offering us an item.
		Param:
			itemType				type of item being offered
		'''
		self.tradeSelfAccepted = False
		self.ownClient.tradeOfferItemNotify( itemType )


	def tradeAcceptRequest( self, sourceID, accepted ):
		'''Client has accepted trade of currently offered items.
		Params:
			sourceID				id of client entity making request (must be self.id)
			accepted				True if entity is accepting item. False otherwise
		'''
		assert sourceID == self.id
		assert self._isInTradeMode()

		if accepted != self.tradeSelfAccepted:
			self.tradeSelfAccepted = accepted
			partner = self._getModeTarget()
			partner.tradeAcceptNotify( accepted )
			self._tryTradeBegin()


	def tradeAcceptNotify( self, accepted ):
		'''Partner wants to commit trade of currently offered items.
		Params:
			accepted				True if partner is accepting item. False otherwise
		'''
		assert self.tradeOutboundLock != -1
		self.ownClient.tradeAcceptNotify( accepted )
		self.tradePartnerAccepted = accepted
		self._tryTradeBegin()


	def tradeCommitPassive( self, activeBase ):
		'''Partner is telling us to commit the trade now.
		Params:
			activeBase			base of partner (he is the one in active mode)
		'''
		assert self.mode == Mode.TRADE_PASSIVE
		assert self.tradeOutboundLock != -1
		assert self.tradeSelfAccepted == True
		self.base.tradeCommitPassive( self.tradeOutboundLock, activeBase )


	def tradeCommitNotify( self, success, outItemsLock,
				outItemsSerials, outGoldPieces, inItemsTypes,
				inItemsSerials, inGoldPieces ):
		'''Base is notifying us that the trade has being commited.
		Params:
			success				True if commit was successful. False otherwise.
			outItemsLock		lock handle to items being traded out
			outItemsSerials	serials of items being traded out
			outGoldPieces		ammount of gold being traded out
			inItemsTypes		list of items being traded in
			inItemsSerials		serials of items being traded in
			inGoldPieces		ammount of gold being traded in
		'''
		if outItemsLock == self.tradeOutboundLock:
			assert self._isInTradeMode()
			self.tradeOutboundLock = -1
			self.tradeSelfAccepted    = False
			self.tradePartnerAccepted = False

		self.ownClient.tradeCommitNotify( success, outItemsLock,
				outItemsSerials, outGoldPieces, inItemsTypes,
				inItemsSerials, inGoldPieces )


	def _tradeOfferCancel( self ):
		'''Cancels current trade offer
		'''
		self.tradeOutboundLock = -1
		self.tradePartnerAccepted = False
		if self._isInTradeMode():
			try:
				partner = self._getModeTarget()
				if partner._isInTradeMode():
					partner.tradeOfferItem( ItemBase.ItemBase.NONE_TYPE )
			except KeyError:
				pass


	def _tryTradeBegin( self ):
		'''Test if both we and our trade partner have
		agreed on trading the items currently being offered
		by each party. If so, ask base to commit the trade.
		'''
		if self.mode == Mode.TRADE_ACTIVE and \
				self.tradePartnerAccepted and \
					self.tradeSelfAccepted:

			assert self.tradeOutboundLock != -1
			self.base.tradeCommitActive( self.tradeOutboundLock )
			partner = self._getModeTarget()
			partner.tradeCommitPassive( self.base )


	def _isInTradeMode( self ):
		'''Returns true if this entity is in TRADE_ACTIVE or TRADE_PASSIVE mode.
		'''
		return self.mode in (Mode.TRADE_ACTIVE, Mode.TRADE_PASSIVE)

	# -------------------------------------------------------------------------
	# Section: Items locking
	# -------------------------------------------------------------------------

	def itemsLockNotify( self, success, lockHandle, itemsSerials, itemsTypes, goldPieces ):
		'''Base is notifying us about items being locked.
		Params:
			success				True if lock was successful. False otherwise.
			lockHandle			handle of items just locked
			itemsSerials		serials of items just locked
			itemsTypes			list of items just locked
			goldPieces			ammount of gold pieves locked
		'''
		if lockHandle == self.tradeOutboundLock:
			if success:
				assert self._isInTradeMode()

				self.tradePartnerAccepted = False
				partner = self._getModeTarget()
				assert partner._isInTradeMode()
				assert partner.modeTarget == self.id
				partner.tradeOfferItem( itemsTypes[0] )
			else:
				self.tradeOutboundLock = -1
				self.ownClient.tradeOfferItemDeny( lockHandle )
		else:
			assert success
			self.ownClient.itemsLockNotify( lockHandle, itemsSerials, goldPieces )


	def itemsUnlockRequest( self, sourceID, lockHandle ):
		'''Client is requesting items to be unlocked.
		Params:
			sourceID				id of client entity making request (must be self.id)
			lockHandle			handle of items to be unlocked
		'''
		self.base.itemsUnlockRequest( lockHandle )


	def requestBoardVehicle( self, sourceVehicleID ):
		vehicle = BigWorld.entities[ sourceVehicleID ]
		self.boardVehicle( sourceVehicleID )
		vehicle.passengerBoarded( self.id )


	def requestAlightVehicle( self, sourceVehicleID ):
		vehicle = BigWorld.entities[ sourceVehicleID ]
		if self.vehicle != None:
			self.alightVehicle()
		vehicle.passengerAlighted( self.id )


	def itemsUnlockNotify( self, success, lockHandle ):
		'''Base is notifying us about items being unlocked.
		Params:
			success				True if unlock was successful. False otherwise.
			lockHandle			handle of items just unlocked
		'''
		if success and self._isInTradeMode() and \
				lockHandle == self.tradeOutboundLock:
			self._tradeOfferCancel()

		self.ownClient.itemsUnlockNotify( success, lockHandle )

	# -------------------------------------------------------------------------
	# Section: Items commerce
	# -------------------------------------------------------------------------

	def commerceStartRequest( self, sourceID, merchantID ):
		'''Client is requesting to enter the commerce mode.
		Forward request to Merchant.
		Params:
			sourceID				id of client entity making request (must be self.id)
			merchantID				id of target Merchant
		'''
		assert sourceID == self.id

		if self.mode != Mode.NONE:
			self.ownClient.commerceStartDeny()
			return

		try:
			merchant = BigWorld.entities[ merchantID ]
		except KeyError:
			self.ownClient.commerceStartDeny()
			errorMsg = 'Avatar.commerceStartRequest: unknown entity (id=%d)'
			print errorMsg % merchantID
			return

		if not isinstance( merchant, Merchant.Merchant ):
			self.ownClient.commerceStartDeny()
			errorMsg = 'Avatar.commerceStartRequest: entity not a Merchant: %d'
			print errorMsg % merchantID
			return

		if merchant.modeTarget == Mode.NO_TARGET:
			merchant.commerceStartRequest( self.base )
		else:
			self.ownClient.commerceStartDeny()


	def commerceStartResponse( self, success, merchantID ):
		'''Merchant is responding to our commerce start request.
		Params:
			success				True if he has accepted our request. False otherwise.
			merchantID			Id of the merchant responding to our request.
		'''
		if success:
			self.modeTarget = merchantID
			self.mode = Mode.COMMERCE
		else:
			self.ownClient.commerceStartDeny()


	def commerceCancelRequest( self, sourceID ):
		'''Client is requesting to exit the commerce. Forward request to partner.
		Params:
			sourceID				id of client entity making request (must be self.id)
		'''
		assert sourceID == self.id
		assert self.mode == Mode.COMMERCE

		merchant = self._getModeTarget()
		if merchant.modeTarget == self.id:
			merchant.commerceCancelRequest()

		self.mode = Mode.NONE


	def finaliseCommerceCancel( self, sourceID ):
		"""
		We need to know about our commerce modeTarget until our
		client Avatar has finished with it.
		"""
		assert sourceID == self.id
		self.modeTarget = Mode.NO_TARGET


	def commerceBuyRequest( self, sourceID, lockHandle, itemIndex ):
		'''Client is requesting to buy an item.
		Params:
			sourceID				id of client entity making request (must be self.id)
			lockHandle			handle to buyer's locked gold pieces
			itemIndex			index (in seller's inventory) of item to be bought
		'''
		assert sourceID == self.id
		assert self.mode == Mode.COMMERCE

		merchant = self._getModeTarget()
		assert merchant.modeTarget == self.id

		merchant.base.commerceSellRequest( lockHandle, itemIndex, self.base )


	def commerceSellRequest( self, sourceID, lockHandle, itemSerial ):
		'''Client is requesting to sell an item.
		Params:
			sourceID				id of client entity making request (must be self.id)
			lockHandle			handle to the avatar's locked item
			itemSerial			serial of item (in avatar's inventory) to be sold
		'''
		assert sourceID == self.id
		assert self.mode == Mode.COMMERCE

		merchant = self._getModeTarget()
		assert merchant.modeTarget == self.id

		self.base.commerceSellRequest( lockHandle, itemSerial, merchant.base )

	# -------------------------------------------------------------------------
	# Section: Items pick-up and drop
	# -------------------------------------------------------------------------

	def pickUpRequest( self, sourceID, droppedItemID ):
		'''Client is requesting to picked up an item.
		Params:
			sourceID				id of client entity making request (must be self.id)
			droppedItemID		id of item entity to picked up
		'''
		assert sourceID == self.id

		try:
			item = BigWorld.entities[ droppedItemID ]
			item.pickUpRequest( self.id )
		except KeyError:
			errorMsg = 'Pickup request for unknown dropped item: (id=%d)'
			print errorMsg % droppedItemID


	def pickUpResponse( self, success, droppedItemID, itemType, itemSerial ):
		'''Base is notifying us about an item being picked up.
		Params:
			success				True if pickup request was granted. False otherwise
			droppedItemID		id of item entity being picked up
			itemType				type of items being picked up
			itemSerial			serial to be assigned to item inside inventory
		'''
		if success:
			# success: notify all clients this entity base
			self.ownClient.pickUpResponse( True, droppedItemID, itemSerial )
			self.otherClients.pickUpNotify( droppedItemID )
			self.rightHand = itemType
		else:
			# failed: notify requesting client only
			self.ownClient.pickUpResponse( False, droppedItemID, 0 )


	def dropNotify( self, itemSerial, itemType ):
		'''Base is notifing us that an item is being dropped by this avatar.
		Params:
			itemType				type of item being dropped
		'''
		# compute drop position
		vPos = Vector3( self.position )
		vDir = Vector3( self.direction )

		cosPitch = math.cos( vDir.y )
		vDelta = Vector3( cosPitch * math.sin( vDir.z ), 0,
				cosPitch * math.cos( vDir.z ) )

		handDist = 0.45
		vDelta = vDelta.scale( handDist )

		# create DroppedItem
		args = {
			"itemSerial"		: itemSerial,
			"classType"			: itemType,
			"dropperID"			: self.id }

		droppedItem = BigWorld.createEntity( "DroppedItem",
						self.spaceID, (vPos + vDelta).tuple(),
						vDir.tuple(), args )
		if self.vehicle:
			droppedItem.boardVehicle( self.vehicle.id )

		self.rightHand = ItemBase.ItemBase.NONE_TYPE


	# -------------------------------------------------------------------------
	# Section: Load Generation for stress testing
	# -------------------------------------------------------------------------

	def startLoadGeneration( self ):#, level ):
		#self.loadGenLevel = level
		if not self.loadGenTimer:
			self.loadGenTimer = self.addTimer(
				random.randrange(1,10)*0.1, 0.1, Avatar.LOADGEN_TIMER );

	def doLoadGeneration( self ):
		level = Avatar.loadGenLevel
		if level <= 0 :
			self.cancel( self.loadGenTimer )
			self.loadGenTimer = 0

		if ((int(BigWorld.time() * 10.0) + self.id) % Avatar.loadGenPeriod) != 0:
			return

		if level > 0:
			self.allClients.loadGenMeth1( "w"*Avatar.loadGenLength )
		if level > 1:
			self.allClients.loadGenMeth2( BigWorld.time(), "flibbertigibbit" )
		if level > 2:
			self.allClients.loadGenMeth3( self.position.x, self.position.y,
				self.position.z )
		if level > 3:
			self.allClients.loadGenMeth4( [3,129,5,74]*random.randrange(1,8) )

	def getPlayerInfo( self ):
		"""
		A method from the base requesting information about the player.
		"""
		return (self.playerName, self.position,	self.direction,
			self.health, self.maxHealth, self.frags)

	def takeDamage( self, damage ):

		if (damage < 0):
			return defer.fail( CustomErrors.InvalidDamageAmountError(
						"Avatar can not take negative damage" ) )

		self.health = self.health - damage

		if (self.health < 0):
			self.health = 0

		return (self.health, self.maxHealth)

	def summonEntity( self, sourceID, typeName, properties ):
		assert sourceID == self.id
		self.base.summonEntity( typeName,
			self.position,
			self.direction,
			self.spaceID,
			properties )

	def enableCellBoundsCapture( self, sourceID, enabled ):
		if self.cellBoundsCaptureTimerHandle != 0:
			self.cancel( self.cellBoundsCaptureTimerHandle )
			self.cellBoundsCaptureTimerHandle = 0

		self.cellBounds = []

		if enabled:
			self.cellBoundsCaptureTimerHandle = \
					self.addTimer( 1.0, 1.0, Avatar.CELL_BOUNDS_CAPTURE_TIMER )


	def enableEntityInfoCapture( self, sourceID, enabled ):

		if self.entityInfoCaptureTimerHandle != 0:
			self.cancel( self.entityInfoCaptureTimerHandle )
			self.entityInfoCaptureTimerHandle = 0

		if enabled:
			self.entityInfoCaptureTimerHandle = \
					self.addTimer( 1.0, 1.0, Avatar.ENTITY_INFO_CAPTURE_TIMER )


	def captureCellBounds( self ):
		cellBounds = []
		watcherString = "spaces/%d/cellInfos" % (self.spaceID,)
		dirs = BigWorld.getWatcherDir( watcherString )
		for ( childType, label, value ) in dirs:
			if childType is 3:
				rect = BigWorld.getWatcher( watcherString + "/" + label + "/rect" )
				for i in rect.split(', '):
					cellBounds.append(
						float( i.replace( 'FLT_MAX', '3.4028234663852886e+38' ) ) )
		self.cellBounds = cellBounds
		self.cellAppID = int(BigWorld.getWatcher( "id" ))
		#print self.cellBounds


	def captureEntityInfo( self ):
		reals = filter( lambda x : x.isReal(), BigWorld.entities.values() )
		self.entityInfo = len(reals)


	def setAvatarModel( self, avatarModel ):
		self.avatarModel = avatarModel


	def onTeleportSuccess( self, nearbyEntity ):
		if nearbyEntity and self.position == BigWorld.INVALID_POSITION:
			self.position = nearbyEntity.position


	@ThrottledMethods.hardThresholdCell( 2.0, 0.5 )
	def testThrottlingOwnClient( self, callerID ):
		print "testThrottlingOwnClient() called!\n"


	@ThrottledMethods.hardThresholdCellAllClients( 2.0, 0.5 )
	def testThrottlingAllClients( self, callerID ):
		print "testThrottlingCellAllClients() called!\n"


# Module method designed to be called by runscript
def startLoadGenerationOnAll( level, length, period ):
	Avatar.loadGenLevel = level
	Avatar.loadGenLength = length
	Avatar.loadGenPeriod = int( period * 10 )
	if level > 0:
		for e in BigWorld.entities.values():
			if e.__class__ == Avatar:
				e.startLoadGeneration()

# Avatar.py
