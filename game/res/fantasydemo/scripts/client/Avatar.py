
import math
import BigWorld
import FantasyDemo
import Seat
import random
from functools import partial
import particles
import AvatarMode as Mode
from Math import Vector3
import Item
import ItemLoader
import TeleportSource as TeleportSource

import FDGUI
from FDGUI import Minimap

from Helpers import PSFX

from Helpers import Caps
from Listener import Listenable
from Helpers.CallbackHelpers import *

import XMPPRoster
from Math import *
from bwdebug import *

import AvatarModel

from ModeTarget import ModeTarget

# ------------------------------------------------------------------------------
# Section: class Avatar
# ------------------------------------------------------------------------------
# Note: Any NPC class derived from Avatar must override the enterDeadMode()
# method otherwise they will play the respawn and teleport animation.
# ------------------------------------------------------------------------------


# helper class

class CoordinatedActionPlayer:
	"TODO: Document."

	def __init__( self, enA, enB, resA, resB, doneA = None, doneB = None ):
		self.enA = enA
		self.enB = enB
		self.resA = resA
		self.resB = resB
		self.callCount = 0
		self.doneA = doneA
		self.doneB = doneB

	def __call__( self ):
		self.callCount += 1

		if self.callCount == 2:
			if self.doneA != None:
				self.enA.model.action( self.resA )( 0, self.doneA )
			else:
				self.enA.model.action( self.resA )( 0, self.enA.actionComplete )
			if self.doneB != None:
				self.enB.model.action( self.resB )( 0, self.doneB )
			else:
				self.enB.model.action( self.resB )( 0, self.enB.actionComplete )
		elif self.callCount != 1:
			print "CoordinatedActionPlayer called too many times!"


# helper fns for GestureActions.
def swordSwingGesture( avatar, theAction ):
	loft = BigWorld.Loft( "maps/fx/fx_swish.bmp" )
	loft.maxAge = 0.15

	swordModel = avatar.model.right_hand
	node = swordModel.node("HP_sheath")
	node.attach(loft)
	loft.endPoint = swordModel.node("HP_tip")

	action = avatar.model.action( theAction.actionName )
	action( 0, partial(swordSwingGestureEnd, avatar, loft, node) )


def swordSwingGestureEnd( avatar, loft, node ):
	avatar.actionComplete()
	loft.threshold = 99999.0 # Set to something large to prevent any more trail to be added at this point.
	BigWorld.callback( loft.maxAge, partial(removeSwordSwingLoft, loft, node) )


def removeSwordSwingLoft( loft, node ):
	node.detach(loft)


# another helper class (really just a struct)
class GestureAction:
	"TODO: Document"

	def __init__( self, actionName, canMove, canHoldItem, soundToPlay="", fn=None ):
		self.actionName = actionName
		self.canMove = canMove
		self.canHoldItem = canHoldItem
		self.actionSound = soundToPlay
		self.fn = fn

	def play( self, model, completion ):
		# see if we have a list of actions or just one
		if type( self.actionName ) == type( (0,) ):
			for an in self.actionName[:-1]:
				model.action( an )()
			lastAction = self.actionName[-1]
		else:
			lastAction = self.actionName
		model.action( lastAction )()
		BigWorld.callback( model.action( lastAction ).duration - 0.3, completion )
		if ( self.actionSound != "" ):
			pass # model.playSound( self.actionSound )

# Named constants
CONTEXT_HELP = (
	EXPLORE,
	MOUSE,
	BINOCULARS,
	SWORDFIGHT ) = range( 4 )

# the big avatar class
class Avatar(

# Important bases
BigWorld.Entity,
ModeTarget,
Listenable

):
	"TODO: Document"

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

	# sfxActionMap: Map from action names to sound names or other specialfx such as sparks
	#				and their playback delay (in seconds)
	#
	# Sounds just use the plain sound name, sfx names are prefixed with "@": ie
	# @S = spark,
	# @B = blood
	#
	# NB: they are grouped (with blanks) by their animations
	# (ie anims are shared amoung actions)
	#
	sfxActionMap = {
		"CCPasFwdHit":		(("players/grunts/hurt", 0.500), ("@B", 0.500), ),
		"CCPasMidHit":		(("players/grunts/hurt", 0.500), ("@B", 0.500), ),
		"CCPasBakHit":		(("players/grunts/hurt", 0.500), ("@B", 0.500), ),

		"CCActSlay":		(("sword/shared/hit",	0.500),
							 ("footstep_grass_DL",	0.933),
							 ("footstep_grass_DR",	1.200),
							 ("players/bodyfall01",	1.500),
							 ("players/grunts/hurt",1.500),
							 ("players/bodyfall02",	2.035, -10),
							 ("players/bodyfall02",	2.200, -20),
							 ),

		"CCPasSlay":		(),

		"CCActFwdMiss":		(("sword/med/swish", 0.240), ),
		"CCActFwdParry":	(("sword/med/swish", 0.240), ),

		"CCPasFwdMiss":		(("sword/med/block", 0.500), ("@S", 0.500), ),
		"CCPasFwdParry":	(("sword/med/block", 0.500), ("@S", 0.500), ),

		"CCActFwdKnock":	(("sword/med/bigswish", 0.300), ),
		"CCActFwdHit":		(("sword/med/bigswish", 0.300), ("sword/shared/hit", 0.460), ),

		"CCPasFwdKnock":	(("sword/med/block", 0.500), ("@S", 0.500), ),

		"CCActMidMiss":		(("sword/med/swish", 0.400), ),
		"CCActMidParry":	(("sword/med/swish", 0.400), ),
		"CCActBakMiss":		(("sword/med/swish", 0.400), ),
		"CCActBakParry":	(("sword/med/swish", 0.400), ),

		"CCPasMidMiss":		(("sword/med/block", 0.500), ("@S", 0.500), ),
		"CCPasMidParry":	(("sword/med/block", 0.500), ("@S", 0.500), ),

		"CCPasMidKnock":	(("sword/med/block", 0.500), ("@S", 0.500), ),

		"CCActMidKnock":	(("sword/med/bigswish", 0.300), ),
		"CCActMidHit":		(("sword/med/bigswish", 0.300), ("sword/shared/hit", 0.500), ),
		"CCActBakKnock":	(("sword/med/bigswish", 0.300), ),
		"CCActBakHit":		(("sword/med/bigswish", 0.300), ("sword/shared/hit", 0.500), ),

		"CCPasBakKnock":	(("sword/med/block", 0.500), ("@S", 0.500), ),

		"CCPasBakMiss":		(("players/grunts/effort", 0.200), ),
		"CCPasBakParry":	(("players/grunts/effort", 0.200), ),
	}


	def __init__( self ):
		BigWorld.Entity.__init__( self )
		ModeTarget.__init__( self )
		Listenable.__init__( self )

		self.am = BigWorld.ActionMatcher( self )
		self.focalMatrix = MatrixProduct()

		self.healthHitTime = 0.0

		self.warp = None
		self.deathWarp = None
		self.alighting = 0		# used by Ripper.py

		self.overheadGui = None
		self.overheadIcon = None

		self.rightHandItem = None
		self.shoulderItem = None
		self.rightHipItem = None
		self.leftHipItem = None

		self._itemCache = {}

		self.targettingColour = (64,192,64,255)
		self.minimapColour = self.targettingColour

		# combat camera modes
		self.cameraMode = Avatar.CAMERAMODE_NO_GUN

		# Friends list. List order must correspond to base friendsList.
		self.friendsList = []

		self.cellBoundsModel = None
		#The current WebScreen being used
		self.currentWebScreen = None
		
		self.isStandingUp = False
		self.sitIdleCalbackID = None


	#---------------------------------
	# XMPP Example
	#---------------------------------

	# Callback methods from the XMPP interface on the Base
	def onXmppRegisterWithTransport( self, transport ):
		pass


	def onXmppDeregisterWithTransport( self, transport ):
		pass


	def onXmppMessage( self, friendID, transport, message ):
		pass


	def onXmppRoster( self, roster ):
		pass


	def onXmppRosterItemAdd( self, friendID, transport ):
		pass


	def onXmppRosterItemDelete( self, friendID, transport ):
		pass


	def onXmppPresence( self, friendID, transport, presence ):
		pass


	def onXmppError( self, message ):
		pass



	#---------------------------------
	# Note Data Store Example
	#---------------------------------
	def onAddNote( self, id ):
		return


	def onGetNotes( self, noteList ):
		return


	#---------------------------------
	# Map streaming example
	#---------------------------------
	def mapStreamResponse( self, streamID, minX, minY, maxX, maxY ):
		ERROR_MSG( "Unexpected mapStreamResponse with ID %d" % ( streamID, ) )


	#---------------------------------
	# General Avatar methods
	#---------------------------------

	# This method is also used by the Ripper.
	def initPhysics( self ):
		self.physics = BigWorld.STANDARD_PHYSICS
		self.physics.velocity		= ( 0.0, 0.0, 0.0 )
		self.physics.velocityMouse	= "Direction"
		self.physics.angular		= 0
		self.physics.angularMouse	= "MouseX"
		self.physics.oldStyleCollision = FantasyDemo.rds.oldStyleCollision
		# old style physics flag
		self.physics.collide = 1
		# new style physics flags
		self.physics.collideTerrain = 1
		self.physics.collideObjects = 1
		self.physics.fall = 1
		self.physics.modelWidth = 0.47
		self.physics.modelDepth = 0.3


	# This method is called when the entity enters the world
	# Any of our properties may have changed underneath us,
	#  so we do most of the entity setup here
	def onEnterWorld( self, prereqs ):
		self.filter = BigWorld.AvatarFilter()

		self.setTargetCaps()

		self.am.turnModelToEntity = 0
		self.am.matcherCoupled = 1
		self.am.matchCaps = [2,]
		self.am.entityCollision = 1
		self.am.collisionRooted = 0
		self.am.footTwistSpeed = math.radians( 270 )

		self.entityDirProvider = BigWorld.EntityDirProvider(self, 1, 0)

		self.waitingMode = -1
		self.modelHidden = self.alighting
		self.inDeadState = 0
		self.causeOfDeath = Avatar.COD_SHOT
		self.tightFocus = -1

		self.rightHandItem = None

		# tell the team about it
		#Team.entityEntered( self )

		# set up our model and items
		orh = self.rightHand
		self._lockRHCounter = 0
		self.rightHand = Item.Item.NONE_TYPE

		#Never let self.model == None
		self.model = BigWorld.Model("")
		self.set_avatarModel()

		self.rightHand = orh
		self.set_rightHand( Item.Item.NONE_TYPE, 0 )

		# Add to dot to minimap if not a player
		if BigWorld.player() == None or BigWorld.player() != self:
			Minimap.addEntity( self )

		if self.vehicle and hasattr( self.vehicle, 'passengerEnterWorld' ):
			self.vehicle.passengerEnterWorld( self )

		# XMMP Friends list
		self.roster = XMPPRoster.XMPPRoster()


	# This method is called when the entity leaves the world
	def onLeaveWorld( self ):

		# Remove dot from minimap if not a player
		if BigWorld.player() != None and BigWorld.player() != self:
			Minimap.delEntity( self )

		if self.warp != None:
			self.delModel( self.warp )
			self.warp = None

		if self.deathWarp != None:
			try:	self.delModel( self.deathWarp )
			except:	pass
			self.deathWarp = None

		# tell the team about it
		#Team.entityLeft( self )

		if self.mode == Mode.COMBAT_CLOSE:
			self.leaveCloseCombatMode()

		if hasattr( self, "doingAction" ):
			if self.doingAction > 0:
				self.actionComplete()

		# The code below may want to be put in at some stage. JWD 10/09/2002
		#self.worldTransition = 1
		#om = self.mode
		#self.mode = Mode.NONE
		#self.leaveMode()
		#self.mode = om
		#self.worldTransition = 0

		# If player is on a vehicle, let it know...
		#if not self.vehicle == None:
			#self.vehicle.pilotDead()

		BigWorld.target.exclude = self

		self.rightHandItem = None
		self.model = None

		self.overheadGui    = None
		self.overheadIcon   = None

		if hasattr( self, "waterListenerID" ):
			BigWorld.delWaterVolumeListener( self.waterListenerID )
			del self.waterListenerID



	def clientOnCreateCellFailure( self ):
		FantasyDemo.onCreateAvatarFailed()


	def setTargetCaps( self ):
		if self != BigWorld.player():
			#if self.mode == Mode.DEAD:
			#	if Team.members.has_key( self.id ):
			#		self.targetCaps = [Caps.CAP_CAN_REVIVE]
			#	else:
			#		self.targetCaps = [Caps.CAP_NEVER]
			#elif Team.members.has_key( self.id ):
			#	self.targetCaps = [Caps.CAP_CAN_BUG, Caps.CAP_CAN_USE, Caps.CAP_CAN_FEED]
			#else:
			self.targetCaps = [Caps.CAP_CAN_BUG, Caps.CAP_CAN_USE,
							   Caps.CAP_CAN_FEED, Caps.CAP_CAN_HIT,
							   Caps.CAP_CAN_TAKE_DOWN, Caps.CAP_CAN_MELEE,
							   Caps.CAP_CAN_SHONK]

	# Called by script (hack) to give us a simpler mesh, or not
	def toggleMesh( self, flag ):
		pass

	# Hide ourselves. Just hide, don't go away.
	@IgnoreCallbackIfDestroyed
	def hideModel( self, flag ):
		self.modelHidden = flag
		self.model.visible = not self.modelHidden

	# Returns true if we can set off a mine (by being near it)
	def canSetOffMine( self, mine ):
		return self.id != mine.owner

	# -------------------------------------------------------------------------
	# Section: Items trading
	# -------------------------------------------------------------------------

	def tradeActiveEnterMode( self ):
		'''Called when Avatar.mode gets set by the cell. The active
		Avatar takes care of setting up the stage, animating both characters
		and showing the trade icon if it's partner is this player.
		'''
		partner = ModeTarget._getModeTarget( self )
		if partner == None:
			ERROR_MSG( "Unable to find modeTarget entity: %s" % self.modeTarget )
			return

		player = BigWorld.player()
		self.tradeAnimateAccept()
		partner.tradeAnimateAccept()
		if partner == player:
			FantasyDemo.addChatMsg( -1, 'Player has agreed to trade with you' )
			player.tradeShowGUI( True )


	def tradeActiveLeaveMode( self ):
		'''Called when Avatar.mode gets set by the cell. Cleans the scene.
		'''
		player = BigWorld.player()
		if self.getLastModeTarget() == player:
			player.tradeShowGUI( False )


	def tradePassiveEnterMode( self ):
		'''Called when Avatar.mode gets set by the cell. If partner is this
		player, shows the trade icon and add a chat message to the console.
		'''
		player = BigWorld.player()
		if ModeTarget._getModeTarget( self ) == player:
			FantasyDemo.addChatMsg( -1, 'Player wants to trade with you' )


	def tradePassiveLeaveMode( self ):
		'''Called when Avatar.mode gets set by the cell.
		Clears trade icon if partner was this player.
		'''
		pass


	def tradeDeny( self ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def tradeAnimateAccept( self, endCallback = None ):
		'''Plays the trade accept animation on this avatar.
		'''
		if self.mode == Mode.TRADE_PASSIVE:
			self.model.Shake_B_Extend().Shake_B_Accept( 0, endCallback )
		elif self.mode == Mode.TRADE_ACTIVE:
			self.model.Shake_A_Extend().Shake_A_Accept( 0, endCallback )
		elif self.mode == Mode.COMMERCE:
			self.model.Shake_A_Extend().Shake_A_Accept( 0, endCallback )
		else:
			assert False, 'Not in trade or commerce mode'


	def tradeOfferItemNotify( self, itemType ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def tradeOfferItemDeny( self, tradeItemLock ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def tradeAcceptNotify( self ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def tradeCommitNotify( self, success, outItemsLock,
			outItemsSerial, outGoldPieces, inItemsTypes,
			inItemsSerials, inGoldPieces ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False

	# -------------------------------------------------------------------------
	# Section: Items locking
	# -------------------------------------------------------------------------

	def itemsLockNotify( self, lockHandle, itemsSerials, goldPieces ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def itemsUnlockNotify( self, success, lockHandle ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False

	# -------------------------------------------------------------------------
	# Section: Items commerce
	# -------------------------------------------------------------------------

	def commerceEnterMode( self ):
		'''Called when Avatar.mode gets set by the cell.
		The Avatar takes care of animating both characters.
		'''
		partner = ModeTarget._getModeTarget( self )
		if partner != None:
			partner.tradeAnimateAccept()
			self.tradeAnimateAccept()


	def commerceLeaveMode( self ):
		'''Called when Avatar.mode gets set by the cell. Does nothing.
		'''
		pass


	def commerceStartDeny( self ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def commerceItemsNotify( self, items ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False

	# -------------------------------------------------------------------------
	# Section: Items pick-up
	# -------------------------------------------------------------------------

	def pickUpResponse( self, success, droppedItemID, itemSerial ):
		'''Overriden by PlayerAvatar. Never called on non-player Avatars.
		'''
		assert False


	def pickUpNotify( self, droppedItemID ):
		'''Cell entity is notifying that this entity is picking up an item
		Params:
			droppedItemID		id of item entity being picked up
		'''
		try:
			droppedItem = BigWorld.entities[ droppedItemID ]
			self._pickUpProcedure( droppedItem )
			self.lockRightHandModel( True )
		except KeyError:
			print 'pickUpNotify for unknown entity: %d' % droppedItemID


	def _pickUpProcedure( self, droppedItem ):
		'''Do the pickup procedure.
		Params:
			droppedItem			item entity being picked up
		'''
		def doStep1():
			droppedItem.pickUpNotify( self )
			self.pickUpAnimate( doStep2, lambda: None )

		def doStep2():
			droppedItem.pickUpComplete()
			self.lockRightHandModel( False )

		doStep1()


	def pickUpAnimate( self, equipCallback, completeCallback ):
		'''Do a three step pick-up animation: (1) bend down,
		(2) pick-up/equip item and (3) raise up. Call equipCallback and
		completeCallback after step 2 and 3 respectively.
		Params:
			equipCallback		callback called when item is ready to be equiped
			completeCallback	callback called when animation has completed
		'''
		model = self.model.PickUpStart().PickUp( 0, equipCallback )
		model.PickUpComplete( 0, completeCallback )


	def disagree( self ):
		'''Play the disagree animation.
		'''
		self.actionCommence()
		self.didGesture( 4 )

	# -------------------------------------------------------------------------
	# Section: Items drop
	# -------------------------------------------------------------------------

	def dropNotify( self, droppedItem ):
		'''DroppedItem is notifying that this entity is dropping the item.
		Params:
			droppedItem			item entity being dropped
		'''
		self._dropProcedure( droppedItem )


	def _dropProcedure( self, droppedItem ):
		'''Do the drop procedure. Overriden by PlayerAvatar
		Params:
			droppedItem			item entity being dropped
		'''
		def doStep1():
			self.lockRightHandModel( True )
			self.dropAnimate( droppedItem, doStep2, lambda: None )

		def doStep2():
			droppedItem.dropComplete()
			self.lockRightHandModel( False )

		doStep1()


	def dropDeny( self ):
		'''Never called on non-player Avatars.
		'''
		assert False


	def dropAnimate( self, droppedItem, unequipCallback, completeCallback ):
		'''Do the drop animations itself in three parts. Decides what drop
		animation to play based on the distance from the entity to the item.
		Calls unequipCallback and completeCallback after steps 2 and 3,
		respectively.
		Params:
			droppedItem			item entity being dropped
			unequipCallback	callback called when item is ready to be unequiped
			completeCallback	callback called when animation has completed
		'''
		if self.mode == Mode.DEAD:
			unequipCallback()
			return

		queuer = self.model.PickUpStart().PickUp( 0, unequipCallback )
		queuer.PickUpComplete( 0, completeCallback )

	# -------------------------------------------------------------------------
	# Section: Feeding
	# -------------------------------------------------------------------------

	# We somehow ended up feeding something to someone (possibly ourself)
	def feed( self, item, targetID ):
		item

		if self != BigWorld.player():
			self.actionCommence()

		if self.rightHandItem.canEat:
			if targetID == 0:
				self.rightHandItem.eat( self )
			else:
				self.rightHandItem.feed( self, BigWorld.entity( targetID ) )
		else:
			print "Just what are you trying to eat?"
			self.actionComplete()


	# We somehow ended up eating something
	def eat( self, item ):
		item

		self.actionCommence()
		try:
			if self.rightHand == Item.Item.DRUMSTICK_TYPE:
				# BigWorld.playFxDelayed("eat_drumstick", 0.2, self.position)
				if random.random() < 0.2:
					pass # BigWorld.playFxDelayed("burp", 3.0, self.position)
				self.model.EatDrumstick(0,self.actionComplete);
				self.model.Fat()

			elif self.rightHand == Item.Item.GOBLET_TYPE:
				# BigWorld.playFxDelayed("drink", 0.2, self.position)
				if random.random() < 0.2:
					pass # BigWorld.playFxDelayed("burp", 3.5, self.position)
				self.model.DrinkFromFlask( 0,self.actionComplete )
				self.model.Skinny()

			else:
				print "Just what are you trying to eat?"
				self.actionComplete()
		except:
			self.actionComplete()


	# We made an unsucessful attempt at assailing someone
	#  (never called if we're the player)
	def assail( self ):
		if self.rightHandItem != None:
			self.rightHandItem.enact( self, None )

	def inMeleeCombat( self ):
		return self.rightHandItem != None and ( self.rightHandItem.canSwing )

	# utility function
	def inCombat( self ):
		return self.rightHandItem != None and ( self.rightHandItem.canShoot or self.rightHandItem.canSwing )

	def enterWaterCallback( self, entering, volume ):
		if entering:
			self.am.matchCaps = [16,]
		else:
			self.am.matchCaps = [2,]


	def set_avatarModel( self, oldValue = None, callback = lambda: None ):

		self.loadingResource = True
		unpackedAvatarModel = AvatarModel.unpack( self.avatarModel )

		BigWorld.loadResourceListBG( AvatarModel.getPrerequisites( unpackedAvatarModel ),
									partial( self.set_avatarModel_stage2, self.avatarModel, unpackedAvatarModel, callback ) )


	@IgnoreCallbackIfDestroyed
	def set_avatarModel_stage2( self, packedAvatarModel, unpackedAvatarModel, callback, resourceRefs ):

		# this is a workaround for models not properly restoring actions and their callbacks
		# bug: 22631
		if hasattr( self, "doingAction" ) and self.doingAction > 0:
			BigWorld.callback( 0.5, partial( self.set_avatarModel_stage2, packedAvatarModel, unpackedAvatarModel, callback, resourceRefs ) )
			return

		if self.avatarModel != packedAvatarModel:
			return

		# detach all items from previous model
		if hasattr(self.model, "right_hand"):
			self.model.right_hand = None
		if hasattr(self.model, "left_hip"):
			self.model.left_hip = None
		if hasattr(self.model, "right_hip"):
			self.model.right_hip = None
		if hasattr(self.model, "shoulder"):
			self.model.shoulder = None


		savedActionQueue = ResMgr.DataSection( 'savedActionQueue' )
		self.model.saveActionQueue( savedActionQueue )

		self.model = AvatarModel.create( unpackedAvatarModel, self.model )

		self.model.restoreActionQueue( savedActionQueue )

		orh = self.rightHand
		if self.rightHand != Item.Item.NONE_TYPE:
			self.rightHand = Item.Item.NONE_TYPE
			self.set_rightHand( orh, 0 )

		if hasattr( self, "waterListenerID" ):
			BigWorld.delWaterVolumeListener( self.waterListenerID )
			del self.waterListenerID

		try:
			self.waterListenerID = BigWorld.addWaterVolumeListener( self.model.node("biped Spine"), self.enterWaterCallback )
		except:
			self.waterListenerID = BigWorld.addWaterVolumeListener( self.model.matrix, self.enterWaterCallback )

		#self.set_colour()

		# Add any extra effects here based on the model.
		# Note: This should probably be based on the Avatar state.
		# In the case of persistent particle effects, the code should just
		# check that Avatar state check is normal.

		# TO DO: add glowing eyes for wraiths.

		#self.respawnEnergyMist = particles.respawnEnergyMist( self )

		if self.am.owner != None: self.am.owner.delMotor( self.am )
		self.model.motors = ( self.am, )

		try:
			self.setFocalNode()
		except:
			pass

		try:
			lfoot = self.model.node( "biped L Toe0" )
			rfoot = self.model.node( "biped R Toe0" )

			# create left & right feet
			footSoundPath = "players/footsteps"
			self.footTriggers = [BigWorld.FootTrigger( 0, footSoundPath ),
								 BigWorld.FootTrigger( 1, footSoundPath )]
			lfoot.attach( self.footTriggers[0] )
			rfoot.attach( self.footTriggers[1] )

			# Add dust trails.
			self.dustSource = particles.attachDustSource( self.model )
			try:
				self.footTriggers[0].dustSource = self.dustSource.action(1)
				self.footTriggers[1].dustSource = self.dustSource.action(1)
			except:
				self.footTriggers[0].dustSource = self.dustSource.system(0).action(1)
				self.footTriggers[1].dustSource = self.dustSource.system(0).action(1)
		except:
			print "ERROR: Unable to set up foot triggers for model ['%s']" % "', '".join( self.model.sources )

		# put any item back in our hand, shoulders and hip.
		if orh != Item.Item.NONE_TYPE:
			self.rightHand = orh
			self.set_rightHand( Item.Item.NONE_TYPE, 0 )
		self.set_shoulder()
		self.set_rightHip()
		self.set_leftHip()

		self.hideModel( self.modelHidden )

		try:
			# HeadTracker Setup.
			self.headNodeInfo = BigWorld.TrackerNodeInfo(
				self.model,
				"biped Head",
				[ ( "biped Neck", -0.20 ),
				  ( "biped Spine", 0.50 ),
				  ( "biped Spine1", 0.40 ) ],
				"None",
				-60.0, 60.0,
				-80.0, 80.0,
				360,
				45,
				0.1)

			self.gunAimingNodeInfo = BigWorld.TrackerNodeInfo(
				self.model,
				"biped Spine",
				[	( "biped Spine1", 1 ),
					( "biped Neck", 1 ) ],
				"biped Spine",
				-60.0, 60.0,
				-80.0, 80.0,
				270.0 )

			self.tracker = BigWorld.Tracker()
			self.model.tracker = self.tracker

			# this if test is temporary and should be removed
			# as soon as the beziel model get his skeleton fixed
			import Guard
			if not isinstance(self, Guard.Guard):
				if not (self.rightHandItem and self.rightHandItem.canShoot):
					self.tracker.nodeInfo = self.headNodeInfo
				else:
					self.tracker.nodeInfo = self.gunAimingNodeInfo
				self.tracker.directionProvider = self.entityDirProvider

			if self.mode == Mode.DEAD:
				self.disableAllTrackers()
		except:
			print "ERROR: Unable to set head tracker for model ['%s']" % "', '".join( self.model.sources )


		# Get our respective camera heights from the model.
		# TBD: Setting these first for now. Will get model info later.
		self.cameraHeightWhenStanding = self.model.height
		self.cameraHeightWhenCrouched = self.model.height * 0.5
		self.cameraHeightWhenSeated   = self.model.height * 0.65

		if self.mode == Mode.SEATED:
			FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenSeated, 0.0 )
		elif self.mode == Mode.CROUCH:
			FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenCrouched, 0.0 )
		else:
			FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenStanding, 0.0 )

		# set up the lip sync fashion
		self.setupLipSyncer()

		self.onModelChangeUpdateMode()

		self.loadingResource = False
		callback()

	# morph target names for morphing lips
	lipMorphs = ('oh', 'ahh', 'angry')

	# set up lip syncing if we have it
	def setupLipSyncer( self ):
		pass

	def chooseColourFromTable( self, idx ):
		if not hasattr( self, "customColourTable" ):
			cols = []
			cols.append([  (0.254646, 0.493217, 0.273348, 1.000000) , (0.933844, 0.777852, 0.769663, 1.000000) , (0.398893, 0.522769, 0.206916, 1.000000) , (0.101148, 0.138710, 0.111911, 1.000000)  ])
			cols.append([  (0.651712, 0.804786, 0.637214, 1.000000) , (0.454525, 0.296249, 0.603035, 1.000000) , (0.552301, 0.365443, 0.334284, 1.000000) , (0.427665, 0.431813, 0.525500, 1.000000)  ])
			cols.append([  (0.338514, 0.843630, 0.319555, 1.000000) , (0.102077, 0.223424, 0.069588, 1.000000) , (0.477499, 0.479614, 0.093775, 1.000000) , (0.153238, 0.658224, 0.282533, 1.000000)  ])
			cols.append([  (0.383577, 0.915329, 0.895179, 1.000000) , (0.366810, 0.726941, 0.973709, 1.000000) , (0.448015, 0.315202, 0.232618, 1.000000) , (0.570178, 0.286184, 0.187847, 1.000000)  ])
			cols.append([  (0.619137, 0.469237, 0.537302, 1.000000) , (0.369039, 0.300652, 0.496189, 1.000000) , (0.461669, 0.406311, 0.222290, 1.000000) , (0.808304, 0.842354, 0.731943, 1.000000)  ])
			cols.append([  (0.365277, 0.354405, 0.698976, 1.000000) , (0.171019, 0.461236, 0.538547, 1.000000) , (0.823559, 0.088536, 0.286342, 1.000000) , (0.375137, 0.903168, 0.767630, 1.000000)  ])
			cols.append([  (0.401896, 0.554190, 0.910975, 1.000000) , (0.992968, 0.291006, 0.166388, 1.000000) , (0.210172, 0.191736, 0.186281, 1.000000) , (0.630907, 0.286023, 0.236809, 1.000000)  ])
			cols.append([  (0.612891, 0.585045, 0.627191, 1.000000) , (0.255579, 0.025262, 0.184869, 1.000000) , (0.467111, 0.669241, 0.226030, 1.000000) , (0.552551, 0.736929, 0.379236, 1.000000)  ])
			cols.append([  (0.478003, 0.438623, 0.290965, 1.000000) , (0.894686, 0.862873, 0.615390, 1.000000) , (0.671886, 0.552357, 0.281442, 1.000000) , (0.885097, 0.856283, 0.778209, 1.000000)  ])
			cols.append([  (0.522206, 0.451343, 0.232465, 1.000000) , (0.569357, 0.515254, 0.144128, 1.000000) , (0.461813, 0.073066, 0.234372, 1.000000) , (0.625959, 0.186348, 0.592377, 1.000000)  ])
			cols.append([  (0.888899, 0.553464, 0.173847, 1.000000) , (0.293426, 0.285857, 0.198984, 1.000000) , (0.547580, 0.092823, 0.267288, 1.000000) , (0.939010, 0.293352, 0.517629, 1.000000)  ])
			cols.append([  (0.759867, 0.959759, 0.982294, 1.000000) , (0.880115, 0.283955, 0.033396, 1.000000) , (0.266175, 0.537536, 0.438662, 1.000000) , (0.512929, 0.354165, 0.266605, 1.000000)  ])
			cols.append([  (0.600831, 0.743807, 0.703723, 1.000000) , (0.300400, 0.545004, 0.644512, 1.000000) , (0.688422, 0.340142, 0.004766, 1.000000) , (0.472573, 0.440426, 0.267864, 1.000000)  ])
			cols.append([  (0.578025, 0.845675, 0.745759, 1.000000) , (0.349171, 0.086918, 0.277436, 1.000000) , (0.590162, 0.227906, 0.554312, 1.000000) , (0.337594, 0.360935, 0.262908, 1.000000)  ])
			cols.append([  (0.623980, 0.672316, 0.189026, 1.000000) , (0.889134, 0.583676, 0.198866, 1.000000) , (0.892509, 0.731511, 0.831040, 1.000000) , (0.546391, 0.280228, 0.050640, 1.000000)  ])
			cols.append([  (0.899648, 0.528558, 0.941157, 1.000000) , (0.533302, 0.750191, 0.940004, 1.000000) , (0.665484, 0.199860, 0.366958, 1.000000) , (0.445581, 0.481421, 0.296309, 1.000000)  ])
			cols.append([  (0.597921, 0.487229, 0.327416, 1.000000) , (0.796666, 0.699612, 0.937783, 1.000000) , (0.277807, 0.083920, 0.114420, 1.000000) , (0.826359, 0.146185, 0.960009, 1.000000)  ])
			cols.append([  (0.149531, 0.438053, 0.002597, 1.000000) , (0.062633, 0.474245, 0.343709, 1.000000) , (0.773542, 0.469882, 0.313250, 1.000000) , (0.725692, 0.755280, 0.502405, 1.000000)  ])
			cols.append([  (0.159739, 0.195771, 0.325857, 1.000000) , (0.588584, 0.225984, 0.057916, 1.000000) , (0.234929, 0.333477, 0.505054, 1.000000) , (0.666816, 0.259040, 0.163941, 1.000000)  ])
			cols.append([  (0.768643, 0.270522, 0.107105, 1.000000) , (0.054516, 0.141897, 0.589053, 1.000000) , (0.615351, 0.653648, 0.588571, 1.000000) , (0.988234, 0.852759, 0.636260, 1.000000)  ])
			cols.append([  (0.830812, 0.718017, 0.028693, 1.000000) , (0.593831, 0.727215, 0.451927, 1.000000) , (0.287905, 0.462448, 0.150299, 1.000000) , (0.674195, 0.838175, 0.462626, 1.000000)  ])
			cols.append([  (0.913555, 0.646139, 0.555507, 1.000000) , (0.561943, 0.438088, 0.591138, 1.000000) , (0.226763, 0.228060, 0.592938, 1.000000) , (0.875686, 0.859162, 0.775180, 1.000000)  ])
			cols.append([  (0.500000, 0.200000, 0.100000, 1.000000) , (0.437556, 0.831906, 0.047606, 1.000000) , (0.268502, 0.470271, 0.089447, 1.000000) , (0.942319, 0.872523, 0.890474, 1.000000)  ])
			self.customColourTable = cols

		return self.customColourTable[ idx % len(self.customColourTable) ]



	# Someone set the item in our right hand
	# First Stage: Set up animations
	def set_rightHand( self, oldRH = None, itemChangeAnim = 1 ):
		if oldRH != None and oldRH == self.rightHand: return

		# if we're in the process of becoming the player, don't
		# call its functions (this is BAD that we have to do this!)
		if self == BigWorld.player() and self.physics == None:
			endFn = partial( Avatar.set_rightHandEnd, self )
		else:
			endFn = self.set_rightHandEnd

		# Test if the hard point exists for this model.
		try:
			self.model.right_hand
		except AttributeError, e:
			if len( "".join( self.model.sources ) ) > 0:
				print "ASSET ERROR: No hard point 'right_hand'  model ['%s']" % "', '".join( self.model.sources )
			return

		# stop any existing animations
		if self.inWorld:
			aq = self.model.queue
			haveCIB = "ChangeItemBegin" in aq
			haveCIE = "ChangeItemEnd" in aq

			# ... if we can't recycle them
			if haveCIE:
				# currently queue is only playing actions, not waiting ones
				self.model.ChangeItemEnd.stop()

		# increment the right hand lock counter.  when it goes back down to
		# zero, the model swap can take place.
		self.lockRightHandModel( True )

		# this is the item retrieval lock on the rhm.
		self.lockRightHandModel( True )

		# get the item, either this has been cached, or we need to bg load it
		if self._itemCache.has_key(self.rightHand):
			self.lockRightHandModel(False)
		else:
			#start the item loading, and increment the rhi counter again, only decrementing
			#it when the item has finished loading.
			ItemLoader.LoadBG( self.rightHand,
				partial( self.lockRightHandModel, False ) )

		# start the animations if we want them
		if self.inWorld:
			#Added this exception handler due to temporary lack of
			#Actions in models.  Should probably fix this in art not
			#with workarounds in code.
			if hasattr( self.model, "ChangeItemBegin" ):
				cib = self.model.ChangeItemBegin
				cibDur = cib.duration - cib.blendOutTime - 0.0001
			else:
				ERROR_MSG( "model does not have required action ChangeItemBegin" )
				endFn( itemChangeAnim )
				return

			if itemChangeAnim == 1:
				if haveCIE or not haveCIB:
					cib().ChangeItemEnd()
					#cib()
					#self.model.ChangeItemEnd( -cibDur )
					self.lastICAStarted = BigWorld.time()
				else:
					self.lastICAStarted += 0.0001
					cibDur -= BigWorld.time() - self.lastICAStarted
					if cibDur < 0: cibDur = 0.0001
			else:	# itemChangeAnim == 0
				if not (haveCIB or haveCIE):
					# have to be careful if there's one already running,
					# that its callback doesn't happen after ours,
					# so we wait the whole duration just in case
					# (this is the else case of this conditional)
					cibDur = 0

			if cibDur:
				BigWorld.callback( cibDur, partial( endFn, itemChangeAnim ) )
			else:
				endFn( itemChangeAnim )
		else:
			endFn( itemChangeAnim )


	# Second Stage: Swap actual item in hand
	def set_rightHandEnd( self, itemChangeAnim ):
		if self.isDestroyed:
			return
			
		if self.rightHandItem != None:
			self.rightHandItem.unequip( self )

		if self.inWorld and itemChangeAnim == 1:
			pass # BigWorld.playFx("stow_item", self.position)

		self.lockRightHandModel( False )


		#tmp workaround for no action on some model.
		try:
			self.model.HoldUpright.stop()
		except AttributeError:
			pass


	def getItem( self, itemType, itemLoader = None ):
		if self._itemCache.has_key( itemType ):
			return self._itemCache[ itemType ]
		elif itemLoader:
			return ItemLoader.newItem( itemType, itemLoader.resourceRefs )
		elif hasattr(self, "itemLoader") and self.itemLoader:
			return ItemLoader.newItem( itemType, self.itemLoader.resourceRefs )
		else:
			#Note - should never reach this part of the code, doing so will cause a pause
			#in the main thread and indicates the background loading of items has gone awry.
			return ItemLoader.newItem( itemType )

	@IgnoreCallbackIfDestroyed
	def lockRightHandModel( self, lock, itemLoader = None ):
		if not lock:
			self._lockRHCounter -= 1
		else:
			self._lockRHCounter += 1

		assert self._lockRHCounter >= 0, 'Right hand lock went negative'

		if self._lockRHCounter == 0:

			self.rightHandItem = self.getItem( self.rightHand, itemLoader )
			if hasattr( self, "itemLoader" ):
				self.itemLoader = None

			if self.rightHandItem != None:
				self.model.right_hand = self.rightHandItem.model
				if self.inCombat():
					self.rightHandItem.enactDrawn( self )
				else:
					self.rightHandItem.enactIdle( self )
			else:
				self.model.right_hand = None
		elif itemLoader != None:
			#cache itemLoader until we need it.  When observing 3rd persons change
			#items that are already loaded in memory (for example when the player
			#avatar already has the item cached), the ItemLoader.loadBG call finishes
			#immediately, and the unlock calls to this fn ending up going like:
			#lockRightHandModel( false, itemLoader )  #lock goes to 1
			#lockRightHandModel( false, None )		  #lock goes to 0 - show new item
			#(The first one is called when the item is BG loaded - i.e. immediately)
			#(The second one is called when the switch item animation finishes)
			self.itemLoader = itemLoader


	# Someone changed the item on our shoulder.
	def set_shoulder( self, oldItem = None ):
		if oldItem != None and oldItem == self.shoulder:
			return

		# Unequip the old item if we had one
		if self.shoulderItem:
			del self.shoulderItem
			self.shoulderItem = None

		# Test if the hard point exists for this model.
		try:
			self.model.shoulder
		except:
			#print 'Avatar model does not have hardpoint: shoulder'
			return

		self.shoulderItem = self.getItem( self.shoulder )
		if self.shoulderItem != None:
			self.model.shoulder = BigWorld.Model(*self.shoulderItem.model.sources)
		else:
			self.model.shoulder = None


	# Someone changed the item on our right hip.
	def set_rightHip( self, oldItem = None ):
		if oldItem != None and oldItem == self.rightHip:
			return

		# Unequip the old item if we had one
		if self.rightHipItem:
			del self.rightHipItem
			self.rightHipItem = None

		# Test if the hard point exists for this model.
		try:
			self.model.right_hip
		except:
			#print 'Avatar model does not have hardpoint: right_hip'
			return

		self.rightHipItem = self.getItem( self.rightHip )
		if self.rightHipItem != None:
			self.model.right_hip = BigWorld.Model(*self.rightHipItem.model.sources)
		else:
			self.model.right_hip = None


	# Someone changed the item on our left hip.
	def set_leftHip( self, oldItem = None ):
		if oldItem != None and oldItem == self.leftHip: return

		# Unequip the old item if we had one
		if self.leftHipItem:
			del self.leftHipItem
			self.leftHipItem = None

		# Test if the hard point exists for this model.
		try:
			self.model.left_hip
		except:
			#print 'Avatar model does not have hardpoint: left_hip'
			return

		self.leftHipItem = self.getItem( self.leftHip )
		if self.leftHipItem != None:
			self.model.left_hip = BigWorld.Model(*self.leftHipItem.model.sources)
		else:
			self.model.left_hip = None


	# Someone changed our health
	def set_healthPercent( self, oldHealth = None ):
		# record the time that regeneration should start
		if oldHealth > self.healthPercent:
			self.healthHitTime = BigWorld.time() + 3.0
		else:
			self.healthHitTime = BigWorld.time()

		oldHealthPct = oldHealth / 100.0 if oldHealth is not None else None
		self.listeners.healthUpdated( self.healthPercent / 100.0, oldHealthPct )

		if self == BigWorld.target():
			FantasyDemo.rds.fdgui.updateTargetHealth()

		if self.mode == Mode.COMBAT_CLOSE and self.healthPercent == 0:
			self.set_stance( self.stance )

	# Someone updated our frag count
	def set_frags( self, oldFrags = None ):
		if BigWorld.player() != None and BigWorld.player().id == self.id \
			and self.frags > oldFrags:
			if self.frags != 1:
				FantasyDemo.addChatMsg( -1, "You now have %d frags" % self.frags )
			else:
				FantasyDemo.addChatMsg( -1, "You got your first frag" )

	# Someone set our mode
	def set_mode( self, oldMode = None ):
		if self.mode == oldMode:
			return
			
		if( self.loadingResource ):
			return 

		self.cancelMode( oldMode )
		self.enterMode( oldMode )


	# Someone set our mode target
	def set_modeTarget( self, oldModeTarget = None ):
		# tell the old target about it:
		if oldModeTarget != None and oldModeTarget != Mode.NO_TARGET:
			oldTargetEntity = BigWorld.entity( oldModeTarget )
			if oldTargetEntity != None:
				BigWorld.entity( oldModeTarget ).modeTargetBlur( self )

		# tell the new target about it
		if self.modeTarget != Mode.NO_TARGET:
			newTargetEntity = BigWorld.entity( self.modeTarget )
			if newTargetEntity != None:
				BigWorld.entity( self.modeTarget ).modeTargetFocus( self )

		self.lastModeTarget = oldModeTarget


	def _onModeTargetReady( self ):
		"""
		Overridden ModeTarget method.
		"""
		DEBUG_MSG( "" )
		if ModeTarget._onModeTargetReady( self ):
			self.enterMode( Mode.NONE )


	def setModeTarget( self, targetID ):
		oldTarget = self.modeTarget
		self.modeTarget = targetID
		self.set_modeTarget( oldTarget )


	def getLastModeTarget( self ):
		try:
			return BigWorld.entities[ self.lastModeTarget ]
		except KeyError:
			errorMsg = 'Avatar.getModeTarget: unknown last target entity (id=%d)'
			print errorMsg % self.lastModeTarget
			return None


	# Going into shonk mode
	def enterShonkMode( self ):
		# If the target is this client's player, then inform the player of
		# the intention to shonk.
		target = ModeTarget._getModeTarget( self )
		if target == None:
			return

		if target == BigWorld.player():
			FantasyDemo.addChatMsg( -1,
				"%s would like to play Paper/Scissors/Rock with you." % self.name() )
			FantasyDemo.addChatMsg( -1,
				"Target %s and press [7] [8] or [9] on the numpad to play." % self.name() )

		self.model.ShonkWait()

	# Going into handshake mode
	def enterHandshakeMode( self ):
		# BigWorld.playFx("rustle", self.position)

		self.inIdle = 0
		self.am.turnModelToEntity = 0

		self.model.Shake_A_Extend().Shake_A_Idle()

		target = ModeTarget._getModeTarget( self )
		if target == None:
			return

		# If the target is this client's player, then inform the player of
		# the intention to shake hands.
		if target == BigWorld.player():
			FantasyDemo.addChatMsg( -1,
				"%s would like to shake your hands." % self.name() )
			FantasyDemo.addChatMsg( -1,
				"Target %s and left-click to accept the handshake." % self.name() )


	# Going into pull up mode
	def enterPullUpMode( self ):
		self.model.PullUpActiveBegin().PullUpActiveIdle()

		# doingAction is left on while we wait for the server response,
		# so we stop that action here before enterMode starts another.
		self.actionComplete()

		target = ModeTarget._getModeTarget( self )
		if target == None:
			return

		# If the target is this client's player, then inform the player of
		# the intention to pull-up.
		if target == BigWorld.player():
			BigWorld.callback( 1.0, self.informTargetOfLiftUp )


	@IgnoreCallbackIfDestroyed
	def informTargetOfLiftUp( self ):
		if self.mode == Mode.PULLUP:
			FantasyDemo.addChatMsg( -1,
				"%s would like to lift you up." % self.name() )
			FantasyDemo.addChatMsg( -1,
				"Target %s and left-click to agree to this." % self.name() )


	# Going into push up mode
	def enterPushUpMode( self ):
		if self.isDestroyed:
			return
		self.model.PushUpActiveBegin().PushUpActiveIdle()

		# doingAction is left on while we wait for the server response,
		# so we stop that action here before enterMode starts another.
		self.actionComplete()

		target = ModeTarget._getModeTarget( self )
		if target == None:
			return

		# If the target is this client's player, then inform the player of
		# the intention to bunk-up.
		if target == BigWorld.player():
			BigWorld.callback( 1.0, self.informTargetOfBunkUp )

	@IgnoreCallbackIfDestroyed
	def informTargetOfBunkUp( self ):
		if self.isDestroyed:
			return
		if self.mode == Mode.PUSHUP:
			FantasyDemo.addChatMsg( -1,
				"%s would like to give you a bunk up." % self.name() )
			FantasyDemo.addChatMsg( -1,
				"Target %s and left-click to agree to this." % self.name() )

	# Going into combat mode
	def enterCombatMode( self, locked, temporary ):
		if not temporary and self.rightHandItem:
			pass

		#AUSTIN GDC - move all matchCaps into items
		#if not locked:
		#	self.am.matchCaps = [0] + filter( lambda x : x>2, self.am.matchCaps )
		#	self.model.CombatL0Blender()
		#else:
		#	self.am.matchCaps = [0,2] + filter( lambda x : x>2, self.am.matchCaps )
		#	self.model.CombatL2Blender()
		#	self.enableTracker( self.gunAimingNodeInfo )

	# Going out of combat mode
	def leaveCombatMode( self, locked, temporary ):
		#AUSTIN GDC - move all matchCaps into items
		#self.am.matchCaps = filter( lambda x : x>2, self.am.matchCaps )

		if not temporary and self.rightHandItem:
			pass

		#AUSTIN GDC - remove combat blenders
		#if not locked:
		#	self.model.CombatL0Blender.stop()
		#else:
		#	self.model.CombatL2Blender.stop()
		#	self.enableTracker( self.headNodeInfo )

	# Going into crouch mode
	def enterCrouchMode( self ):
		self.model.EnterCrouch().Crouch()
		self.actionCommence()


	# Leaving crouch mode
	def leaveCrouchMode( self ):
		self.model.LeaveCrouch(0, self.actionComplete)

	def crouchActionMidway( self ):
		pass

	# Going into sneak mode
	def enterSneakMode( self ):
		pass
		#AUSTIN GDC - move all matchCaps into items
		#self.am.matchCaps = self.am.matchCaps + [6];

	# Leaving sneak mode
	def leaveSneakMode( self ):
		pass
		#AUSTING GDC - move all matchCaps into items
		#self.am.matchCaps = filter( lambda c: c != 6, self.am.matchCaps )


	# Going into seated mode
	def enterSeatedMode( self ):
		self.filter.callback( 0, partial( self.sitDownWait, 5 ) )

	# TODO: At the moment, we wait for up to 5 seconds for the target to be in
	# our AoI. We should not really do this.
	@IgnoreCallbackIfDestroyed
	def sitDownWait( self, count ):
		if BigWorld.entity( self.modeTarget ) != None:
			Seat.sitDown( self )
		elif count > 0:
			BigWorld.callback( 1, partial( self.sitDownWait, count-1 ) )

	# Leaving seated mode
	def leaveSeatedMode( self ):
		Seat.standUp( self )

	# Starting using the item in your hand
	def enterUsingItemMode( self ):
		if self.rightHand != Item.Item.NONE_TYPE:
			try: self.rightHandItem.retain( self )
			except:	self.actionCommence()

	# Stopping using the item in your hand
	def leaveUsingItemMode( self ):
		if self.rightHand != Item.Item.NONE_TYPE:
			try:	self.rightHandItem.release( self )
			except:	self.actionComplete()

	# Helper function for leaveUsingItemMode
	def doneWithLeftHand( self ):
		self.model.left_hand = None


	# Entering close combat
	def enterCloseCombatMode( self ):
		# If we're the player, we've already called actionCommence
		#  when we started the swing

		# Try fetching this entity now
		if BigWorld.entities.has_key( self.modeTarget ):
			self.ccTarget = BigWorld.entity( self.modeTarget )
		else:
			ERROR_MSG( "Unable to find modeTarget entity: %s" % self.modeTarget )
			self.ccTarget = None
			return

		# The fight doesn't start until one of the combatants is nominated
		#  as its director, by receiving a salida message.
		self.ccIsFightDirector = 0
		self.ccBreaking = 0

		# Play the appropriate combat idle animation
		self.set_stance()

		# If we're targetting the player let them know
		if self.ccTarget == BigWorld.player():
			BigWorld.player().ccRespond( self )

		self.listeners.enterCloseCombatMode()


	# Leaving close combat
	def leaveCloseCombatMode( self ):
		BigWorld.callback( 0.1, self.closeCombatDelayedExit )

		# Let us know it's all over
		self.closeCombatNo( self.ccTarget, 1 )

		# Let the target know it's all over too
		if self.ccTarget != None:
			try:
				self.ccTarget.closeCombatNo( self, 0 )
			except:
				pass

		self.listeners.leaveCloseCombatMode()

		# Remove close combat caps
		#AUSTING GDC - move all matchCaps into items
		#self.am.matchCaps = filter( lambda c: c not in range(8,11), self.am.matchCaps )

	# Tidy up after leaving close combat mode. Delayed to hopefully get
	# any messages which may change how we get out of the mode in time.
	@IgnoreCallbackIfDestroyed
	def closeCombatDelayedExit( self ):
		if self.inWorld:
			if self.healthPercent <= 0:
				BigWorld.callback( 1.0, self.actionComplete )
			elif self.ccBreaking:
				BigWorld.callback( 0.7, self.actionComplete )
			else:
				self.model.CCOver( 0, self.actionComplete )


	# The server has decided a new step in the dance
	def salida( self, result ):
		# See if we've had any of these messages before
		if not self.ccIsFightDirector:
			self.ccIsFightDirector = 1

			# Nope, let everyone know who's calling the shots
			self.ccTarget = BigWorld.entity( self.modeTarget )
			self.closeCombatGo( self.ccTarget, 1 )
			try:
				self.ccTarget.closeCombatGo( self, 0 )
			except:
				pass

		# OK, process the step as usual then
		self.closeCombatStepActive( result )


	# Being the target of close combat
	def closeCombatGo( self, assailant, weAreInitiator ):
		assailant
		weAreInitiator

		self.ccBreaking = 0

		self.am.turnModelToEntity = 1
		self.tracker.directionProvider = None

	# No longer the target of close combat
	def closeCombatNo( self, assailant, weAreInitiator ):
		assailant
		weAreInitiator

		if self.mode != Mode.DEAD:
			self.am.turnModelToEntity = 0
			self.tracker.directionProvider = self.entityDirProvider

	# The next step in the close combat dance (active)
	def closeCombatStepActive( self, lr ):
		# Choose our counterpart for this step
		if self.ccTarget == None:
			self.ccTarget = BigWorld.entity( self.modeTarget )
			try:
				self.ccTarget.closeCombatGo( self, 0 )
			except:
				pass
		elif not self.ccTarget.inWorld:
			try:
				self.ccTarget.closeCombatNo( self, 0 )
			except:
				pass
			self.ccTarget = None

		# Tell our dancing partner what to do
		try:
			# Could be none or could not have this fn
			self.ccTarget.closeCombatStepAnswer( lr )
		except:
			pass

		# If we got something from the server, then display it,
		#  otherwise just play a dummy action
		#if lr != -1:
		#	act = self.getCCAction( (lr >> 4) - 1, (lr & 7) - 1, (lr >> 3) & 1 )
		#	self.ccLastResult = -1
		#else:
		#	act = self.model.CCAttack1

		if (lr >> 6) == 1:
			act = self.ccActiveAction( lr & 0x3F )
			delay = 0
		else:
			act = self.ccPassiveAction( lr & 0x3F )
			delay = 8 / 30.0	# 8 frames delay

		if act: self.closeCombatPerform( act, delay )

	# The next step in the close combat dance (passive)
	def closeCombatStepAnswer( self, lr ):
		#if lr != -1:
		#	act = self.getCCAction( (lr & 7) - 1, (lr >> 4) - 1, not ((lr >> 3) & 1) )
		#else:
		#	act = self.model.CCParryR

		if (lr >> 6) == 1:
			act = self.ccPassiveAction( lr & 0x3F )
			delay = 8 / 30.0	# 8 frames delay
		else:
			act = self.ccActiveAction( lr & 0x3F )
			delay = 0

		if act: self.closeCombatPerform( act, delay );

	# This method performs an action for either the active or passive combatant
	def closeCombatPerform( self, act, delay ):
		# start the action running
		if act.impact[2] == 0:
			act( -delay )
		else:
			act( -delay, None, 1 )

		# give the action matcher a break
		#self.am.matcherCoupled = 0
		# no point doing this until we can do the thing below

		# move the entity position to the end of this action
		#self.position = Vector3(self.position) + Vector3(act.displacement)
		# can't move client entity position ... yet - we need the
		# filter modification thingy

		# Note: really want to turn on am after end of action ...
		# so it does the idle/stance thing for us... hmmm.
		# assumes that position will be right or not overriden by
		# server. ouch, this is not going to be nice.


	hitResultStrings = {
		CL_HIT: "hit",
		CL_DESPERATE: "desperate parry",
		CL_PARRY: "parry",
		CL_MISS: "miss",
		(1<<5) | 0: "slay",
		(1<<5) | 1: "break"
	}

	stancePartDict = {
		STANCE_NEUTRAL: "Mid",
		STANCE_BACKWARD: "Bak",
		STANCE_FORWARD: "Fwd",
		STANCE_LEFT: "Mid",
		STANCE_RIGHT: "Mid"
	}

	hitResultPartDict = {
		CL_MISS:		"Miss",
		CL_PARRY:		"Parry",
		CL_DESPERATE:	"Knock",
		CL_HIT:			"Hit"
	}

	# Play sounds and sparks
	def doFX(self, actionName):
		for soundAction in self.fxActionMap[actionName]:
			if soundAction[0][0] == "@":
				which = soundAction[0][1]
				f = None
				if which == 'S':
					# sparks
					if self.rightHandItem and self.rightHandItem.canSwing:
						f = self.rightHandItem.createSparks
				elif which == 'B':
					# blood
					f = partial( PSFX.attachBloodSpray, self.model,
						2,	# Direction, 1=left, 2=right
						5	# Number of blood sprays.
					)

				if f: BigWorld.callback( soundAction[1], f )
			else:
				if len(soundAction) == 3:
					pass 	# BigWorld.playFxDelayedAtten(soundAction[0], soundAction[1],
							# 					soundAction[2], self.position)
				else:
					pass # BigWorld.playFxDelayed(soundAction[0], soundAction[1], self.position)


	# Return the attacker's action to play based on this result from the server
	def ccActiveAction( self, res ):
		print "Attack result was", Avatar.hitResultStrings[res]

		if res & (1<<5):
			special = res & 7
			if special == 0:	# slay
				self.doFX( "CCActSlay" )
				return self.model.CCActSlay
			else:				# break
				self.ccBreaking = 1
				return self.model.CCActBreak

		prePart = "CCAct" + Avatar.stancePartDict[ self.stance ]

		defMove = res & 7
		actionName = prePart + Avatar.hitResultPartDict[ defMove ]

		self.doFX( actionName )

		return self.model.action( actionName )


	# Return the defender's action to play based on this result from the server
	def ccPassiveAction( self, res ):
		if res & (1<<5):
			special = res & 7
			if special == 0:	# slay
				self.causeOfDeath = Avatar.COD_SLAIN
				return None # self.model.CCPasSlay
				# We wait until we get told we're dead
			else:				# break
				return self.model.CCPasBreak

		prePart = "CCPas" + Avatar.stancePartDict[ self.stance ]

		defMove = res & 7
		actionName = prePart + Avatar.hitResultPartDict[ defMove ]

		self.doFX( actionName )

		return self.model.action( actionName )


	# Figure out an action based on the input stances (no longer used)
	def getCCAction( self, ownStance, othStance, ownTurn ):
		r = random.random()

		#print "getCCAction for", self.playerName, "ownStance", \
		#	ownStance, "othStance", othStance, "ownTurn", ownTurn

		if ownStance == 1:					# forward
			act = self.model.CCAttack3			# big attack
		elif ownStance == 0:				# backward
			if othStance != 0 and r < 0.5:
				act = self.model.CCParryL		# random parry
			else:
				act = self.model.CCParryR		# unless both defending
		else:								# neutral
			if othStance == 1:					# other forward
				if r < 0.5:							# random parry
					act = self.model.CCParryL
				else:
					act = self.model.CCParryR
			elif othStance == 0:				# other backward
				if r < 0.5:							# random attack
					act = self.model.CCAttack1
				else:
					act = self.model.CCAttack2
			else:								# other (both) neutral
				if ownTurn:							# our attack
					if r < 0.5:
						act = self.model.CCAttack1
					else:
						act = self.model.CCAttack2
				else:								# our defend
					if r < 0.5:
						act = self.model.CCParryL
					else:
						act = self.model.CCParryR

		return act


	stanceCapsDict = {
		STANCE_NEUTRAL: [8],
		STANCE_BACKWARD: [8,10],
		STANCE_FORWARD: [8,9],
		STANCE_LEFT: [8],
		STANCE_RIGHT: [8]
		}

	# The stance property has been set
	def set_stance( self, oldStance = None ):
		oldStance

		if self.mode != Mode.COMBAT_CLOSE: return

		#AUSTIN GDC - move all matchCaps into items
		#kept = filter( lambda c: c not in range(8,11), self.am.matchCaps )
		#
		#if self.healthPercent > 0:
		#	self.am.matchCaps = kept + Avatar.stanceCapsDict[ self.stance ]
		#else:	# We are dazed
		#	self.am.matchCaps = kept + [8,9,10]

	modelColours = (
		(1,1,1,1),	# white
		(1,1,0,1),	# yellow
		(1,0,1,1),	# magenta
		(0,1,1,1),	# cyan
		(1,0,0,1),	# red
		(0,1,0,1),	# green
		(0,0,1,1),	# blue
		(0,0,0,1),	# black
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1),	# grey
		(0.5,0.5,0.5,1)		# grey
	)		# other colours by request :)
	modelColourCount = 7

	# The colour property has been set
	def set_colour( self, oldColour = None ):
		pass
		#TO DO: implement colour changing
		#if self.colour == oldColour: return

		#try:		self.model.Legs.Colour = Avatar.modelColours[ self.colour & 15 ]
		#except:		pass
		#try:		self.model.Torso.Colour = Avatar.modelColours[ self.colour >> 4 ]
		#except:		pass

	DEAD_PENALTY = 10

	# Set dead state for all Avatars when dead.
	@IgnoreCallbackIfDestroyed
	def setDeadState( self, dyingAnimation = 1, delay = 0 ):
		if delay > 0:
			BigWorld.callback( 0.000001, partial( self.setDeadState, dyingAnimation, delay-1 ) )
			return
		self.inDeadState = 1
		self.waitingMode = -1

		self.disableAllTrackers()

		self.am.entityCollision = 0
		self.am.turnModelToEntity = 0

		self.setTargetCaps()

		# modeTarget is used to indicate how we died.
		# if silent take down, let the attack handle
		# the death animation
		if self.modeTarget == Avatar.COD_TAKEN_DOWN:
			return

		if self.model != None and self.model.inWorld:
			ntime = 0
			if self.causeOfDeath == Avatar.COD_SHOT:
				if dyingAnimation:
					da = self.model.Die
					da()
					ntime = da.duration-da.blendOutTime - 0.1
				de = self.model.Dead
				de( ntime )
				ntime += de.duration - de.blendOutTime
			else:	# COD_SLAIN
				if dyingAnimation:
					da = self.model.CCPasSlay
					da()
					ntime = da.duration-da.blendOutTime - 0.0001
				de = self.model.CCPasSlayDead
				de( ntime )
				ntime += de.duration - de.blendOutTime

			# align model to terrain
			self.filter = BigWorld.AvatarDropFilter()
			self.filter.alignToGround = True

			if hasattr( self, "am" ):
				self.am.useEntityPitchAndRoll = True
				self.am.turnModelToEntity = True
				self.am.bodyTwistSpeed = math.radians( 60.0 )

	# Becoming dead
	def enterDeadMode( self ):
		self.actionCommence()

		# Hide the model now if we are just entering the world,
		# and don't both with any of the teleportation effects
		# (which are highly likely to stuff up since they would be out of date)
		if self.worldTransition:
			self.setDeadState( 0 )	# no dying animation
			self.hideModel( True )
			return

		# Wait for causeOfDeath to be set... (twice through ticks since
		# enterDeadMode called from network input which is before callback
		# handling in game loop, and we need a frame to have been drawn)
		self.setDeadState( 1, 2 )

		# Set up the teleport out effect
		positionOffset = Vector3( 0.25, 0.00, 1.50 )
		cosYaw = math.cos( self.model.yaw )
		sinYaw = math.sin( self.model.yaw )
		positionOffset = Vector3( (
			positionOffset.x * cosYaw + positionOffset.z * sinYaw,
			positionOffset.y,
			positionOffset.z * cosYaw - positionOffset.x * sinYaw ) )
		ascendPoint = Vector3( self.position ) + positionOffset

		self.deathWarp = BigWorld.Model( "objects/models/fx/fx_deathwarp.model" )
		self.deathWarp.position = ascendPoint
		self.deathWarp.yaw = self.model.yaw

		BigWorld.callback( Avatar.DEAD_PENALTY + 3.0, self.beginTeleportation )
		FantasyDemo.firstPerson( False )
		FantasyDemo.resetCamera()

	def tryToTeleport( self, spaceName, pointName ):
		self.base.tryToTeleport( spaceName, pointName, self.spaceID )

	def teleportTo( self, spaceName, pointName ):
		TeleportSource.startTeleportation( spaceName, pointName )

	def addInfoMsg( self, msg ):
		FantasyDemo.addChatMsg( -1, msg )

	@IgnoreCallbackIfDestroyed
	def beginTeleportation( self ):
		if self.mode != Mode.DEAD:	return

		self.addModel( self.deathWarp )
		self.deathWarp.Go( 0, self.doTeleportation )

	@IgnoreCallbackIfDestroyed
	def doTeleportation( self ):
		if self.mode != Mode.DEAD:	return

		self.hideModel( True )
		self.deathWarp.Continue( 0, self.endTeleportation )

	@IgnoreCallbackIfDestroyed
	def endTeleportation( self ):
		if self.mode != Mode.DEAD:	return

		self.delModel( self.deathWarp )
		self.deathWarp = None
		self.am.matcherCoupled = 1


	def beginReincarnation( self ):
		if self.inWorld:
			dropPointPair = BigWorld.findDropPoint( self.spaceID, self.position )
			if dropPointPair == None:
				dropPoint = Vector3( self.position )
			else:
				dropPoint = dropPointPair[0]

			self.warp = BigWorld.Model( "objects/models/fx/fx_warp.model" )
			self.addModel( self.warp )
			self.warp.position = dropPoint
			self.warp.Go( 0, self.endReincarnation )

			# self.model.playSound( "spawnIn" )

			self.model.RespawnFall().RespawnLand()
			BigWorld.callback( self.model.RespawnFall.duration,
				self.respawnHitGround )

		BigWorld.callback( 0.25, partial( self.hideModel, False ) )

	@IgnoreCallbackIfDestroyed
	def respawnHitGround( self ):
		PSFX.attachRespawnMist( self.model )
		# TBD: Play sound here.


	def endReincarnation( self ):
		self.delModel( self.warp )
		self.warp = None

		self.actionComplete()


	# Helper function to disable all an Avatar's trackers
	def disableAllTrackers( self ):
		self.tracker.directionProvider = None

	# Helper function to enable specific tracker, called from guns.py
	def enableTracker( self, nodeInfo = None ):
		# this if test is temporary and should be removed
		# as soon as the beziel model get his skeleton fixed
		import Guard
		if isinstance(self, Guard.Guard):
			return

		if nodeInfo and not nodeInfo == self.tracker.nodeInfo:
			self.tracker.nodeInfo = nodeInfo
		if not self.tracker.directionProvider:
			self.tracker.directionProvider = self.entityDirProvider

	def unsetDeadState( self ):
		self.inDeadState = 0
		try:
			self.model.Dead.stop()
			self.model.CCPasSlayDead.stop()
		except AttributeError:
			pass
		self.causeOfDeath = Avatar.COD_SHOT
		self.am.entityCollision = 1
		self.am.matcherCoupled = 1
		self.filter = BigWorld.AvatarFilter()
		self.setTargetCaps()
		self.enableTracker()

	# Begin reincarnated
	def leaveDeadMode( self ):
		#Team.isDead( self.id, 0 )
		# remove the death warp (and interrupt its sequence) if it is still around
		if self.deathWarp != None:
			try:	self.delModel( self.deathWarp )
			except:	pass
			self.deathWarp = None

		# ok, now continue with the reincarnation
		self.unsetDeadState()

		if hasattr( self, "am" ):
			self.am.useEntityPitchAndRoll = False
			self.am.turnModelToEntity = False
			self.am.bodyTwistSpeed = math.radians( 360.0 )

		# reincarnate
		self.beginReincarnation()

	# Entering no mode
	def enterNoneMode( self ):
		pass

	# Leaving no mode
	def leaveNoneMode( self ):
		pass

	def onModelChangeUpdateMode( self ):
		# Called once the model has been set up correctly
		# go back into whatever mode we were in
		self.worldTransition = 1
		if( ModeTarget._isModeTargetReady( self ) ):
			self.enterMode( oldMode = Mode.NONE )
		else:
			ModeTarget._waitForModeTarget( self )
		self.worldTransition = 0

	# Going into any mode
	def enterMode( self, oldMode ):
		if self.mode == Mode.NONE:
			self.enterNoneMode()
			return

		assert not self._waitingForModeTarget

		if self.mode == Mode.SHONK:
			self.enterShonkMode()
		elif self.mode == Mode.HANDSHAKE:
			self.enterHandshakeMode()
		elif self.mode == Mode.PULLUP:
			self.enterPullUpMode();
		elif self.mode == Mode.PUSHUP:
			self.enterPushUpMode();
		elif self.mode == Mode.COMBAT_UNLOCKED:
			self.enterCombatMode(0, 0)
		elif self.mode == Mode.COMBAT_LOCKED:
			self.enterCombatMode(1, 0)
		elif self.mode == Mode.USING_ITEM:
			self.enterUsingItemMode()
		elif self.mode == Mode.CROUCH:
			self.enterCrouchMode()
		elif self.mode == Mode.SEATED:
			self.enterSeatedMode();
		elif self.mode == Mode.COMBAT_CLOSE:
			self.enterCloseCombatMode()
		elif self.mode == Mode.TRADE_PASSIVE:
			self.tradePassiveEnterMode()
		elif self.mode == Mode.TRADE_ACTIVE:
			self.tradeActiveEnterMode()
		elif self.mode == Mode.COMMERCE:
			self.commerceEnterMode()
		elif self.mode == Mode.DEAD:
			self.enterDeadMode()
		elif self.mode == Mode.WEB_SCREEN:
			pass
		else:
			print "Avatar::enterMode: In unknown mode ", self.mode

		if self.mode < Mode.ANSWERABLE:
			self.actionCommence()
			self.waitingMode = self.mode

	# Going out of any mode
	def cancelMode( self, oldMode ):
		if oldMode == Mode.NONE:
			self.leaveNoneMode()
			return

		if oldMode < Mode.ANSWERABLE:
			if self.waitingMode != -1:
				# wait for a bit to see if we're going to get a message with it
				BigWorld.callback( 0.5,
					partial( self.showModeCancellation, oldMode ) )
		elif oldMode == Mode.COMBAT_UNLOCKED:
			self.leaveCombatMode(0, 0)
		elif oldMode == Mode.COMBAT_LOCKED:
			self.leaveCombatMode(1, 0)
		elif oldMode == Mode.USING_ITEM:
			self.leaveUsingItemMode()
		elif oldMode == Mode.CROUCH:
			self.leaveCrouchMode()
		elif oldMode == Mode.SEATED:
			self.leaveSeatedMode()
		elif oldMode == Mode.COMBAT_CLOSE:
			self.leaveCloseCombatMode()
		elif oldMode == Mode.TRADE_PASSIVE:
			self.tradePassiveLeaveMode()
		elif oldMode == Mode.TRADE_ACTIVE:
			self.tradeActiveLeaveMode()
		elif oldMode == Mode.COMMERCE:
			self.commerceLeaveMode()
		elif oldMode == Mode.DEAD:
			self.leaveDeadMode()
		elif oldMode == Mode.WEB_SCREEN:
			pass
		else:
			print "Avatar::cancelMode: Out unknown mode ", oldMode

	# Play the cancellation animation
	@IgnoreCallbackIfDestroyed
	def showModeCancellation( self, mode ):
		if self.waitingMode == mode:
			if self.mode in Avatar.combativeModes:
				self.model.Disagree( 0, self.actionComplete )
			else:
				self.actionComplete()
			self.waitingMode = -1

	# Becoming a target
	def modeTargetFocus( self, other ):
		pass

	# Quitting as target
	def modeTargetBlur( self, player ):
		try:
			FantasyDemo.rds.fdgui.targetGui.source = None
		except AttributeError:
			pass

	# Some action has begun
	def actionCommence( self, combativeAction = 0 ):
		if not (self.rightHandItem and self.rightHandItem.canShoot):
			self.tracker.directionProvider = None

	# Some action is complete
	@IgnoreCallbackIfDestroyed
	def actionComplete( self ):
		#print "Avatar::actionComplete: Stopping action"
		if self.mode != Mode.SEATED and self.mode != Mode.DEAD:
			self.am.turnModelToEntity = 0
			self.am.matcherCoupled = 1
		if self.mode != Mode.DEAD:
			# tracker and entityDirProvider is only set once the model is loaded
			if hasattr( self, "tracker" ) and hasattr( self, "entityDirProvider" ):
				self.tracker.directionProvider = self.entityDirProvider
			try:
				self.tracker.directionProvider = self.entityDirProvider
			except AttributeError:
				pass


	# We got fragged!
	def fragged( self, shooterID ):
		e = BigWorld.entity( shooterID )
		if e != None:
			shname = e.name()
		else:
			shname = "An invisible monster"
		FantasyDemo.addChatMsg( self.id, shname + " fragged me!" )


	# Callback from tracking to get our name
	def name( self ):
		return self.playerName;


	def castSpell( self, targetid, hitLocn, materialKind ):
		try:
			self.currentSpell = self.rightHandItem.spell
		except:
			self.currentSpell = None

		if self.currentSpell != None:
			self.currentSpell.go( self, targetid, self.rightHandItem, hitLocn, materialKind )


	# Someone told us to shoot.
	def fireWeapon( self, shotid, lock ):
		if shotid == 0:
			lock = -1

		firePrep = None

		if lock == -1:
			fireBeg = self.model.CombatL0BeginFire
			fireExe = self.model.CombatL0ExecuteFire
			firePrep = self.model.CombatL0Blender
			movableShoot = 1
		else:
			fireBeg = self.model.CombatL1BeginFire
			fireExe = self.model.CombatL1ExecuteFire
			movableShoot = 1

		preparationTime = fireBeg.duration - fireBeg.blendOutTime
		# postTime = preparationTime + (fireExe.duration - fireExe.blendOutTime)

		if self.rightHandItem and self.rightHandItem.canShoot:
			self.rightHandItem.fire( self, preparationTime )

		fn = None
		if BigWorld.entities.has_key( shotid ):
			se = BigWorld.entity( shotid )
			if hasattr( se, "recoil" ):
				fn = partial( se.recoil, self, lock )

		if firePrep != None:
			firePrep.stop()
			self.enableTracker()
			# Commented out the following line when using ShootAir animation
			# as CombatL0 animation.
			#self.enableTracker( self.gunAimingNodeInfo )

		fireBeg( 0, fn )
		fireExe( -(preparationTime-0.01), partial( self.doneFire, firePrep ) )

		BigWorld.callback( 0.1, partial( self.model.playSound, "guns/fire" ) )

		return movableShoot


	# Called when we have finished a fire action.
	# If firePost is passed in, and we are still in combat
	# mode, then call the fn.
	def doneFire( self, firePost ):
		if self.isDestroyed:
			return
		BigWorld.callback( 0.5, self.doneFire2 )

		if firePost != None and self.mode == Mode.COMBAT_UNLOCKED:
			self.enableTracker( self.headNodeInfo )
			# Commented out the following line when using ShootAir animation
			# as CombatL0 animation.
			#self.gunAimingTracker.trackNothing()
			firePost()

	# Completely finished with firing now.
	# Call actionComplete, and turn off the gun aiming tracker if
	# we lost our target in the meantime
	@IgnoreCallbackIfDestroyed
	def doneFire2( self ):
		if self.isDestroyed:
			return
		self.actionComplete()

		# if we've lost our target since we began, we'd better
		# turn off the gun aiming tracker as targetBlur won't
		if self.mode != Mode.COMBAT_LOCKED:
			self.enableTracker( self.headNodeInfo );


	# We got shot at! (overriden by player)
	def recoil( self, shooter, lockAccuracy ):
		if lockAccuracy >= 1:
			# BigWorld.playFx( "players/grunts/hurt" , self.position )
			self.model.Recoil( -0.1 )
			self.recoilCommon( shooter, lockAccuracy )
		else:
			self.model.Recoil( -0.1 )
			self.recoilCommon( shooter, lockAccuracy )

	# Show the shield (not overriden by players)
	def recoilCommon( self, shooter, lockAccuracy ):
		dir = Vector3( shooter.position ) - Vector3( self.position )
		dir.normalise()

		if lockAccuracy >= 1:
			hitm = BigWorld.Model( "objects/models/fx/fx_shieldhit.model" )
		else:
			hitm = BigWorld.Model( "objects/models/fx/fx_shieldglance.model" )

		# BigWorld.playFx( "shield_hit", self.position )

		self.addModel( hitm )

		hitm.position = Vector3( self.position ) + dir.scale( 0.3 ) + Vector3(0,1.5,0)
		hitm.yaw = math.atan2( dir.x, dir.z )

		hitm.Go()
		BigWorld.callback( hitm.Go.duration, partial( self.delModel, hitm ) )

	# Shoot the target with a projectile
	def shootProjectile( self, target, projectileName ):
		# general settings
		srcoff = Vector3(0,1.5,0)
		dstoff = Vector3(0,1.2,0)
		projectile = BigWorld.Model(projectileName)
		self.addModel( projectile )
		projectile.position = self.position + srcoff
		mot = BigWorld.Homer()
		mot.target = target.model.matrix
		#mot.offset = dstoff
		mot.speed = 48
		mot.turnRate = 10

		# calculate the trip time based on the displacement
		disp = (Vector3(self.position)+srcoff) -	\
			(Vector3(target.model.position)+dstoff)
		sx = math.sqrt(disp.x*disp.x + disp.z*disp.z)
		sy = disp.y
		ay = -9.8
		U = mot.speed
		intercept = U*U*U*U - 2*U*U*sy*ay - ay*ay*sx*sx

		# if we can't make it, return now
		if intercept < 0:
			return

		tsq = (2.0/(ay*ay)) * (sy*ay - U*U + math.sqrt(intercept))
		t = math.sqrt(abs(tsq))
		mot.tripTime = t

		# rotate arrow to point in direction of initial velocity
		ux = sx/t
		uy = sy/t - 0.5*ay*t
		#print "ux is ", ux, " uy is ", uy
		projectile.rotate( math.atan2(uy,ux), (1,0,0) )
		projectile.yaw = math.atan2(disp.x,disp.z) + math.pi/2

		# and whack on the motor
		projectile.addMotor( mot )
		#self.addModel( projectile )

		# and whack on ye olde blur
		#particles.arrowBlur( projectile, mot.tripTime )
		PSFX.attachArrowTrace( projectile, None, mot.tripTime )

		# call us back when you get close enough
		mot.proximity = 0.5
		mot.proximityCallback = partial( self.clearProjectile, projectile )


	# Remove the specified projectile
	def clearProjectile( self, projectile ):
		self.delModel( projectile )


	# We're talking and the player heard us
	def chat( self, msg ):
		FantasyDemo.addChatMsg( self.id, msg )



	# We did a gesture and the player saw us
	def didGesture( self, actionID ):
		try:
			theAction = Avatar.gestureActions[actionID]
			if theAction.fn is not None:
				theAction.fn( self, theAction )
			else:
				self.model.action( theAction.actionName )( 0, self.actionComplete )
			if ( theAction.actionSound != "" ):
				pass # BigWorld.playFx( theAction.actionSound, self.position )
		except:
			self.actionComplete()


	# Server method telling us our shonk offer has been accepted
	def shonk( self, opponentID, oppAction, ownAction ):
		self.waitingMode = -1

		#print "Avatar::shonk: I performed %d, and Avatar %d performed %d." % (
		#	ownAction, opponentID, oppAction)

		# figure out what happened
		ownResult = ((3 + ownAction - oppAction) % 3)
		oppResult = ((3 + oppAction - ownAction) % 3)

		# figure out who our opponent is
		oppo = BigWorld.entity( opponentID )

		# Set camera to fixed position if the player is one of the Avatars
		# playing shonk.
		if self == BigWorld.player() or oppo == BigWorld.player():

			localCameraPos = Vector3( 1.25, 2.25, 0.75 )
			localCameraLookAt = Vector3( 0.00, 2.00, 0.75 )
			if self == BigWorld.player():
				target = self
			else:
				target = oppo

			( cameraPos, lookAtPos ) = self.calculateCameraView(
				target, localCameraPos, localCameraLookAt )

			FantasyDemo.setFixedCamera( cameraPos, lookAtPos )

		# start the game actions
		callback = CoordinatedActionPlayer( self, oppo,
			Avatar.shonkResultActionNames[ownResult],
			Avatar.shonkResultActionNames[oppResult] )

		selfEnd = partial( self.shonkComplete, ownAction, ownResult, callback )
		oppEnd = partial( oppo.shonkComplete, oppAction, oppResult, callback )

		self.model.action( Avatar.shonkPlayActionNames[ownAction] )( 0, selfEnd )
		oppo.model.action( Avatar.shonkPlayActionNames[oppAction] )( 0, oppEnd )

	def shonkComplete( self, action, result, callback ):
		if self == BigWorld.player():

			if result == 0:
				FantasyDemo.addChatMsg( -1, "It is a draw!" )
			else:
				if result == 1:
					FantasyDemo.addChatMsg( -1, "You win!" )
					if action == 0:
						FantasyDemo.addChatMsg( -1, "Paper wraps Rock" )
					elif action == 1:
						FantasyDemo.addChatMsg( -1, "Scissors cuts Paper" )
					else:
						FantasyDemo.addChatMsg( -1, "Rock blunts Scissors" )
				else:
					FantasyDemo.addChatMsg( -1, "You lose!" )
					if action == 0:
						FantasyDemo.addChatMsg( -1, "Scissors cuts Paper" )
					elif action == 1:
						FantasyDemo.addChatMsg( -1, "Rock blunts Scissors" )
					else:
						FantasyDemo.addChatMsg( -1, "Paper wraps Rock" )

			FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
		callback()


	# Calculates the position and lookAtPos for the camera given a relative
	# camera and lookAt position to an Entity.
	#
	# Returns a pair with the first element being the world camera position;
	# and the second element being the world camera lookAt position.
	def calculateCameraView( self, entity, cameraPos, lookAtPos ):
		sinYaw = math.sin( entity.model.yaw )
		cosYaw = math.cos( entity.model.yaw )

		worldPos = Vector3( entity.position ) + Vector3( (
			cameraPos.x * cosYaw + cameraPos.z * sinYaw,
			cameraPos.y,
			cameraPos.z * cosYaw - cameraPos.x * sinYaw ) )

		worldLookAt = Vector3( entity.position ) + Vector3( (
			lookAtPos.x * cosYaw + lookAtPos.z * sinYaw,
			lookAtPos.y,
			lookAtPos.z * cosYaw - lookAtPos.x * sinYaw ) )

		return ( worldPos, worldLookAt )

	# -------------------------------------------------------------------------
	# Section: Handshake
	# -------------------------------------------------------------------------

	# Server method telling us our handshake offer has been accepted
	def handshake( self, partnerID ):
		self.waitingMode = -1

		partner = BigWorld.entity( partnerID )
		if self.mode == Mode.HANDSHAKE:
			print "Shaking hands with " + partner.name()
		else:
			print "Avatar.handshake() called from unknown mode"
			return

		# These seem to make it look worse.
		# set our yaw to what the other client must think it is
		# given the position it's gone to.
		#self.am.turnModelToEntity = 0
		#print "Our yaw set to: ", partner.model.Shake_B_Accept.seek[3]
		#self.model.yaw = partner.model.Shake_B_Accept.seek[3]
		# set our partners yaw to what it should be explicitly
		#partner.am.turnModelToEntity = 0
		#print "Our partner's yaw set to: ", self.model.Shake_B_Accept.seekInv[3]
		#partner.model.yaw = self.model.Shake_B_Accept.seekInv[3]

		# Set camera to fixed position if the player is doing the handshake.
		if self == BigWorld.player() or partner == BigWorld.player():

			localCameraPos = Vector3( 1.25, 2.25, 0.75 )
			localCameraLookAt = Vector3( 0.00, 2.00, 0.75 )
			if self == BigWorld.player():
				target = self
			else:
				target = partner

			( cameraPos, lookAtPos ) = self.calculateCameraView(
				target, localCameraPos, localCameraLookAt )

			BigWorld.target.clear()
			FantasyDemo.setFixedCamera( cameraPos, lookAtPos )

		if partner != BigWorld.player():
			partner.actionCommence()

		self.disableAllTrackers()
		partner.disableAllTrackers()

		sbe = partner.model.Shake_B_Extend
		sbe().Shake_B_Accept( 0, partner.handshakeComplete )
		self.model.Shake_A_Accept( sbe.duration, self.handshakeComplete )


	def handshakeComplete( self ):
		if self == BigWorld.player():
			FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
		self.actionComplete()


	# Server method telling us our pull up offer has been accepted
	def pullUp( self, partnerID ):
		self.waitingMode = -1

		partner = BigWorld.entity( partnerID )
		print "Avatar::pullUp: Pulling up ", partner.name()

		partner.am.matcherCoupled = 0
		# commented out because it turns the model away from the wall if the player has moved the mouse
		#partner.model.yaw = partner.yaw

		# At this point we have a choice. We can either leave our partner's
		#  pose set to what it thinks it should be, and play the animation
		#  with the possibility of hands not exactly meeting up, or we can
		#  set it to what we know looks good, and experience a pop in its
		#  pose when we recouple the action matcher. Since the hands usually
		#  match up reasonably well, I'm leaving it at what it thinks is
		#  right for now. These differences arise primary due to the
		#  resolution of 'yaw', which is not great. Another possibility is
		#  that higher resolution yaws could be passed up with the state
		#  change and with this message.				John 7/6/01 {P^/
		#pose = self.model.PullUpActiveBegin.seek
		#partner.model.position = pose[0:3]
		#partner.model.yaw = pose[3]


		# Set camera to fixed position if the player is involved.
		if self == BigWorld.player() or partner == BigWorld.player():
			localCameraPos = Vector3( -1.50, 2.00, 2.50 )
			localCameraLookAt = Vector3( 0.00, -2.50, 0.50 )

			( cameraPos, lookAtPos ) = self.calculateCameraView(
				self, localCameraPos, localCameraLookAt )

			#BigWorld.fixedCameraPos( cameraPos.x, cameraPos.y, cameraPos.z )
			#BigWorld.fixedCameraLookAt( lookAtPos.x, lookAtPos.y, lookAtPos.z )
			#FantasyDemo.cameraType( FantasyDemo.rds.FIXED_CAMERA )

		if partner == BigWorld.player():
			partner.am.inheritOnRecouple = 0
			partner.physics.teleport( partner.model.PullUpPassiveImpact.impact[0:3] )
		else:
			partner.actionCommence()	# player has already commenced

		pupb = partner.model.PullUpPassiveBegin;
		pupb().PullUpPassiveAccept( 0, partner.pullUpEndPartner ).Idle()

		aftertime = pupb.duration - pupb.blendOutTime - 0.001
		self.model.PullUpActiveAccept( aftertime, self.pullUpEnd )

	def pullUpEnd( self ):
		if self == BigWorld.player():
			FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
		self.model.Idle.stop()
		self.actionComplete()

	def pullUpEndPartner( self ):
		if self == BigWorld.player():
			FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
		self.model.Idle.stop()
		self.actionComplete()

	# Server method telling us our push up offer has been accepted
	def pushUp( self, partnerID ):
		self.waitingMode = -1

		partner = BigWorld.entity( partnerID )
		print "Avatar::pushUp: Pushing up ", partner.name()


		partner.am.matcherCoupled = 0
		# commented out because it turns the model away from the wall if the player has moved the mouse
		#partner.model.yaw = partner.yaw

		# we have to move up 5cm here because the two animations together
		# don't _quite_ provide enough lift for us :)
		pmp = partner.model.position
		partner.model.position = pmp[0], pmp[1] + 0.05, pmp[2]

		if self == BigWorld.player(): sname = "Player"
		else: sname = "Initer"
		#~ print sname, " entity position: " , self.position, ", yaw: ", self.yaw
		#~ print sname, " model  position: " , self.model.position, ", yaw: ", self.model.yaw
		if partner == BigWorld.player(): sname = "Player"
		else: sname = "Partnr"
		#~ print sname, " entity position: " , partner.position, ", yaw: ", partner.yaw
		#~ print sname, " model  position: " , partner.model.position, ", yaw: ", partner.model.yaw


		# Set camera to fixed position if the player is involved.
		if self == BigWorld.player() or partner == BigWorld.player():
			localCameraPos = Vector3( -2, 8, 1.5 )
			localCameraLookAt = Vector3( 1, -4.5, 2 )

			( cameraPos, lookAtPos ) = self.calculateCameraView(
				self, localCameraPos, localCameraLookAt )

			#BigWorld.fixedCameraPos( cameraPos.x, cameraPos.y, cameraPos.z )
			#BigWorld.fixedCameraLookAt( lookAtPos.x, lookAtPos.y, lookAtPos.z )
			#FantasyDemo.cameraType( FantasyDemo.rds.FIXED_CAMERA )

		if partner == BigWorld.player():
			#partner.am.inheritOnRecouple = 0

			dir = Vector3( math.sin(partner.yaw), 0, math.cos(partner.yaw) )
			#dist = Vector3(partner.model.PushUpPassiveAccept.displacement) + \
			#	Vector3(partner.model.PushUpPassiveComplete.displacement);
			dist = Vector3( 0, 5.1, 1.35 )		# don't ask :)
			newPos = Vector3( partner.position ) + dir.scale( dist.z )
			newPos.y = newPos.y + dist.y
			partner.physics.teleport( newPos )
			# this isn't perfect, but it will do :)

			# or try adding impacts... hmmm...
		else:
			partner.actionCommence()


		self.model.PushUpActiveAccept( 0, self.pushUpEnd ).Idle()
		partner.model.PushUpPassiveAccept().PushUpPassiveComplete(
			0, partner.pushUpEndPartner ).Idle()

	def pushUpEndPartner( self ):
		if self == BigWorld.player():
			FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
		self.model.Idle.stop()
		self.actionComplete()

	def pushUpEnd( self ):
		if self == BigWorld.player():
			FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
		self.model.Idle.stop()
		self.actionComplete()


	# The player wants to use us
	def use( self ):
		# See if we are in a mode then
		player = BigWorld.player()
		if self.mode == Mode.SHONK:
			# should put up a menu (stays until focus lost?) asking how
			# the player wants to reply... hmmm need to think about this
			player.shonkKey( random.randrange( 3 ) )
		elif self.mode == Mode.HANDSHAKE:
			player.handshakeKey()
		elif self.mode == Mode.PULLUP:
			player.pullUpKey()
		elif self.mode == Mode.PUSHUP:
			player.pushUpKey()
		elif self.mode == Mode.JOIN_GROUP:
			player.answerJoinGroup( self )
		elif self.mode in ( Mode.THROW, Mode.THROW_CROUCHED ):
			player.catchKey( self )
		elif self.mode in ( Mode.CATCH, Mode.CATCH_CROUCHED ):
			player.throwKey( self )
		elif self.mode == Mode.TRADE_PASSIVE:
			player.onTradeKey()

	# Seperated from the above so the right trigger doesn't heal other players
	def useFromWhiteButton( self ):
		if isinstance(player.rightHandItem, Reviver) or isinstance(player.rightHandItem, Medipack):
			player.rightHandItem.use( player, self )


	# Some class-static data definitions

	simpleModelName = "characters/avatars/base/base.model"

	shonkPlayActionNames = [ "ShonkPaper", "ShonkScissors", "ShonkRock" ]
	shonkResultActionNames = [ "Shrug", "ShonkWin", "ShonkLose" ]

	#
	#---------------------------------------------------------------------------


	gestureActions = {
		0 :GestureAction("ShooAway",		0,	1),
		1 :GestureAction("OneHandedWave",	1,	0),
		2 :GestureAction("TwoHandedWave",	1,	0),
		3 :GestureAction("Cry",				0,	0),
		4 :GestureAction("Shrug",			1,	1),
		5 :GestureAction("ShonkWin",		0,	1),
		6 :GestureAction("ShonkLose",		0,	0),
		7 :GestureAction("ShonkPaper",		0,	0),
		8 :GestureAction("ShonkScissors",	0,	0),
		9 :GestureAction("ShonkRock",		0,	0),
		10:GestureAction("FoldArms",		0,	0),
		11:GestureAction("CatchBreath",		0,	0),
		12:GestureAction("HeavyBreathing",	0,	0),
		13:GestureAction("WatchItWarning",	1,	0),
		14:GestureAction("WhoMe",			0,	0),
		15:GestureAction("StopWarning",		1,	1),
		16:GestureAction("Laugh",			1,	1),
		17:GestureAction("HeavyLaugh",		0,	0),
		18:GestureAction("BeckonTaunt",		0,	1),
		19:GestureAction("Agree",			0,	1),
		20:GestureAction("Disagree",		0,	1),
		21:GestureAction("SubtleBeckon",	1,	1),
		22:GestureAction("FranticBeckon",	0,	1),
		23:GestureAction("KissMyAssTaunt",	0,	0),
		24:GestureAction("Point",			0,	1),
		25:GestureAction("PointToSelf",		0,	0),
		26:GestureAction("PointWarning",	0,	1),
		27:GestureAction("Ponder",			0,	0),
		28:GestureAction("RudeGesture",		0,	0),
		29:GestureAction("GiveUp",			0,	1),
		30:GestureAction("FaceRoar",		1,	1, "orc_roar"),
		31:GestureAction("RaiseSword",		0,	1),
		32:GestureAction("HeadStretch",	0,	0),
		33:GestureAction("Troller",	0,	0),
		34:GestureAction("TeamJoinAccept", 0, 1),
		35:GestureAction("Jump",	0,	1),
		36:GestureAction("PressPalm",	0,	0),
		37:GestureAction("GoGoGo",	0,	0),
		38:GestureAction("GetDown",	0,	0),
		39:GestureAction("MoveUp",	0,	0),
		40:GestureAction("Salute",	0,	0),
		41:GestureAction("Shhhh",	0,	0),
		42:GestureAction("PointLeft",	0,	0),
		43:GestureAction("PointRight",	0,	0),
		44:GestureAction("Fat",	1,	1),
		45:GestureAction("Skinny",	1,	1),
		46:GestureAction("SwingSword",	1,	1, "", swordSwingGesture),
	}

	# This sets the target focal node for this entity,
	#  for either normal (-1), loose combat (0),
	#  tight combat (1), or take down (2) focus
	def setFocalNode( self, tight = None ):
		if tight == None:
			tight = self.tightFocus
		else:
			self.tightFocus = tight

		if tight == -1:
			self.focalMatrix.a = self.model.node( "biped Head" )
		elif tight == 0:
			self.focalMatrix.a = self.model.node( "biped Spine1" )
		elif tight == 1:
			self.focalMatrix.a = self.model.node( "biped Head" )
		elif tight == 2:
			self.focalMatrix.a = self.model.node( "biped Head" )
		else:
			self.focalMatrix.a = self.model.node( "biped Head" )

	def notLoggedOn( self, playerName ):
		FantasyDemo.addChatMsg( -1, playerName + " is not logged on" )

	# -------------------------------------------------------------------------
	# Friends list
	# -------------------------------------------------------------------------

	# Helper method to get the target player name if friendName is empty
	def getTargetForFriendlyAction( self, friendName ):
		if len( friendName ):
			return friendName

		target = BigWorld.target()
		if target != None and isinstance(target, Avatar):
			return target.playerName

		else:
			FantasyDemo.addChatMsg( -1, \
				"Please specify friend name or have friend targetted." )
			return ""


	# Helper method to find the index of friendName in self.friendsList
	def getFriendIdxByName( self, friendName ):
		for i in range( len( self.friendsList ) ):
			if self.friendsList[i][0] == friendName:
				return i
		return -1

	def newFriendsList( self, friendsList ):
		self.friendsList = [ ( x, False ) for x in friendsList ]

	def setFriendStatus( self, idx, isOnline ):
		friend = self.friendsList[idx]
		self.friendsList[idx] = ( friend[0], isOnline )
		self.onFriendPresence( friend[0], isOnline )


	def onFriendPresence( self, friend, isOnline ):
		if friend.find( "@" ) != -1:
			friend += "[IM]"

		if isOnline:
			FantasyDemo.addChatMsg(	-1, friend + " is online.",
					FDGUI.TEXT_COLOUR_ONLINE )
		else:
			FantasyDemo.addChatMsg(	-1, friend + " has logged off.",
					FDGUI.TEXT_COLOUR_OFFLINE )


	def addFriend( self, friendName ):
		targetFriendName = self.getTargetForFriendlyAction( friendName )

		if not len( targetFriendName ):
			return

		idx = self.getFriendIdxByName( targetFriendName )
		if idx < 0:
			self.base.addFriend( targetFriendName )
		else:
			FantasyDemo.addChatMsg( -1, targetFriendName +
				" is already your friend." )


	def onAddedFriend( self, friendName, online ):
		self.friendsList.append( ( friendName, online ) )
		FantasyDemo.addChatMsg( -1, friendName + " is your new friend." )


	def delFriend( self, friendName ):
		targetFriendName = self.getTargetForFriendlyAction(friendName)

		if len(targetFriendName) > 0:
			idx = self.getFriendIdxByName(targetFriendName)

			if idx >= 0:
				del self.friendsList[idx]
				self.base.delFriend(idx)
				FantasyDemo.addChatMsg( -1, targetFriendName +
					" is no longer your friend." )

			else:
				FantasyDemo.addChatMsg( -1, targetFriendName +
					" is not currently one of your friends." )


	def infoFriend( self, friendName ):
		targetFriendName = self.getTargetForFriendlyAction(friendName)

		if len(targetFriendName) > 0:
			idx = self.getFriendIdxByName(targetFriendName)

			if idx >= 0:
				self.base.getFriendInfo(idx)
			else:
				FantasyDemo.addChatMsg( -1, targetFriendName +
					" is not one of your friends." )


	def onRcvFriendInfo( self, friendName, info ):
		FantasyDemo.addChatMsg( -1, info )


	def displayFriendsList( self, onlineFriends, offlineFriends, friendsType ):

		totalFriends = len( onlineFriends ) + len( offlineFriends )

		msg = "%d of %d %s friends online:" % \
					( len( onlineFriends ), totalFriends, friendsType )
		FantasyDemo.addChatMsg( -1, msg )

		if len( onlineFriends ):
			msg = "   online: " + ", ".join( onlineFriends )
			FantasyDemo.addChatMsg( -1, msg, FDGUI.TEXT_COLOUR_ONLINE )

		if len( offlineFriends ):
			msg = "   offline: " + ", ".join( offlineFriends )
			FantasyDemo.addChatMsg( -1, msg, FDGUI.TEXT_COLOUR_OFFLINE )


	def listFriends( self ):

		# In-game friends
		onlineFriends = [ name for (name, online) in self.friendsList
							if online ]
		offlineFriends = [ name for (name, online) in self.friendsList
							if not online ]

		self.displayFriendsList( onlineFriends, offlineFriends, "in-game" )

		# Instant Messaging friends
		friendsDict = self.roster.friendsByStatus()

		offlineFriends = friendsDict.get( "unavailable", [] )

		# Combine any friends that aren't offline into the online group
		onlineFriends = []
		for presence in friendsDict.keys():
			if presence == "unavailable":
				continue

			onlineFriends.extend( friendsDict[ presence ] )

		self.displayFriendsList( onlineFriends, offlineFriends, "IM" )


	def msgFriend( self, friendName, message ):
		targetFriendName = self.getTargetForFriendlyAction(friendName)

		if len(targetFriendName) > 0:
			idx = self.getFriendIdxByName(targetFriendName)
			if idx >= 0:
				self.base.sendMessageToFriend( idx, message )
			else:
				FantasyDemo.addChatMsg( -1, targetFriendName +
					" is not one of your friends." )

	def onReceiveMessageFromAdmirer( self, admirerName, message ):
		FantasyDemo.addChatMsg( -1, admirerName + " says to you: " + message, 2 )


	# We received a message
	def showMessage( self, type, source, msg ):
		FantasyDemo.addChatMsg( -1,
			( "Debug", "Tell", "Group", "Info" )[type] + " - " + source + ": " + msg )


	# Dummy methods used in bots testing
	def loadGenMeth1( self, strArg ): pass
	def loadGenMeth2( self, intArg, strArg ): pass
	def loadGenMeth3( self, floatArg1, floatArg2, floatArg3 ): pass
	def loadGenMeth4( self, arrayArg ): pass

	def summonEntity( self, typeName, properties ):

		positionOffset = Vector3( 0.0, 0.00, 1.50 )
		cosYaw = math.cos( self.model.yaw )
		sinYaw = math.sin( self.model.yaw )
		positionOffset = Vector3( (
			positionOffset.x * cosYaw + positionOffset.z * sinYaw,
			positionOffset.y,
			positionOffset.z * cosYaw - positionOffset.x * sinYaw ) )

		direction = positionOffset
		position = Vector3( self.position ) + positionOffset
		spaceID = self.spaceID

		properties['position'] = position
		properties['direction'] = direction
		properties['spaceID'] = spaceID
		
		entityID = 0
		try:
			entityID = BigWorld.createEntity(
				typeName, spaceID, 0, position, direction, properties )
		except:
			pass

		self.entitySummoned( entityID, typeName )

		return entityID

	def entitySummoned( self, id, typeName ):
		if id != 0:
			FantasyDemo.addChatMsg( -1, "Summoned " + typeName + " id:" + str( id ) )
		else:
			FantasyDemo.addChatMsg( -1, "Failed to summon entity of type: " + typeName )


	def findOwnCellBounds( self ):
		p = self.position
		i = 0
		while i < len(self.cellBounds):
			blX = self.cellBounds[i+0]
			blY = self.cellBounds[i+1]
			trX = self.cellBounds[i+2]
			trY = self.cellBounds[i+3]
			i += 4

			if blX <= p.x and p.x <= trX:
				if blY <= p.z and p.z <= trY:
					return (blX,blY,trX,trY)
		return None


	def set_cellBounds( self, oldCellBounds ):
		try:
			FantasyDemo.rds.fdgui.minimap.m.cellBounds = self.cellBounds
		except:
			#python cellBounds attribute may be compiled out
			pass

		self.setupCellBoundsModel()


	def setupCellBoundsModel( self ):
		ownCellBounds = self.findOwnCellBounds()

		if self.cellBoundsModel is None:
			return

		if not self.showCellBoundsModel or ownCellBounds is None:
			self.cellBoundsModel.visible = False
			return

		# cant handle float max so clamp to smaller value
		clampedCellBounds = []
		clampedCellBounds.append( min( 1000.0 + self.position[0], max( -1000.0 + self.position[0], ownCellBounds[0] ) ) )
		clampedCellBounds.append( min( 1000.0 + self.position[2], max( -1000.0 + self.position[2], ownCellBounds[1] ) ) )
		clampedCellBounds.append( min( 1000.0 + self.position[0], max( -1000.0 + self.position[0], ownCellBounds[2] ) ) )
		clampedCellBounds.append( min( 1000.0 + self.position[2], max( -1000.0 + self.position[2], ownCellBounds[3] ) ) )

		sizeX = clampedCellBounds[2] - clampedCellBounds[0]
		sizeY = 2000.0
		sizeZ = clampedCellBounds[3] - clampedCellBounds[1]

		centerX = ( clampedCellBounds[2] + clampedCellBounds[0] ) / 2
		centerY = 0
		centerZ = ( clampedCellBounds[3] + clampedCellBounds[1] ) / 2

		self.cellBoundsModel.scale = ( sizeX, sizeY, sizeZ )
		self.cellBoundsModel.position = ( centerX, centerY, centerZ )
		self.cellBoundsModel.visible = True


	def inWebScreenMode( self ):
		return self.mode == Mode.WEB_SCREEN

# End of class Avatar

# static function to parse folders and add files to the preload list
def addFolderToPreloads( folder, mask, list ):
	if ".svn" in folder:
		return

	# avoid getting the data section for file extensions we don't care about
	# as just getting a sectin actually loads the file
	fileIndex = folder.rfind( '/' )
	if fileIndex != -1:
		fileIndex = fileIndex + 1
	else:
		fileIndex == 0

	extIndex = folder.rfind( '.', fileIndex )
	if extIndex != -1 and not folder.endswith( mask, extIndex ):
		#print( "Skipping filename=%s ext=%s mask=%s" % (folder[fileIndex:], folder[extIndex:], mask) )
		return

	section = ResMgr.root[ folder ]
	if section == None:
		return

	for key in section.keys():
		done = False
		if key.endswith( mask ):
			list.append( folder + '/' + key )
			done = True
			#print "Adding to preloads: " + folder + '/' + key + " " + mask
		if not done:
			addFolderToPreloads( folder + '/' + key, mask, list )


# static function to append models to preload onto 'list'
def preload( list ):
	preLoadList = []

	preLoadList.append( "scripts/" )

	# Manually add all lens flare bitmaps.  At the very least we should extend
	# the prereqs / preload system to know about mfm files.

	# BigWorld ones
	#preLoadList.append( "system/maps/fx_flare_glow.dds" )
	#preLoadList.append( "system/maps/fx_lens_sec.bmp" )

	# FantasyDemo ones
	#preLoadList.append( "maps/fx/fx_flare_glow.bmp" )
	#preLoadList.append( "maps/fx/flare_glow.bmp" )
	#preLoadList.append( "maps/fx/flare_halo.bmp" )
	#preLoadList.append( "maps/fx/flare_rainbow.bmp" )
	#preLoadList.append( "maps/fx/lens_sec.bmp" )
	#preLoadList.append( "maps/fx/mask_flare.bmp" )
	#preLoadList.append( "maps/fx/flare_trees.bmp" )
	preLoadList.append( "maps/fx/fx_swish.bmp" )

	# Add game metadata XML files to preload list.  Note these should not
	# be preloaded, but instead statically bound as python data
	addFolderToPreloads( "sfx", ".xml", preLoadList )
	addFolderToPreloads( "system/post_processing/chains", ".ppchain", preLoadList )
	#addFolderToPreloads( "particles", ".xml", preLoadList )
	#addFolderToPreloads( "sets/desert/particles", ".xml", preLoadList )
	addFolderToPreloads( "scripts/data", ".xml", preLoadList )
	addFolderToPreloads( "environments/fx", ".xml", preLoadList )

	# Add lens flare XML files to preload list.
	addFolderToPreloads( "materials/fx", ".mfm", preLoadList )
	addFolderToPreloads( "environments/fx", ".xml", preLoadList )
	addFolderToPreloads( "system/materials", ".mfm", preLoadList )


	# Add fx files
	#addFolderToPreloads( "shaders/std_effects", ".fx", preLoadList )


	list += preLoadList
	#print list

import ResMgr

# This function loads and parses the XML file describing all the
# ways in which player supermodels can be constructed,
# and stores the result in the global variable AvatarModels.
def buildAvatarModels( cclass = None ):
	global AvatarModels
	AvatarModels = ResMgr.openSection( "scripts/client/AvatarModels.xml" )

	good = 0
	try:
		amp = ResMgr.openSection( "scripts/client/AvatarModelPresets.xml" )
		if not cclass or not amp.has_key( cclass ):	cclass = "presets"
		Avatar.modelPresets = eval( amp.readString( cclass ) )
		good = (type(Avatar.modelPresets) == type([]))
	except:
		pass
	if not good: Avatar.modelPresets = []

buildAvatarModels()


# Return a model from the given model number
def makeModel( num, oldModel ):
	#print "makeModel(",num,")"
	global AvatarModels

	mnames = []
	dspecs = {}
	# use the bottom n values of num at each stage

	# first decide which skeleton
	skelsec = AvatarModels
	skelcount = len(skelsec)
	skelid = num % skelcount
	num = (num-skelid) / skelcount
	skel = AvatarModels.values()[ skelid ]

	#print " skelid", skelid

	# now for each of the parts:
	for partsec in skel.values():

		# decide which model variation to use
		partcount = len(partsec)
		partid = num % partcount
		num = (num-partid) / partcount
		part = partsec.values()[ partid ]
		mnames.append( part.asString )

		#print "  part", partsec.name, partid

		# and for each of its matters:
		for tintsec in part.values():

			# decide what tint to use
			tintcount = len(tintsec) + 1
			tintid = num % tintcount
			num = (num-tintid) / tintcount
			if tintid > 0:
				tint = tintsec.keys()[ tintid-1 ]
			else:
				tint = ""
			dspecs[ tintsec.name ] = tint

			#print "   tint", tintsec.name, tintid

	# make the model
	#print "mnames: ", mnames
	if oldModel != None and oldModel.sources == tuple(mnames):
		m = oldModel
	else:
		m = BigWorld.Model( *mnames )

	# apply any dyes
	#print "dspecs: ", dspecs
	for dye in dspecs.items():
		setattr( m, dye[0], dye[1] )

	# and that's it
	return m


# Return a tree describing all model combinations
# A node in the tree is a list of choices which must be made at that
# node. The elements of the list are either tuples of more tree nodes
# or a number that must be selected.
def treeModelNumbers():
	global AvatarModels

	tr = []			# tuple => choose one of these
	for skel in AvatarModels.values():
		ts = []			# list => choose in each of these
		for partsec in skel.values():
			tps = []		# tuple => choose one of these
			for part in partsec.values():
				tp = []			# list => choose in each of these
				for tintsec in part.values():
					tt = len(tintsec)+1	# int => choose one of these
					tp.append( tt )
				tps.append( tp )
			ts.append( tuple(tps) )
		tr.append( ts )
	return [tuple(tr)]


# Return a list of all valid model numbers
def listModelNumbers():
	return listModelNode( treeModelNumbers() )

# Return a list of valid model numbers from this node
def listModelNode( node ):
	if node == []: return [0]

	b = []

	# go over all the elts in the list, and add them to b
	for elt in node:
		l = []

		# see if it's a tuple
		if type(elt) == type((0,)):
			lenelt = len(elt)
			for ei in range(lenelt):
				for i in listModelNode( elt[ei] ):
					l.append( ei + lenelt * i )
		# it must be an integer
		else:
			l = range(elt)

		b.append( l )

	# now flatten our list of numbers, by zipping it up
	nums = [0]
	for i in range( len(b)-1, -1, -1 ):
		nn = []
		for j in b[i]:
			for val in nums:
				nn.append( j + len(b[i]) * val )
		nums = nn

	return nums


def create():
	player = BigWorld.player()
	return BigWorld.createEntity('Avatar', player.spaceID, 0, player.position, (0,0,0), {})

import ResMgr

# This function loads and parses the XML file describing all the
# ways in which player supermodels can be constructed,
# and stores the result in the global variable AvatarModels.
def buildAvatarModels( cclass = None ):
	global AvatarModels
	AvatarModels = ResMgr.openSection( "scripts/client/AvatarModels.xml" )

	good = 0
	try:
		amp = ResMgr.openSection( "scripts/client/AvatarModelPresets.xml" )
		if not cclass or not amp.has_key( cclass ):	cclass = "presets"
		Avatar.modelPresets = eval( amp.readString( cclass ) )
		good = (type(Avatar.modelPresets) == type([]))
	except:
		pass
	if not good: Avatar.modelPresets = []

buildAvatarModels()


# Return a model from the given model number
def makeModel( num, oldModel ):
	#print "makeModel(",num,")"
	global AvatarModels

	mnames = []
	dspecs = {}
	# use the bottom n values of num at each stage

	# first decide which skeleton
	skelsec = AvatarModels
	skelcount = len(skelsec)
	skelid = num % skelcount
	num = (num-skelid) / skelcount
	skel = AvatarModels.values()[ skelid ]

	#print " skelid", skelid

	# now for each of the parts:
	for partsec in skel.values():

		# decide which model variation to use
		partcount = len(partsec)
		partid = num % partcount
		num = (num-partid) / partcount
		part = partsec.values()[ partid ]
		mnames.append( part.asString )

		#print "  part", partsec.name, partid

		# and for each of its matters:
		for tintsec in part.values():

			# decide what tint to use
			tintcount = len(tintsec) + 1
			tintid = num % tintcount
			num = (num-tintid) / tintcount
			if tintid > 0:
				tint = tintsec.keys()[ tintid-1 ]
			else:
				tint = ""
			dspecs[ tintsec.name ] = tint

			#print "   tint", tintsec.name, tintid

	# make the model
	#print "mnames: ", mnames
	if oldModel != None and oldModel.sources == tuple(mnames):
		m = oldModel
	else:
		m = BigWorld.Model( *mnames )

	# apply any dyes
	#print "dspecs: ", dspecs
	for dye in dspecs.items():
		setattr( m, dye[0], dye[1] )

	# and that's it
	return m


# Return a tree describing all model combinations
# A node in the tree is a list of choices which must be made at that
# node. The elements of the list are either tuples of more tree nodes
# or a number that must be selected.
def treeModelNumbers():
	global AvatarModels

	tr = []			# tuple => choose one of these
	for skel in AvatarModels.values():
		ts = []			# list => choose in each of these
		for partsec in skel.values():
			tps = []		# tuple => choose one of these
			for part in partsec.values():
				tp = []			# list => choose in each of these
				for tintsec in part.values():
					tt = len(tintsec)+1	# int => choose one of these
					tp.append( tt )
				tps.append( tp )
			ts.append( tuple(tps) )
		tr.append( ts )
	return [tuple(tr)]


# Return a list of all valid model numbers
def listModelNumbers():
	return listModelNode( treeModelNumbers() )

# Return a list of valid model numbers from this node
def listModelNode( node ):
	if node == []: return [0]

	b = []

	# go over all the elts in the list, and add them to b
	for elt in node:
		l = []

		# see if it's a tuple
		if type(elt) == type((0,)):
			lenelt = len(elt)
			for ei in range(lenelt):
				for i in listModelNode( elt[ei] ):
					l.append( ei + lenelt * i )
		# it must be an integer
		else:
			l = range(elt)

		b.append( l )

	# now flatten our list of numbers, by zipping it up
	nums = [0]
	for i in range( len(b)-1, -1, -1 ):
		nn = []
		for j in b[i]:
			for val in nums:
				nn.append( j + len(b[i]) * val )
		nums = nn

	return nums


def create():
	player = BigWorld.player()
	return BigWorld.createEntity('Avatar', player.spaceID, 0, player.position, (0,0,0), {})

# Important - engine searches for Player here
from PlayerAvatar import PlayerAvatar

#Avatar.py
