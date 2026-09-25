import BigWorld
import FantasyDemo
import random
from functools import partial
from Keys import *
from Math import *
from Helpers import Caps
from Helpers.CallbackHelpers import *
from GameData import CreatureData
from FDGUI import Minimap
import FX
import math

# ------------------------------------------------------------------------------
# Class Creature:
#
# Creature is the type of entity that covers animate objects with animal-like
# intelligence or behaviour.
# ------------------------------------------------------------------------------
class Creature( BigWorld.Entity ):

	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Defines all variables used by the creature entity. This includes
	#	  setting variables to None.
	#	- Does not call any of the accessor methods. Any variables set are
	#	  for the purposes of stability.
	#	- Checks built-in properties set by the client.
	#	- Builds the list binding actionIDs to actions.
	# --------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.targetCaps = []
		self.filter = BigWorld.AvatarDropFilter()
		self.model = None
		self.doingSoundCallback = False
		self.targettingColour = (255,128,0,255)
		self.minimapColour = self.targettingColour
		self.checkProperties()
		self.buildActionBindings()


	# Returns true if we can set off a mine (by being near it)
	def canSetOffMine( self, mine ):
		return 1

	# --------------------------------------------------------------------------
	# Method: startSoundLoop
	# Description:
	#	- Sets up a callback on making random sounds for the creatures.
	# --------------------------------------------------------------------------
	def startSoundLoop( self ):
		if not self.inWorld or self.doingSoundCallback: return

		if self.creatureType in CreatureData.randomSounds.keys():
			randomSound = CreatureData.randomSounds[ self.creatureType ]
			if randomSound != None:
				( self.randomSound, minTime, maxTime ) = randomSound
				time = random.randint( minTime, maxTime )
				BigWorld.callback( time, partial(
					self.performEmitSoundAction, True ) )
				self.doingSoundCallback = 1


	# --------------------------------------------------------------------------
	# Method: checkProperties
	# Description:
	#	- Checks all properties defined in the XML file to see if they are
	#	  valid.
	# --------------------------------------------------------------------------
	def checkProperties( self ):
		methodName = "Creature.checkProperties: "

		#
		# Force creatureType to a legal value.
		#
		if not hasattr( self, "creatureType" ):
			self.creatureType = CreatureData.UNKNOWN
			print methodName + "creatureType not initialised."
		else:
			if not self.creatureType in CreatureData.displayNames.keys():
				self.creatureType = CreatureData.UNKNOWN
				print methodName + "creatureType initialised to illegal value."

		#
		# Force creatureState to a legal value.
		#
		if not hasattr( self, "creatureState" ):
			self.creatureState = CreatureData.DEAD
			print methodName + "creatureState not initialised."
		else:
			if ( self.creatureState < CreatureData.DEAD or
				self.creatureState > CreatureData.ALLOWED_STATE ):
				self.creatureState = CreatureData.DEAD
				print methodName + "creatureState initialised to illegal value."

		#
		# Check that lookAtTarget has been set.
		#
		if not hasattr( self, "lookAtTarget" ):
			self.lookAtTarget = 0
			print methodName + "lookAtTarget not initialised."

		#
		# Build the creature's name.
		#
		if not hasattr( self, "creatureName" ):
			self.creatureName = CreatureData.displayNames[ self.creatureType ]
			print methodName + "creatureName not initialised."
		else:
			if not self.creatureName:
				self.creatureName = CreatureData.displayNames[ self.creatureType ]

		#
		# Force creature sounds to a legal value.
		#
		self.randomSound = None


	# --------------------------------------------------------------------------
	# Method: buildActionBindings
	# Description:
	#	- Builds the list of action methods for each creature.
	# --------------------------------------------------------------------------
	def buildActionBindings( self ):
		self.actionMethod = {
			CreatureData.IDLE:				self.performIdleAction,
			CreatureData.GRAZE:				self.performGrazeAction,
			CreatureData.STRETCH:			self.performStretchAction,
			CreatureData.DIE_KILLED:		self.performDieKilledAction,
			CreatureData.DIE_GIBBED:		self.performDieGibbedAction,
			CreatureData.EMIT_SOUND:		self.performEmitSoundAction,
			CreatureData.HIDE:				self.performHideAction,
			CreatureData.REVEAL:			self.performRevealAction,
		}


	# --------------------------------------------------------------------------
	# Method: prerequisites
	# Description:
	#	- Return a list of the resources that we want loaded in the background
	#	for us before onEnterWorld() is called.
	# --------------------------------------------------------------------------
	def prerequisites( self ):
		list = []
		t = self.creatureType
		if CreatureData.gibbedModelNames[ t ] != None:
			list.append( CreatureData.gibbedModelNames[ t ] )
		if CreatureData.modelNames[ t ] != None:
			list.append( CreatureData.modelNames[ t ] )
		if CreatureData.hideFX.has_key( t ):
			list += FX.prerequisites( CreatureData.hideFX[t][0] )
			list += FX.prerequisites( CreatureData.hideFX[t][1] )
		if CreatureData.hitFX.has_key( t ):
			list += FX.prerequisites( CreatureData.hitFX[t] )
		return list


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# Description:
	#	- Updates the creature state and type, which in turns creates a model
	#	  for the creature.
	#	- Sets an animation for the creature if it is dead.
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		#
		# Set standard entity properties dependent on state and type.
		#
		self.prereqs = prereqs
		self.set_creatureType()
		self.set_lookAtTarget()

		#
		# Set idle animations dependent on state.
		#
		if self.model != None:
			if self.creatureState == CreatureData.DEAD:
				self.model.Dead()
			elif self.creatureState == CreatureData.DEAD_GIBBED:
				if CreatureData.gibbedModelNames[ self.creatureType ] != None:
					self.model.Gibbed()
				else:
					self.model.Dead()

		#
		# Retrieve sfx files where needed
		#
		t = self.creatureType
		if CreatureData.hideFX.has_key(t):
			self.hideFX = FX.OneShot(CreatureData.hideFX[t][0],10.0,self.prereqs)
			self.revealFX = FX.OneShot(CreatureData.hideFX[t][1],10.0,self.prereqs)

		if CreatureData.hitFX.has_key(t):
			self.hitFXName = CreatureData.hitFX[t]

		#
		# Minimap
		#
		Minimap.addEntity( self )


	# --------------------------------------------------------------------------
	# This method is called when the entity leaves the world
	# --------------------------------------------------------------------------
	def onLeaveWorld( self ):
		self.model = None
		self.prereqs = None

		#
		# Remove creature minimap icon
		#
		Minimap.delEntity( self )


	# --------------------------------------------------------------------------
	# Method: set_moving
	# Description:
	#	- If the entity was previously not moving, and is now moving,
	#	  reset the filter so that it will not warp.
	# --------------------------------------------------------------------------
	def set_moving( self, oldState ):
		if self.moving == oldState:
			return

		if self.moving:
			#self.filter.reset()
			self.filter.latency = min(
				self.filter.minLatency*2, self.filter.latency )


	# --------------------------------------------------------------------------
	# Method: set_creatureState
	# Description:
	#	- Accessor for the creatureState property.
	#	- Called implicitly by the client when the server sends an update.
	#	- Should be called by the script when changing the creatureState
	#	  variable.
	#
	#	- Resets any state-based idle animations.
	#	- Sets the target capabilities, collision settings, and filters.
	#	- Initiates any random sound callbacks if a random sound is available.
	# --------------------------------------------------------------------------
	def set_creatureState( self, oldState = None ):

		if self.creatureState == oldState:
			return

		#
		# Make sure filler-type animations for idle are stopped if there is
		# a change of state. Otherwise they would keep playing and get blended
		# in with the new state's idle.
		#
		if self.model != None:
			if oldState == CreatureData.DEAD:
				self.model.Dead.stop()
			elif ( oldState == CreatureData.DEAD_GIBBED and
				CreatureData.gibbedModelNames[ self.creatureType ] != None ):
				self.model.Gibbed.stop()

		#
		# Set standard entity variables according to state.
		#
		if self.creatureState == CreatureData.ALIVE:
			self.targetCaps = [Caps.CAP_CAN_BUG, Caps.CAP_CAN_HIT ,
							   Caps.CAP_CAN_USE]

			#
			# Sets up a callback for random noises if specified in the
			# randomSounds list.
			#
			self.startSoundLoop()
		else:
			self.targetCaps = [Caps.CAP_NEVER]


		if self.creatureState == CreatureData.DEAD or self.creatureState == CreatureData.DEAD_GIBBED:
			# align model to terrain
			self.filter = BigWorld.AvatarDropFilter()
			self.filter.alignToGround = True

			if hasattr( self, "am" ):
				self.am.useEntityPitchAndRoll = True
				self.am.turnModelToEntity = True
				self.am.bodyTwistSpeed = math.radians( 60.0 )

			self.lookAtTarget = 0
			self.set_lookAtTarget()
		else:
			self.filter = BigWorld.AvatarDropFilter()
			self.filter.alignToGround = True

		self.setupActionMatcher()


		#
		# Call action methods signifying change of state
		#
		if self.creatureState == CreatureData.HIDDEN:
			self.performHideAction( initial = (oldState == None) )
		elif oldState and oldState == CreatureData.HIDDEN:
			self.performRevealAction()


	# --------------------------------------------------------------------------
	# Method: set_creatureType
	# Description:
	#	- Accessor for the creatureType property.
	#	- Called implicitly by the client when the server sends an update.
	#	- Should be called by the script when changing the creatureType
	#	  variable.
	#
	#	- Loads the appopriate model for the creature. If the creature has
	#	  a gibbed model and its state is DEAD_GIBBED, it will load the gibbed
	#	  model instead.
	# --------------------------------------------------------------------------
	def set_creatureType( self, oldType = None ):
		assert( 1 or oldType ) # Not used

		#
		# Force creature type to a legal value.
		#
		if not self.creatureType in CreatureData.displayNames.keys():
			self.creatureType = CreatureData.UNKNOWN

		#
		# Load the model for the creature. Additional checks are made for the
		# gibbed state so that if there is no gibbed model, the default dead
		# model will be used instead.
		#
		if self.creatureState == CreatureData.DEAD_GIBBED:
			try:
				self.model = self.prereqs[CreatureData.gibbedModelNames[self.creatureType]]
			except KeyError:
				try:
					self.model = self.prereqs[CreatureData.modelNames[self.creatureType]]
				except:
					self.model = None
		else:
			try:
				self.model = self.prereqs[CreatureData.modelNames[self.creatureType]]
			except KeyError:
				self.model = None

		# Collision setup
		if self.model != None:
			if self.creatureState == CreatureData.ALIVE:
				self.setupActionMatcher()
			else:
				self.model.motors[0].entityCollision = False
				self.model.motors[0].collisionRooted = True

		# HeadTracker Setup.
		if self.model != None and self.creatureState != CreatureData.DEAD_GIBBED:
			try:
				self.headNodeInfo = BigWorld.TrackerNodeInfo( self.model,
						"biped Head",
						[("biped Neck3", 1.0 ),
						("biped Neck2", 2.0 ),
						("biped Neck1", 3.0 ),
						("biped Neck",  4.0 ),
						("biped Spine", 2.0 ) ],
						"None",
						-60.0, 60.0,
						-80.0, 80.0,
						180.0 )
				self.tracker = BigWorld.Tracker()
				self.model.tracker = self.tracker
				self.tracker.nodeInfo = self.headNodeInfo
			except:
				self.tracker = None

			self.set_lookAtTarget()
		else:
			self.tracker = None

		# Focal node setup
		if self.model != None:
			try:
				self.focalMatrix = self.model.node( "biped Head" )
			except:
				pass

		self.set_creatureState()
		self.set_creatureName()

		#
		# Set idle animations dependent on state.
		#
		if self.model != None:
			if self.creatureState == CreatureData.DEAD:
				self.model.Dead()
			elif self.creatureState == CreatureData.DEAD_GIBBED:
				if CreatureData.gibbedModelNames[ self.creatureType ] != None:
					self.model.Gibbed()
				else:
					self.model.Dead()


	# --------------------------------------------------------------------------
	# Method: set_creatureName
	# Description:
	#	- Accessor for the creatureName property.
	#	- Called implicitly by the client when the server sends an update.
	#	- Should be called by the script when changing the creatureName
	#	  variable.
	# --------------------------------------------------------------------------
	def set_creatureName( self, oldName = None ):
		assert( 1 or oldName ) # Not used

		if not self.creatureName:
			self.creatureName = CreatureData.displayNames[ self.creatureType ]


	# --------------------------------------------------------------------------
	# Method: set_lookAtTarget
	# Description:
	#	- Accessor for the lookAtTarget property.
	#	- Called implicitly by the client when the server sends an update.
	#	- Should be called by the script when changing the lookAtTarget
	#	  variable.
	# --------------------------------------------------------------------------
	@IgnoreCallbackIfDestroyed
	def set_lookAtTarget( self, oldID = None ):
		assert( 1 or oldID ) # Not used

		if self.model != None and self.tracker != None:
			target = BigWorld.entity( self.lookAtTarget )
			hasFocalMatrices = hasattr(self, "focalMatrix") and hasattr(target, "focalMatrix")
			if target != None and hasFocalMatrices:
				self.tracker.directionProvider = BigWorld.DiffDirProvider(
					self.focalMatrix, target.focalMatrix )
			else:
				self.tracker.directionProvider = BigWorld.EntityDirProvider(self, 1, 0 )


	# --------------------------------------------------------------------------
	# Method: set_healthPercent
	# Description:
	#	- Accessor for the health property.
	# --------------------------------------------------------------------------
	def set_healthPercent( self, oldHealth = None ):
		assert( 1 or oldHealth ) # Not used

		if self == BigWorld.target():
			FantasyDemo.rds.fdgui.updateTargetHealth()


	# --------------------------------------------------------------------------
	# This method sets up the action matcher for a living, moving creature
	# --------------------------------------------------------------------------
	def setupActionMatcher( self ):
		if self.model is None:
			return

		am = self.model.motors[0]
		if self.creatureState == CreatureData.ALIVE:
			collisionSettings = CreatureData.collideWithPlayersWhenAlive
		else:
			collisionSettings = CreatureData.collideWithPlayersWhenDead

		am.entityCollision = collisionSettings[ self.creatureType ][0]
		am.collisionRooted = collisionSettings[ self.creatureType ][1]
		alignToGround = CreatureData.alignToGround[ self.creatureType ]
		am.turnModelToEntity = alignToGround
		am.useEntityPitchAndRoll = alignToGround
		
		am.footTwistSpeed = 0

		self.am = am


	# --------------------------------------------------------------------------
	# Method: name
	# Description:
	#	- Part of the entity interface: This allows the client to get a string
	#	  name for the creature.
	# --------------------------------------------------------------------------
	def name( self ):
		return self.creatureName


	# --------------------------------------------------------------------------
	# Method: performAction
	# Description:
	#	- Dispatches the action specified in the argument to the appropriate
	#	  action method call.
	# --------------------------------------------------------------------------
	def performAction( self, actionID ):
		#
		# Force the actionID to a legal one.
		#
		if actionID < CreatureData.IDLE or actionID > CreatureData.ALLOWED_ACTION:
			actionID = CreatureData.IDLE

		if actionID in CreatureData.allowedActions[self.creatureType]:
			self.actionMethod[ actionID ]()
		else:
			pass


	# --------------------------------------------------------------------------
	# Method: performIdleAction
	# Description:
	#	- Handles all details involving the IDLE action.
	# --------------------------------------------------------------------------
	def performIdleAction( self ):
		pass


	# --------------------------------------------------------------------------
	# Method: performGrazeAction
	# Description:
	#	- Handles all details involving the GRAZE action.
	# --------------------------------------------------------------------------
	def performGrazeAction( self ):
		if self.creatureState == CreatureData.ALIVE and self.model != None:
			if self.tracker != None:
				self.tracker.directionProvider = None
				self.model.Graze( 0.0, self.set_lookAtTarget )
			else:
				self.model.Graze()


	# --------------------------------------------------------------------------
	# Method: performStretchAction
	# Description:
	#	- Handles all details involving the STRETCH action.
	# --------------------------------------------------------------------------
	def performStretchAction( self ):
		if self.creatureState == CreatureData.ALIVE and self.model != None:
			if self.tracker != None:
				self.tracker.directionProvider = None
				self.model.Stretch( 0.0, self.set_lookAtTarget )
			else:
				self.model.Stretch()


	# --------------------------------------------------------------------------
	# Method: performDieKilledAction
	# Description:
	#	- Handles all details involving the DIE_KILLED action.
	# --------------------------------------------------------------------------
	def performDieKilledAction( self ):
		if self.creatureState != CreatureData.DEAD_GIBBED and self.model != None:
			if self.creatureType == CreatureData.CHICKEN:
				self.model.visible = False
				self.model.visibleAttachments = True
			else:
				self.model.Die().Dead()

			# TBD: This should be removed when the animations include a channel
			# for sounds.

			# Sound calls disabled because sound events are missing from soundbank.
			# self.model.playSound( "creatures/striff_young/die" )

		self.creatureState = CreatureData.DEAD
		self.set_creatureState()


	# --------------------------------------------------------------------------
	# Method: performDieGibbedAction
	# Description:
	#	- Handles all details involving the DIE_GIBBED action.
	# --------------------------------------------------------------------------
	def performDieGibbedAction( self ):
		if CreatureData.gibbedModelNames[ self.creatureType ] == None:
			self.performAction( CreatureData.DIE_KILLED )

		gibbedModel = BigWorld.Model(
			CreatureData.gibbedModelNames[ self.creatureType ] )
		if gibbedModel != None:
			self.model.root.attach(gibbedModel)
			self.model.visible = False
			self.model.visibleAttachments = True
			gibbedModel.Gib().Gibbed()

			# TBD: This should be removed when the animations include a channel
			# for sounds.

			# Sound calls disabled because sound events are missing from soundbank.
			# self.model.playSound( "creatures/striff_young/die"  )

		self.creatureState = CreatureData.DEAD_GIBBED
		self.set_creatureState()


	# --------------------------------------------------------------------------
	# Method: performEmitSoundAction
	# Description:
	#	- Handles all details involving the EMIT_SOUND action.
	# --------------------------------------------------------------------------
	@IgnoreCallbackIfDestroyed
	def performEmitSoundAction( self, repeat = False ):
		if repeat: self.doingSoundCallback = 0

		if not self.inWorld: return
		if self.creatureState != CreatureData.ALIVE or \
				self.randomSound == None:
			return

		# Sound calls disabled because sound events are missing from soundbank.
		# self.model.playSound( self.randomSound )

		if repeat:
			randomSound = CreatureData.randomSounds[ self.creatureType ]
			if randomSound != None:
				( self.randomSound, minTime, maxTime ) = randomSound
				time = random.randint( minTime, maxTime )
				BigWorld.callback( time, partial(
					self.performEmitSoundAction, True ) )
				self.doingSoundCallback = 1


	# --------------------------------------------------------------------------
	# Method: performRevealAction
	# Description:
	#	- Some creatures can hide, and reveal themselves later.
	# --------------------------------------------------------------------------
	def performRevealAction( self, repeat = False ):
		self.revealFX.go( self.model )
		self.model.spider_dug.stop()
		self.model.spider_spawn()


	# --------------------------------------------------------------------------
	# Method: performHideAction
	# Description:
	#	- Some creatures can hide, and reveal themselves later.
	# --------------------------------------------------------------------------
	def performHideAction( self, repeat = False, initial = False ):
		if not initial:
			self.hideFX.go( self.model )
			self.model.spider_dig().spider_dug()
		else:
			self.model.spider_dug()


	# --------------------------------------------------------------------------
	# Method: use
	# Description: Allows a player to beckon a creature.
	# --------------------------------------------------------------------------
	def use( self ):
		if self.ownerId != BigWorld.player().id:
			gesture = 18 # BeckonTaunt
			user = BigWorld.player()
			user.didGesture( gesture )
			user.cell.didGesture( gesture )
			user.actionCommence()
			self.cell.startFollow()
		else:
			gesture = 0 # Shooaway
			user = BigWorld.player()
			user.didGesture( gesture )
			user.cell.didGesture( gesture )
			user.actionCommence()
			self.cell.stopFollow()

#Creature.py
