
import Avatar
import PlayerAvatar
import math
import sys

from Avatar import Avatar
import AvatarMode as Mode
import AvatarModel
import BigWorld
import DroppedItem
import FDGUI
from FDGUI import Minimap
import FX
import FantasyDemo
import GUI
from Helpers import BWKeyBindings
from Helpers import Caps
from Helpers import ConsoleCommands
from Helpers import XMPP
from Helpers import collide
from Helpers.BWKeyBindings import BWKeyBindingAction
from Helpers.CallbackHelpers import *
from Helpers.CallbackHelpers import IgnoreCallbackIfDestroyed
import Inventory
import Item
import ItemBase
import ItemLoader
import Keys
import Math
from Math import *
from Math import Vector3
import Merchant
from ModeTarget import ModeTarget
import PlayerModel
import Seat
import PathSeeker
import TeleportSource as TeleportSource
from WebScreen import WebScreen
from bwdebug import *
from functools import partial
import random
import traceback
import weakref

# Named constants
STOW_PLACES = (
	SHOULDER,
	RIGHT_HIP,
	LEFT_HIP ) = range( 3 )

#
# PlayerAvatar C++ Interface Note:
# The identifier 'physics' refers to the C++ Python Object Physics. It is a
# special variable as it is initially set to a specified value to initialise
# it to a particular physics model.
#
# eg. self.physics = BigWorld.STANDARD_PHYSICS will initialise the physics
# object for the PlayerAvatar instance.
#
# Any subsequent call can then treat 'physics' as a structure with data
# members that control physics behaviour.
#
# eg. self.physics.collide = true will turn on collision detection for the
# PlayerAvatar.
#
# The list of physics data members are:
#     velocity, (X,Y,Z) movement velocity
#     velocityMouse, Direction|MouseX|MouseY indicating how the mouse
#         behave velocity.
#     angularMouse, Direction|MouseX|MouseY indicating how the mouse
#         affects direction.
#     angular, a double value indicating current angular velocity.
#     nudge, the (X,Y,Z) movement value to be moved this frame.
#     turn, the double value indicating turned amount this frame.
#     fall, a true or false value indicating if gravity should affect it.
#     collide, a true or false value indicating if collision detection is
#              turned on or off for this Avatar.
#
class PlayerAvatar(

# Important base classes
Avatar,
BWKeyBindings.BWActionHandler

):
	"TODO: Document"

	DROPPICK_TIMEOUT = 3
	TARGET_UPDATE_TIME_S = 1.0

	def __init__( self ):
		"""__init__ is never called because of how Player classes are made."""
		pass
		
	# ------------------------------------------------------------------------------
	# Method: prerequisites
	# Description:
	#	- This method is called between __init__ and onEnterWorld, and allows the
	#	class to load any resources it will need.  By the time this is called, all
	#	of the entity properties are set and can be used to determine exactly which
	#	resources to ask for.
	# ------------------------------------------------------------------------------
	def prerequisites( self ):
		prereqs = []
		return prereqs

	def onEnterWorld( self, prereqs, initial=True ):
		print "PlayerAvatar::onEnterWorld: begin"

		FantasyDemo.cameraType(0)

		self._initInventory()
		self._initInventoryGUI()

		if initial:
			self.initialPosition = self.position
			Avatar.onEnterWorld( self, prereqs )

		# we're using a filter tailor-made for us
		self.filter = BigWorld.PlayerAvatarFilter()
		self.am.entityCollision = 1
		self.am.collisionRooted = 0

		self._initInternalData()

		FantasyDemo.cameraType(0)

		self.setUpMovementSpeedsFromModel()

		self.initialPos = self.position
		self.pickingUpItem = False
		self.allowFPSModeToggle = True

		# physics setup
		self.initPhysics()
		self.am.velocityProvider = self.physics.uncorrectedVelocity

		# spawnPoint must be called after self.initialPos is set.
		self.physics.teleport( self.spawnPoint() )

		# Data associated with Movement
		self._initMovementData()

		# Targetting stuff
		BigWorld.target.exclude = self
		self.enableMouseTargetting()
		self.targetCaps = [ Caps.CAP_NEVER ]
		BigWorld.target.caps( Caps.CAP_NONE )
		self.minAimScore = 0.0
		self.maxAimScore = 0.99
		self.minimapColour = (64,64,255,255)

		self._initCombatData()
		self._initTradeData()

		FantasyDemo.rds.fdgui.onPlayerAvatarEnterWorld( self )
		FantasyDemo.addChangeEnvironmentsListener( self.onChangeEnvironments )
		self._initHealth()

		self.inventoryWindow.updateInventory(
				self.inventoryItems,
				self.inventoryMgr.availableGoldPieces() )

		#self._initInventory()

		self.set_rightHand( itemChangeAnim = 0 )	# set target caps
		self.set_shoulder()
		self.set_rightHip()
		self.set_leftHip()

		self._initWoWMode()

		self.moveForwardKeys = []
		self.moveBackwardKeys = []
		self.moveLeftKeys = []
		self.moveRightKeys = []

		self.guiMode( 0 )
		self.oldZoomLevel = 0
		FDGUI.Cursor.showCursor( True ) # Non-forced
		FantasyDemo.rds.keyBindings.addHandler( self )

		# and do stuff we can do every time scripts are reloaded
		self.reload()

		self.showCellBoundsModel = False
		self.cell.enableCellBoundsCapture( True )
		self.cellBoundsModel = BigWorld.Model( "sets/global/checker.model" )
		self.cellBoundsModel.visible = False
		self.addModel( self.cellBoundsModel )

		self.seeker = PathSeeker.PathSeeker()

		print "PlayerAvatar::onEnterWorld: end"

	def onBecomePlayer( self ):
		print "PlayerAvatar::onBecomePlayer"

		if self.inWorld:
			self.onEnterWorld( None, False )

		# Add minimap player arrow
		self.minimapIcon = GUI.load("gui/minimap_icon.gui")
		self.minimapHandle = FantasyDemo.rds.fdgui.minimap.m.add(
			self.matrix, self.minimapIcon )

	def onBecomeNonPlayer( self ):
		print "PlayerAvatar::onBecomeNonPlayer"
		self.filter = BigWorld.AvatarFilter()
		self.targetCaps = [ Caps.CAP_CAN_USE, Caps.CAP_CAN_HIT ]
		FantasyDemo.rds.keyBindings.removeHandler( self )

		# Could set self.gui, etc. to None if we wanted to
		# dispose their memory now too - instead it'll be
		# disposed when this Avatar is next made into a Player,
		# and those attributes are overwritten with new ones :-/

		# Remove minimap player arrow
		# Check if minimap still exists
		# eg. if the game is shutting down
		if hasattr( FantasyDemo.rds.fdgui, "minimap" ):
			FantasyDemo.rds.fdgui.minimap.m.remove( self.minimapHandle )
		# FDGUI.Minimap.remove() uses hasattr to determine if we have a
		# minimap icon.
		del self.minimapHandle

	def onLeaveWorld( self ):
		print "PlayerAvatar::onLeaveWorld"
		
		Avatar.onLeaveWorld( self )
		
		self._leaveWoWMode()
		FantasyDemo.delChangeEnvironmentsListener( self.onChangeEnvironments )
		FantasyDemo.rds.fdgui.onPlayerAvatarLeaveWorld( self )
		TeleportSource.cleanupTeleportGUI()
		FX.cleanupBufferedEffects()
		self.seeker.onLeaveWorld( self )

	def enableMouseTargetting( self ):
		if not hasattr( self, "mouseTargettingMatrix" ):
			self.mouseTargettingMatrix = BigWorld.MouseTargettingMatrix()
		BigWorld.target.source = self.mouseTargettingMatrix
		BigWorld.target.selectionFovDegrees = 5.0
		BigWorld.target.deselectionFovDegrees = 8.0


	def disableMouseTargetting( self ):
		if not hasattr( self, "playerTargettingMatrix" ):
			self.playerTargettingMatrix = BigWorld.ThirdPersonTargettingMatrix( BigWorld.PlayerMatrix() )
		BigWorld.target.source = self.playerTargettingMatrix
		BigWorld.target.selectionFovDegrees = 15.0
		BigWorld.target.deselectionFovDegrees = 20.0

	def _initInternalData( self ):
		self.doingAction = 0
		self.firstPerson = 0
		self.freeCamera = 0
		self.modelPreset = 0


	def _initMovementData( self ):
		self.forwardMagnitude	= 0.0
		self.upwardMagnitude	   = 0.0
		self.rightwardMagnitude	= 0.0
		self.speedMultiplier    = 1.0
		self.isDashing		 	   = 0
		self.isRunning			   = 1
		self.flying             = 0


	def _initCombatData( self ):
		self.toldServerID = 0
		self.NCTOutstanding = 0
		self.doingMovableAction = 0
		self.waitingToStand = 0
		self.ccLastAttacker = None


	def _initInventoryGUI( self ):
		weakself = weakref.proxy( self )

		def selectAndEquip( itemIndex ):
			itemSerial = self.inventoryMgr.itemIndex2Serial( itemIndex )
			itemType = self.inventoryMgr.selectItem( itemSerial )
			self._checkStowAndEquip()

		self.inventoryWindow = FantasyDemo.rds.fdgui.inventoryWindow.script
		self.inventoryWindow.inventoryMgr = weakref.proxy( self.inventoryMgr )

		self._stowSerial = [ Inventory.NOITEM ] * len( STOW_PLACES )


	def _initInventory( self ):
		self.inventoryMgr = Inventory.InventoryMgr( self, True )

		for i in self.inventoryItems:
			itemType = i["itemType"]
			ItemLoader.LoadBG( itemType, partial( self._cacheItem, itemType ) )


	def _initWoWMode( self ):
		self._useWoWMode = FantasyDemo.rds.useWoWMode
		self.inWoWMode = False
		self.onMouseMove = None
		self.inMouseMove = False
		self.isMovingToDest = False
		self.moveByStrafe = False
		self.autoMove = False
		self.isMoving = False
		self.isPanning = False
		self.mouseDown = False


	@BWKeyBindingAction( "WoWMode" )
	def _toggleWoWMode( self, isDown ):
		# Should only be used in response to a specific user command.
		# To show or hide the WoW mode for other reasons (like using the
		# binoculars), use the _enter and _leave methods.
		if isDown:
			if self.inWoWMode:
				self._leaveWoWMode()
				self._useWoWMode = False
			else:
				FantasyDemo.handleCameraKey( forceToStandardCamera = True )
				self._enterWoWMode()
				self._useWoWMode = True


	def _enterWoWMode( self ):
		if self.inWoWMode:
			return

		self.inWoWMode = True
		self.onMouseMove = None
		self.inMouseMove = False
		self.amountMouseMoved = 0
		self.isMovingToDest = False
		self.moveByStrafe = False
		self.autoMove = False
		self._setForwardMagnitude()
		self.physics.userDirected = False
		FDGUI.Cursor.forceShowCursor( True )
		self.enableEntityDirCamera()


	def enableEntityDirCamera( self ):
		FantasyDemo.setCursorCameraSource( self.entityDirProvider )
		self._isEntityDir = True

	def disableEntityDirCamera( self ):
		if hasattr( self, "_isEntityDir") and self._isEntityDir:
			m = Math.Matrix( self.entityDirProvider )
			BigWorld.dcursor().yaw = m.yaw
			BigWorld.dcursor().pitch = m.pitch
			self._isEntityDir = False
		FantasyDemo.setCursorCameraSource( BigWorld.dcursor().matrix )



	def _leaveWoWMode( self ):
		if not self.inWoWMode:
			return

		self.inWoWMode = False
		self.onMouseMove = None
		self.inMouseMove = False
		self.isMovingToDest = False
		self.moveByStrafe = False
		self.autoMove = False
		self._setForwardMagnitude()
		self.physics.userDirected = True
		FDGUI.Cursor.forceShowCursor( False )


	def _setupMouseMove( self ):
		self.amountMouseMoved = 0

		leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
		rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )
		if leftIsDown and rightIsDown:
			self._mouseMoveChange( 0, 0 )
		else:
			self.onMouseMove = self._mouseMoveChange


	def _enterMouseMove( self ):
		self.inMouseMove = True
		GUI.mcursor().visible = False
		GUI.mcursor().clipped = True
		self.disableMouseTargetting()

		try:
			turningHalfLife = BigWorld.camera().turningHalfLife
			if turningHalfLife > 0.0:
				self.savedTurningHalfLife = turningHalfLife
				BigWorld.camera().turningHalfLife = 0.0
		except AttributeError:
			#Free camera has no turningHalfLife attribute
			pass


	def _mouseMoveChange( self, dx, dy ):
		'''This function enables and disables camera movement using the
		direction cursor.

		To enable the camera movement it checks for mouse movement to become
		greater than a threshold. Once enabled, it is only disabled when both
		mouse buttons are up.

		It should be called on all mouse button events (up and down) to react
		to changes in the mouse button state as well as on all mouse move event
		until the threshold has been crossed.
		'''
		self._setForwardMagnitude()

		self.amountMouseMoved += abs(dx) + abs(dy)
		leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
		rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )

		if leftIsDown and rightIsDown:
			self.autoMove = False
			self._enterMouseMove()

		if rightIsDown:
			if self.amountMouseMoved > FantasyDemo.rds.mouseMoveThreshold:
				self.onMouseMove = None
				self.moveByStrafe = True
				self.physics.userDirected = True
				if self.isMoving:
					BigWorld.dcursor().yaw = self.yaw
					BigWorld.dcursor().pitch = self.pitch
				BigWorld.setCursor( BigWorld.dcursor() )
				self._enterMouseMove()

		elif leftIsDown:
			if self.amountMouseMoved > FantasyDemo.rds.mouseMoveThreshold:
				self.onMouseMove = None
				self.physics.userDirected = False
				BigWorld.setCursor( BigWorld.dcursor() )
				self._enterMouseMove()

		else:
			if self.moveByStrafe:
				self.enableEntityDirCamera()
			self.inMouseMove = False
			self.onMouseMove = None
			self.moveByStrafe = False
			self.physics.userDirected = False
			BigWorld.setCursor( GUI.mcursor() )
			GUI.mcursor().visible = True
			GUI.mcursor().clipped = False
			if hasattr( self, "savedTurningHalfLife" ):
				BigWorld.camera().turningHalfLife = self.savedTurningHalfLife
				del self.savedTurningHalfLife
			self.enableMouseTargetting()

	def getMouseCollidePos( self ):
		mp = GUI.mcursor().position
		collisionType, target = collide.collide( mp.x, mp.y )
		return ( collisionType, target )


	def onAddItem( self, itemType, itemSerial ):
		if not self._itemCache.has_key( itemType ):
			ItemLoader.LoadBG( itemType, partial( self._cacheItem, itemType ) )


	def onRemoveItem( self, itemType, itemSerial ):
		pass

	@IgnoreCallbackIfDestroyed
	def _cacheItem( self, itemType, resourceLoader ):
		self._itemCache[itemType] = self.getItem( itemType, resourceLoader )


	def _initTradeData( self ):
		self._tradeOfferLock = None


	def onChangeEnvironments( self, inside ):
		self.inside = inside
		Minimap.onChangeEnvironments( inside )


	# This function lets us know we've been reloaded ...
	# and we want to re-get all these function pointers.
	def reload( self ):
		reload( sys.modules["Item"] )

		self.setupActionList()
		self.onBindCallback = self._getMovementKeys
		self.onBindCallback()


	def _getMovementKeys( self ):
		keyBindings = FantasyDemo.rds.keyBindings
		self.moveForwardKeys = keyBindings.getBindingsForAction( "MoveForward" )
		self.moveBackwardKeys = keyBindings.getBindingsForAction( "MoveBackward" )
		self.moveLeftKeys = keyBindings.getBindingsForAction( "MoveLeft" )
		self.moveRightKeys = keyBindings.getBindingsForAction( "MoveRight" )


	def updateCursor( self ):
		mouseEnabled = self.inWoWMode

		if mouseEnabled:
			BigWorld.setCursor( GUI.mcursor() )
		else:
			BigWorld.setCursor( BigWorld.dcursor() )
		GUI.mcursor().visible = mouseEnabled
		GUI.mcursor().clipped = not mouseEnabled


	#This method implements player avatar specific additions to Avatar's
	#enterWaterCallback.
	def enterWaterCallback( self, entering, volume ):
		Avatar.enterWaterCallback( self, entering, volume )
		self.setUpMovementSpeedsFromModel()
		if entering:
			self.walkFwdSpeed /= 2.0
			self.runFwdSpeed /= 3.0
			self.dashFwdSpeed /= 4.0
			if not hasattr( self, "waterViscosity" ):
				self.waterViscosity = 3.0
				self.waterBuoyancy = 16
				self.waterSurfaceHeightDelta = -1.30
			self.physics.inWater = True
			self.physics.viscosity = self.waterViscosity
			self.physics.waterSurfaceHeight = volume.surfaceHeight + self.waterSurfaceHeightDelta
			self.physics.buoyancy = self.waterBuoyancy
		else:
			self.physics.inWater = False
		self.updateVelocity()


	# Avatar override: Going into using item mode
	def enterUsingItemMode( self ):
		Avatar.enterUsingItemMode( self )
		self.updateVelocity()

	# Avatar override: Going out of using item mode
	def leaveUsingItemMode( self ):
		#if self.rightHand != Item.Item.NONE_TYPE and self.rightHandItem:
		#	self.rightHandItem.release( self )
		Avatar.leaveUsingItemMode( self )

	# Avatar override: Entering crouch mode
	def enterCrouchMode( self ):
		FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenCrouched, 0.0 )
		Avatar.enterCrouchMode( self )
		self.updateVelocity()

	# Avatar override: Leaving crouch mode
	def leaveCrouchMode( self ):
		FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenStanding, 0.0 )
		Avatar.leaveCrouchMode( self )

	# Avatar override: Going into seated mode
	def enterSeatedMode( self ):
		self.sitDownWait( 5 )

	# Avatar override:
	@IgnoreCallbackIfDestroyed
	def sitDownWait( self, count ):
		if BigWorld.entity( self.modeTarget ) != None:
			FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenSeated, 0.0 )
			Seat.sitDown( self )
		elif count > 0:
			BigWorld.callback( 1, partial( self.sitDownWait, count-1 ) )

	# Avatar override: Leaving seated mode
	def leaveSeatedMode( self ):
		FantasyDemo.setCursorCameraPivot( 0.0, self.cameraHeightWhenStanding, 0.0 )
		Seat.standUp( self )

	def spawnPoint( self ):
		online = BigWorld.server()
		if online:
			rad = 3.0
			return (self.initialPos[0] + random.uniform( -rad, rad ),
				self.initialPos[1],
				self.initialPos[2] + random.uniform( -rad, rad ) )
		else:
			return self.initialPos

	def enterDeadMode( self ):
		BigWorld.callback( 6.0 + Avatar.DEAD_PENALTY,
			partial( self.physics.teleport, self.spawnPoint() ) )
		BigWorld.callback( 8.0 + Avatar.DEAD_PENALTY, self.cell.reincarnate )
		self.updateVelocity()
		self.equip( Item.Item.NONE_TYPE, 0 )
		self._leaveWoWMode()
		if hasattr( self, "physics" ) and self.physics is not None:
			self.physics.userDirected = False
		Avatar.enterDeadMode( self )

	def leaveDeadMode( self ):
		Avatar.leaveDeadMode( self )
		self.updateVelocity()
		self.filter = BigWorld.PlayerAvatarFilter()
		self.targetCaps = []
		self._enterWoWMode()

	def endReincarnation( self ):
		Avatar.endReincarnation( self )

		# Make sure doing action is zero, in case we died in some weird state
		if self.doingAction != 0: self.doingAction = 0

	# Avatar override: Becoming a target
	def modeTargetFocus( self, other ):
		# TODO: Put arrow over 'other'
		pass

	# Avatar override: Quitting as target
	def modeTargetBlur( self, other ):
		# TODO: Remove arrow from 'other'
		pass

	def moveActionCommence( self ):
		self.doingMovableAction += 1
		self.actionCommence()

	# Avatar override: Action commence
	def actionCommence( self ):
		#print "PlayerAvatar::actionCommence: doingAction was %d, now %d" % (
		#	self.doingAction, self.doingAction+1 )
		Avatar.actionCommence( self )
		if not self.doingAction:
			self._actionCommenceDirected = self.physics.userDirected
			self.physics.userDirected    = 0
		self.doingAction += 1
		self.updateVelocity()

	# Avatar override: Action complete
	def actionComplete( self ):
		if self.doingAction == 0:
			print "Warning: doingAction would go negative."
			traceback.print_stack()
			return

		#print "PlayerAvatar::actionComplete: doingAction was %d, now %d" % (
		#	self.doingAction, self.doingAction-1 )
		self.doingAction -= 1

		self.updateVelocity()

		if self.doingMovableAction > 0:
			self.doingMovableAction -= 1

		try:
			if not self.doingAction:
				self.physics.userDirected = self._actionCommenceDirected
		except AttributeError:
			pass

		Avatar.actionComplete( self )

		self.doingActionDecremented()

	# doingAction was decremented (only done in actionComplete
	#  and when right mouse released for targetting)
	def doingActionDecremented( self ):
		# If we are now free, then respond to any waiting events
		if self.mode == Mode.NONE and self.doingAction == 0:

			# If we're being attacked then fight back immediately
			if self.ccLastAttacker != None and \
				self.ccLastAttacker.mode == Mode.COMBAT_CLOSE and \
				self.ccLastAttacker.modeTarget == self.id:
					self.ccRespond( self.ccLastAttacker )


	# Enter the appropriate GUI mode
	def guiMode( self, mode ):
		if mode == 0:
			#Standard H.U.D.
			FantasyDemo.rds.fdgui.showBinoculars( False )
			FantasyDemo.firstPerson( self.firstPerson )
			BigWorld.projection().fov = 1.0472 #60 degrees
			if self._useWoWMode:
				self._enterWoWMode()
			self.hideModel( self.firstPerson )
		elif mode == 1:
			#Spy Camera. Removed.
			pass
		else:
			#Binoculars
			FantasyDemo.rds.fdgui.showBinoculars( True )
			BigWorld.projection().fov = 0.5 #zoomed in
			FantasyDemo.firstPerson( True )
			if self.inWoWMode:
				self._leaveWoWMode()
			self.hideModel( 1 )

			# Calculate the new FOV into which to move.
			#self.oldZoomLevel = 0
			#minFOV = 2.5
			#maxFOV = 18.0
			#newFOV = maxFOV + ( minFOV - maxFOV ) * (
			#	self.oldZoomLevel / 30.0 )
			# <binoculars need more work> BigWorld.changeFOV( newFOV, 0.01 )

		self.guiModeSelected = mode


	# -------------------------------------------------------------------------
	# Command: Cancel current action.
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "EscapeKey" )
	def escapeKey( self, isDown ):
		handled = False

		if isDown:
			handled = True

			if self.mode in ( Mode.TRADE_ACTIVE, Mode.TRADE_PASSIVE ):
				self.tradeCancel()
			elif self.mode == Mode.COMMERCE:
				self.commerceCancel()
			elif self.mode == Mode.SEATED:
				BigWorld.entity(self.modeTarget).use()
			elif self.mode != Mode.NONE and not self.inCombat():
				FantasyDemo.cameraType( FantasyDemo.rds.CURSOR_CAMERA )
				if not self._isConnected():
					omode = self.mode
					self.mode = -1
					self.set_mode( omode )
				elif self.mode == Mode.COMBAT_CLOSE:
					self.cell.cancelMode()
					if self.ccTarget is not None and \
							self.ccTarget.mode == Mode.COMBAT_CLOSE and \
								self.ccTarget.modeTarget == self.id:
						self.ccTarget.cell.cancelMode()
				else:
					self.cell.cancelMode()
			elif self.inCombat():
				# remove the weapon, so that you go out of combat mode
				self.unequipItem()
			elif not self.doingAction and self.rightHand != Item.Item.NONE_TYPE:
				self.unequipItem()
			else:
				handled = False

		return handled


	# -------------------------------------------------------------------------
	# Command: Last resort gameplay-ignoring current action cancel
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "LastResortEscapeKey" )
	def lastResortEscapeKey( self, isDown ):
		if not isDown: return

		if hasattr( self, "lastResortGui" ): return

		g = GUI.Text( "WAIT" )
		g.position = (0,0,1)
		GUI.addRoot( g )
		self.lastResortGui = g

		# First wait 2s
		self.lastResortGui.colour = (255,0,0,255)
		BigWorld.callback( 2, self.lrekTwo )

	@IgnoreCallbackIfDestroyed
	def lrekTwo( self ):
		# Try a normal escape
		try:
			self.escapeKey( 1 )
		except:
			pass

		# And wait 2s
		self.lastResortGui.colour = (255,255,255,255)
		BigWorld.callback( 2, self.lrekThree )

	@IgnoreCallbackIfDestroyed
	def lrekThree( self ):
		# Now try a server cancel mode
		if self.mode != Mode.NONE:
			self.cell.cancelMode()

		# Wait 2s
		self.lastResortGui.colour = (255,0,0,255)
		BigWorld.callback( 2, self.lrekFour )

	@IgnoreCallbackIfDestroyed
	def lrekFour( self ):
		# If we're still not in the right mode, reincarnate ourselves
		# (which always gets us out of any mode ... currently)
		if self.mode != Mode.NONE:
			self.cell.reincarnate()

		# Wait 2s
		self.lastResortGui.colour = (255,255,255,255)
		BigWorld.callback( 2, self.lrekFive )

	@IgnoreCallbackIfDestroyed
	def lrekFive( self ):
		# Clean up locally

		# Clear our mode anyway
		self.mode = Mode.NONE

		# Doing action
		if self.doingAction < 0: self.doingAction = 0
		while self.doingAction > 0: self.actionComplete()

		# Clear our right hand item
		self.rightHand = -1
		self.cell.setRightHand( -1 )

		# Recreate our model (fixes queue, visibility, and trackers)
		self.set_modelNumber()

		self.lastResortGui.colour = (255,0,0,255)
		BigWorld.callback( 0.5, self.lrekEnd )

	def lrekEnd( self ):
		# Turn off any weird GUI things
		self.firstPerson = 0
		self.guiMode( 0 )

		self.hud.lastResortGui = None
		del self.lastResortGui


	# -------------------------------------------------------------------------
	# Command: Sets the zoom level for the player.
	# -------------------------------------------------------------------------
	def setZoomLevel( self, newZoomLevel ):
		if self.guiModeSelected == 2:
			# Calculate the new FOV into which to move.
			minFOV = 2.5
			maxFOV = 18.0
			newFOV = maxFOV + ( minFOV - maxFOV ) * ( newZoomLevel / 30.0 )

			timeToChange = 0.25
			if self.oldZoomLevel > newZoomLevel:
				pass # BigWorld.playFx( "binoc_out", self.position )
				pass # BigWorld.changeFOV( newFOV, timeToChange * 2.0 )
			elif self.oldZoomLevel < newZoomLevel:
				pass # BigWorld.playFx( "binoc_in", self.position )
				BigWorld.changeFOV( newFOV, timeToChange )
				timeToChange = 0.25

			self.oldZoomLevel = newZoomLevel


	# -------------------------------------------------------------------------
	# Command: Toggles between first and third person mode.
	# -------------------------------------------------------------------------
	def toggleFirstPersonMode( self, isDown ):
		if not self.guiModeSelected == 2 and self.allowFPSModeToggle:
			if not self.freeCamera:
				if isDown:
					self.firstPerson = 1
				else:
					self.firstPerson = 0

				FantasyDemo.firstPerson( self.firstPerson )
				self.hideModel( self.firstPerson )
				return True
		return False


	def allowFirstPersonModeToggle(self, allow):
		self.allowFPSModeToggle = allow

	# -------------------------------------------------------------------------
	# Command: Toggles between mouse control and direction cursor modes for
	# the camera.
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "FreeCameraMode" )
	def toggleFreeCameraMode( self, isDown ):
		if not self.firstPerson:
			if isDown:
				self.freeCamera = not self.freeCamera
				FantasyDemo.freeCamera( self.freeCamera )

	# -------------------------------------------------------------------------
	# Command: Null action. This is used if the C++ code has a binding for
	# one of the keys used by another command; the script code then binds
	# that set to the null action.
	#
	# eg. The C++ code looks for Shift+MiddleMouseButton.
	# Since the script also watches for MiddleMouseButton, then it needs to
	# also bind Shift+MiddleMouseButton to nullAction to disambiguate the
	# key presses.
	# -------------------------------------------------------------------------
	def nullAction( self, isDown ):
		pass

	# -------------------------------------------------------------------------
	# Section: Items trading commands
	# -------------------------------------------------------------------------

	@BWKeyBindingAction( "Trade" )
	def onTradeKey( self, isDown = True ):
		'''Handles do-trade key event.
		Params:
			isDown				key down state
		'''
		if not isDown:
			return

		if self.physics.inWater:
			return

		if self.mode != Mode.NONE or self.inCombat():
			return

		if self.mode not in (Mode.TRADE_ACTIVE, Mode.TRADE_PASSIVE):
			if not self.doingAction:
				self.tradeTry()
		else:
			self.tradeCancel()

	# -------------------------------------------------------------------------
	# Section: Items locking
	# -------------------------------------------------------------------------

	def onUnlockItem( self, lockHandle ):
		'''Handles unlock item events (when user clicks on a locked
		item in the inventory gui). Requests unlocking to server.
		Params:
			lockHandle			handle to item(s) lock
		'''
		self.cell.itemsUnlockRequest( lockHandle )


	def itemsLockNotify( self, lockHandle, itemsSerials, goldPieces ):
		'''Cell is notifying us about items being locked. Just should only
		be called when the locking was not done as a request from the client
		(since in those cases, the client locks his items preenptively).
		Lock items localy so that the player cannot use them. Unequip
		current item if it is in the list of items to lock.
		Params:
			lockHandle			handle to recently locked items
			itemsSerials		serial to all items being locked
			goldPieces			ammount of gold to lock
		'''
		try:
			try:
				if self.inventoryMgr.currentItemSerial() in itemsSerials:
					self.unequipItem()
			except ValueError: # no current item
				pass
			self.inventoryMgr.itemsRelock( lockHandle, itemsSerials, goldPieces )
			self.inventoryWindow.updateInventory(
				self.inventoryItems,
				self.inventoryMgr.availableGoldPieces() )
		except Inventory.LockError:
			errorMsg = 'ClientAvatar.itemsLockNotify: cannot lock items'
			print errorMsg


	def itemsUnlockNotify( self, success, lockHandle ):
		'''Notification that some item(s) have being unlocked in the
		server. Unlock them localy, as well. If lockHandle is for the
		item currently offered for trade, remove it from trade GUI.
		Params:
			success				True if request granted or is not a response to one
			lockHandle			handle to recently unlocked items
		'''
		if success:
			try:
				self.inventoryMgr.itemsUnlock( lockHandle )
			except Inventory.LockError:
				errorMsg = 'PlayerAvatar.itemsUnlockNotify: error unlocking items (handle=%d)'
				print errorMsg % lockHandle
				pass

			self.inventoryWindow.updateInventory(
					self.inventoryItems,
					self.inventoryMgr.availableGoldPieces() )

			if lockHandle == self._tradeOfferLock:
				self._tradeOfferLock = None
		else:
			self.disagree()
			if lockHandle == self._tradeOfferLock:
				FantasyDemo.addChatMsg( -1, 'Cannot withdraw accepted offer' )
			else:
				FantasyDemo.addChatMsg( -1, 'Cannot unlock item' )

	# -------------------------------------------------------------------------
	# Section: Items commerce commands
	# -------------------------------------------------------------------------

	@BWKeyBindingAction( "Commerce" )
	def onCommerceKey( self, isDown = True, partner = None ):
		'''Handles do-commerce key event.
		Params:
			isDown				key down state
		'''
		if not isDown:
			return

		if self.physics.inWater:
			return

		if self.mode != Mode.NONE or self.doingAction or self.inCombat():
			return

		if self.mode != Mode.COMMERCE:
			if partner == None:
				partner = BigWorld.target()
			self.commerceTry( partner )
		else:
			self.commerceCancel()


	def onSellItem( self, itemSerial ):
		'''Handles item sell events (when the user
		clicks on the sell button in the inventory GUI)
		Params:
			itemIndex			index of item in the inventory
		'''
		#~ print '--->', itemSerial
		#~ return

		assert self.mode == Mode.COMMERCE
		try:
			itemLock = self.inventoryMgr.itemsLock( [itemSerial], 0 )
			self.cell.commerceSellRequest( itemLock, itemSerial )
		except (Inventory.LockError, ValueError):
			FantasyDemo.addChatMsg( -1, "Unable to sell specified item" )


	def onBuyItem( self, itemIndex ):
		'''Handles item buy events (when the user clicks on the
		buy button in the inventory GUI). Ignore command if we're
		waiting for a reply from server about a previous buy.
		Params:
			itemIndex			index of item in the seller inventory
		'''
		if self._buyItemIndex is not None:
			return

		try:
			itemPrice = ItemBase.price( self._commerceItems[ itemIndex ]['itemType'] )
			itemLock = self.inventoryMgr.itemsLock( [], itemPrice )
			self._buyItemIndex = itemIndex
			self.cell.commerceBuyRequest( itemLock, itemIndex )
		except Inventory.LockError:
			FantasyDemo.addChatMsg( -1, "Not enough gold pieces to buy item" )
			self.disagree()
		except IndexError:
			errorMsg = 'PlayerAvatar.onBuyItem: invalid item index (idx=%d)'
			print errorMsg % itemIndex
			self.disagree()

	# -------------------------------------------------------------------------
	# Section: Items commerce
	# -------------------------------------------------------------------------

	def commerceTry( self, partner ):
		'''Try entering the commerce mode
		'''
		if partner and isinstance( partner, Merchant.Merchant ):
			if partner.modeTarget == Mode.NO_TARGET:
				self.unequipItem()
				self.moveActionCommence()
				self.commerceEngage( partner )
				return
		self.disagree()


	def commerceCancel( self ):
		'''Requests cancelation of commerce mode
		'''
		self.cell.commerceCancelRequest()


	def commerceEngage( self, partner ):
		'''Try entering the commerce mode. Do this in two steps:
		(1) move close to Merchant and (2) request commerce mode.
		Params:
			partner				the commerce partner entity
		'''
		def doStep1():
			self._tradePosSeek( partner, doStep2, doFail )

		def doStep2():
			self.actionCommence()
			self.setModeTarget( partner.id )
			self.cell.commerceStartRequest( partner.id )

		def doFail():
			self.setModeTarget( Mode.NO_TARGET )
			self.actionComplete()
			self.disagree()

		doStep1()


	def commerceEnterMode( self ):
		'''Called when PlayerAvatar.mode gets set by the cell.
		The PlayerAvatar takes care of setting up the stage, animating
		both characters and showing the commerce icon
		'''
		def endHandshake():
			self.actionComplete()

		partner = ModeTarget._getModeTarget( self )
		if partner != None:
			self.tradeAnimateAccept( endHandshake )
			partner.tradeAnimateAccept()
			self._commerceShowGUI( True )
			self._buyItemIndex = None


	def commerceLeaveMode( self ):
		'''Called when Avatar.mode gets set by the cell. Cleans the scene.
		'''
		traderWindow = FantasyDemo.rds.fdgui.traderWindow.script
		traderWindow.updateInventory( [], 0 )
		traderWindow.active( False )

		if not self._inventoryWasActive:
			self.inventoryWindow.active( False )

		self.actionComplete()
		partner = ModeTarget._getModeTarget( self )
		self.setModeTarget( Mode.NO_TARGET )
		self._commerceShowGUI( False )
		self._commerceItems = None
		self.cell.finaliseCommerceCancel()


	def commerceStartDeny( self ):
		'''The cell is denying our request to enter commerce mode.
		(maybe Merchant has just been grabbed by another player).
		'''
		self.setModeTarget( Mode.NO_TARGET )
		self.actionComplete()
		self.disagree()


	def _commerceShowGUI( self, visible ):
		'''Shows/hide inventory GUI in commerce mode.
		Params:
			visible				True if GUI is to be shown. False if should be hidden
		'''
		if visible:
			self.inventoryWindow.updateInventory(
					self.inventoryItems,
					self.inventoryMgr.availableGoldPieces() )

		self.updateCursor()


	def commerceItemsNotify( self, items ):
		'''The Merchant is notifying us about the items it has for sale.
		Params:
			items					List of item being sold by merchant
		'''
		self._commerceItems = items

		traderWindow = FantasyDemo.rds.fdgui.traderWindow.script
		traderWindow.updateInventory( self._commerceItems, 0 )
		traderWindow.active( True )

		self._inventoryWasActive = self.inventoryWindow.isActive
		self.inventoryWindow.active( True )


	def _commerceCommitNotify( self, success, outItemsLock, inItemsTypes ):
		'''This method is called by the trade commit notify if the
		transaction was the result of a commerce (buy/sell) operation.
		Note that the actual items/gold transcation will be carried by
		the tradeCommitNotify method. This methos will only take care
		of properly updating the commerce interface.
		Params:
			success				True if trade was successful. False otherwise
			outItemsLock		lock handle for items being traded out
			inItemsTypes		types of items being traded in
		'''
		if success:
			try:
				discardSerial, outItems, goldPieces = \
					self.inventoryMgr.itemsLockedRetrieve( outItemsLock )

				if outItems:
					# Player is selling
					Inventory.addItems( self._commerceItems, [{'serial': discardSerial[i], 'itemType':outItems[i], 'lockHandle':Inventory.NOLOCK } for i in range(len(outItems)) ] )
				else:
					# Player is buying
					assert len( inItemsTypes ) == 1
					assert self._commerceItems[ self._buyItemIndex ]['itemType'] == inItemsTypes[0]
					Inventory.removeItem( self._commerceItems, self._buyItemIndex )
					self._buyItemIndex = None

				traderWindow = FantasyDemo.rds.fdgui.traderWindow.script
				traderWindow.updateInventory( self._commerceItems, 0 )
				traderWindow.active( True )

			except Inventory.LockError:
				errorMsg   = 'PlayerAvatar._commerceCommitNotify: lock not found '
				parameters = '(lock=%d)' % outItemsLock
				print errorMsg + parameters
		else:
			self._buyItemIndex = None
			FantasyDemo.addChatMsg( -1, "Merchant is unable to proceed with trade" )
			ModeTarget._getModeTarget( self ).disagree()
			self.disagree()


	# -------------------------------------------------------------------------
	# Section: Items pick-up and drop commands
	# -------------------------------------------------------------------------

	@BWKeyBindingAction( "PickDrop" )
	def onPickDropKey( self, isDown = True ):
		'''Handles pick/drop item key events.
		Params:
			isDown				key down state
		'''

		if self.physics.inWater:
			return
		
		# ignore key if player is seated, in
		# combat or doing some other action
		if self.mode == Mode.SEATED or not isDown or self.doingAction:
			return

		# if not holding an item, try picking one up
		# if holding an item, try dropping it
		if self.rightHand == Item.Item.NONE_TYPE:
			self.pickUpTry()
		else:
			self.dropTry()


	def onEquipNDrop( self, itemIndex ):
		'''Handles item drop event (when the user draggs and
		drops an item in the drop area in the inventory gui)
		Params:
			itemIndex			index to inventory of item being dropped
		'''
		currentItem = self.inventoryMgr.currentItem()
		if currentItem != self.rightHand:
			self.equip( currentItem )
			cib = self.model.ChangeItemBegin
			cibDur = cib.duration - cib.blendOutTime - 0.0001
			cie = self.model.ChangeItemEnd
			cieDur = cie.duration - cie.blendOutTime - 0.0001
			BigWorld.callback( cibDur + cieDur, partial( self.onPickDropKey ) )
		else:
			self.onPickDropKey()

	# -------------------------------------------------------------------------
	# Section: Items pick-up
	# -------------------------------------------------------------------------

	def pickUpTry( self ):
		'''Try to pick-up current target.
		'''
		target = BigWorld.target()
		Item = DroppedItem.DroppedItem
		if target and isinstance( target, Item ) and target.pickUpTry():
			self.pickExecute( target )
		else:
			self.disagree()


	def pickExecute( self, droppedItem ):
		'''Do the first two steps in the pick-up procedure:
		(1) seek pick-up position and (2) request pick-up to cell.
		Params:
			droppedItem			item entity being picked up
		'''
		def doStep1():
			self.unequipItem()
			self.moveActionCommence()
			self.pickUpSeekPos( droppedItem, doStep2, handleFailure )

		def doStep2():
			if self._isConnected():
				self.cell.pickUpRequest( droppedItem.id )
				self._pickUpSetupCancelTimer()
			else:
				# if not connected, short circuit
				import time
				self.pickUpResponse( True, droppedItem.id, int(time.clock()) + 100 )

		def handleFailure():
			self.disagree()
			self.actionComplete()

		doStep1()


	def _pickUpSetupCancelTimer( self ):
		'''Sets timer for cancelation of pick-up.
		'''
		@IgnoreCallbackIfDestroyed
		def cancel( self ):
			if self._waitingPickup:
				self.disagree()
				self.actionComplete()
				self._waitingPickup = False

		self._waitingPickup = True
		BigWorld.callback( self.DROPPICK_TIMEOUT, partial( cancel, self ) )


	def pickUpResponse( self, success, droppedItemID, itemSerial ):
		'''Cell entity is notifying that this entity is picking up an item
		Params:
			success				True is pickup request was granted. False otherwise
			droppedItemID		id of item entity being picked up
			itemSerial			serial assigned to item when inside the inventory
		'''
		if success:
			try:
				droppedItem = BigWorld.entities[ droppedItemID ]
				self._pickUpProcedure( droppedItem, itemSerial )
			except KeyError:
				errorMsg = 'pick-up response for unknown entity: %d'
				print errorMsg % droppedItemID
		else:
			self.disagree()
			self.actionComplete()

		self._waitingPickup = False


	def _pickUpProcedure( self, droppedItem, itemSerial ):
		'''Does the pickup procedure and adds item to inventory.
		Params:
			droppedItem			item entity being picked up
			itemSerial			serial assigned to item when inside the inventory
		'''

		def doStep1():
			self.lockRightHandModel( True )
			self.pickUpAnimate( doStep2, doStep3 )

		def doStep2():
			droppedItem.pickUpComplete()
			itemType = droppedItem.classType
			self.inventoryMgr.addItem( itemType, itemSerial )
			self.inventoryMgr.selectItem( itemSerial )
			itemIndex = self.inventoryMgr.currentItemIndex()

			self.inventoryWindow.updateInventory(
					self.inventoryItems,
					self.inventoryMgr.availableGoldPieces() )

			self.lockRightHandModel( False )
			self.equip( itemType, 0 )

		def doStep3():
			self.actionComplete()

		doStep1()
		self._waitingPickup = False


	def pickUpSeekPos( self, droppedItem, successCallback, errorCallback ):
		'''Moves avatar close to the item where the pickup animation
		should be played. Eventually calls successCallback or failCallback
		depending of the outcome of the seek operation.
		Params:
			droppedItem			item entity being picked up
			successCallback	callback to be called if seek is successfull
			failCallback		callback to be called if seek fails
		'''
		moveToPos = Vector3( droppedItem.position )

		#	1. Find the normalised direction
		#     from player to item.
		delta = moveToPos - Vector3( self.position )
		delta.normalise()

		#	2. Offset that distance by an approximate
		#     hand-to-item distance.
		#
		#  TODO: The magic cueball says it is around 45 cm.
		#  We should not be relying on the magic cueball.
		handToItemDist = 0.45
		delta = delta.scale( handToItemDist )
		moveToPos -= delta

		#	3. Calculate the desired termination
		#     yaw from the delta vector.
		yaw = math.atan2( delta.x, delta.z )

		#  4. Tell the Avatar to move into position.
		finalPosition = ( moveToPos.x, moveToPos.y, moveToPos.z, yaw )

		def onSeek( success ):
			if success:
				successCallback()
			else:
				errorCallback()

		self.seeker.seekPath( self,
			finalPosition,
			self.walkFwdSpeed,
			10.0,
			0.40,
			onSeek )

	def disagree( self ):
		'''Play the disagree animation.
		'''
		Avatar.disagree( self )
		self.cell.didGesture( 4 )

	# -------------------------------------------------------------------------
	# Section: Items drop
	# -------------------------------------------------------------------------

	def dropTry( self ):
		'''Try to drop currently equipped item.
		'''
		if self._isConnected():
			self.dropOnline()
		else:
			self.dropOffline()


	def dropOnline( self ):
		'''Request item drop to base.
		'''
		self.actionCommence()
		itemClass = self.inventoryMgr.currentItem()
		itemSerial = self.inventoryMgr.currentItemSerial()
		self.base.dropRequest( itemSerial )

		# ... setup cancel timer
		@IgnoreCallbackIfDestroyed
		def cancel( self ):
			if self._waitingDrop:
				self.disagree()
				self.actionComplete()
				self._waitingDrop = False

		self._waitingDrop = True
		BigWorld.callback( self.DROPPICK_TIMEOUT, partial( cancel, self ) )


	def dropOffline( self ):
		'''Simulate server response to drop request:
		create a local item at hand distance.
		'''
		self.actionCommence()

		# compute drop position
		dir = Vector3( math.sin(self.yaw), 0, math.cos(self.yaw) )
		dropPos = Vector3(self.position) + dir.scale( 0.45 )

		upVector = Vector3(0.0, 2.0, 0.0)
		dropRes = BigWorld.findDropPoint( self.spaceID, dropPos + upVector )
		if dropRes != None:
			dropPos = dropRes[0]

		# create DroppedItem
		itemClass = self.inventoryMgr.currentItem()
		itemSerial = self.inventoryMgr.currentItemSerial()
		properties = {
				'itemSerial'	 : itemSerial,
				'classType'		 : itemClass,
				'dropperID'		 : self.id }

		BigWorld.createEntity( 'DroppedItem',
			self.spaceID, 0, dropPos.tuple(),
			( 0.0, self.yaw, 0.0 ), properties )


	def _dropProcedure( self, droppedItem ):
		'''Do the complete drop procedure in three steps: (1) start drop,
		(2) drop/unequip/remove item from inventory and (3) finish drop.
		Overrides method in Avatar. Also invalidates drop cancelation timer.
		Params:
			droppedItem			DroppedItem entity just dropped
		'''
		def doStep1():
			self.lockRightHandModel( True )
			self.dropAnimate( droppedItem, doStep2, doStep3 )

		def doStep2():
			droppedItem.dropComplete()
			self.inventoryMgr.removeItem(droppedItem.itemSerial)
			self.inventoryWindow.updateInventory(
					self.inventoryItems,
					self.inventoryMgr.availableGoldPieces() )
			self.equip( Item.Item.NONE_TYPE, 0 )
			BigWorld.target.caps( Caps.CAP_CAN_USE )
			self.lockRightHandModel( False )

		def doStep3():
			self.actionComplete()

		doStep1()
		self._waitingDrop = False


	def dropDeny( self ):
		'''Server is notifying us that the drop request has been denied.
		'''
		self.actionComplete()
		self.disagree()


	# -------------------------------------------------------------------------
	# Command: Hit the Move Key
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "RightMouseButton" )
	def moveKey( self, isDown ):
		if self.inWoWMode:
			if self.inMouseMove:
				# We're moving the camera with the mouse. React to new button state.
				self._mouseMoveChange( 0, 0 )
			elif isDown:
				self.mouseDown = True
				# Mouse button down. Wait for a move.
				self.seeker.cancel( self )
				self._setupMouseMove()
				self.disableEntityDirCamera()
			else:
				self.mouseDown = False
				if self.isMoving:
					self.enableEntityDirCamera()

				# Mouse button up and we weren't moving the camera.
				# Try to move the player.

				# Can seek in water
				# Can't seek if seated or waiting for handshake etc.
				if self.mode != Mode.NONE:
					return

				# Get new target
				type, target = self.getMouseCollidePos()
				if type == collide.COLLIDE_TERRAIN:
					targetPosAndYaw = self.seeker.getPosAndYawToTarget(
						self.position, target )
					self.seeker.seekPath( self, targetPosAndYaw, self.runFwdSpeed )
				elif type == collide.COLLIDE_ENTITY:
					targetPosAndYaw = self.seeker.getPosAndYawToTarget(
						self.position, target.position )
					self.seeker.seekPath( self, targetPosAndYaw, self.runFwdSpeed )
			return


	# -------------------------------------------------------------------------
	# Command: Hit the Use Key
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "LeftMouseButton" )
	def useKey( self, isDown ):
		if self.inWoWMode:
			if self.inMouseMove:
				# We're moving the camera with the mouse. React to new button state.
				self._mouseMoveChange( 0, 0 )
			else:
				# Mouse button up and we weren't moving the camera. Try to move the player.
				type, target = self.getMouseCollidePos()
				if isDown:
					#Mouse down on web screen doesn't do anything (the mouse up will use the web screen)
					if not self.inWebScreenMode() or not isinstance(target, WebScreen) :
						# Mouse button down. Wait for a move.
						self._setupMouseMove()
				else:
					if type == collide.COLLIDE_ENTITY:
						self.onEntityClicked( target )
					else:
						self.onEntityClicked( None )
						#Remove currentWebScreen
						if self.currentWebScreen != None :
							self.removeWebScreenFocus()
			# if we're moving, make sure the EDP is on
			if isDown:
				self.mouseDown = True
				self.disableEntityDirCamera()
				if not self.isPanning or self.isMoving:
					BigWorld.dcursor().yaw = self.yaw
					BigWorld.dcursor().pitch = self.pitch
				self.isPanning = True
			else:
				self.mouseDown = False
				if self.isMoving:
					self.enableEntityDirCamera()
					self.isPanning = True
					BigWorld.dcursor().yaw = self.yaw
					BigWorld.dcursor().pitch = self.pitch
			return

		if isDown:
			if self.mode == Mode.SEATED:
				if not self.doingAction:
					if self.rightHandItem != None and self.rightHand != -1:
						self.rightHandItem.use( self, BigWorld.target() )
					else:
						BigWorld.entity(self.modeTarget).use()

			elif not self.doingAction:
				handled = 0
				if not handled and BigWorld.target() != None and \
					   Caps.CAP_CAN_HIT not in BigWorld.target().targetCaps:
					BigWorld.target().use()
					handled = 1

				#PCWJ - removed 'create new item on use just to check the itemType'
				#because that seems ridiculous to do but why was this in here??
				#and self.rightHandItem.itemType == Item.newItem(self.rightHand).itemType:
				if not handled and self.rightHandItem != None and self.rightHand != -1:
					handled = self.rightHandItem.use( self, BigWorld.target() )
					if handled not in [0,1]:
						print "Warning: No bool from item %d use method" % \
							self.rightHand
						handled = 1

				if not handled and BigWorld.target() != None:
					BigWorld.target().use()
					handled = 1

				if not handled:
					pass

			elif self.doingAction == 1 and self.mode == Mode.COMBAT_CLOSE:
				self.closeCombatSwing()

	def setWebScreenFocus( self, webScreen ):
			self.currentWebScreen = webScreen
			FantasyDemo.rds.inGameFocusedComponent = webScreen
			self.origCursorShape = GUI.mcursor().shape
			GUI.mcursor().shape = 'point'
			self.mode = Mode.WEB_SCREEN
			self.set_mode( Mode.NONE )
			self.actionCommence()
			#show the web controls
			if self.currentWebScreen.isGame():
				FantasyDemo.rds.fdgui.activateWebGameControls(True)
			else:
				FantasyDemo.rds.fdgui.webControls.editField.script.setText(webScreen.url())
				FantasyDemo.rds.fdgui.activateWebControls(True)

	def removeWebScreenFocus( self ):
		FantasyDemo.rds.inGameFocusedComponent = None
		if hasattr(self, 'origCursorShape'):
			GUI.mcursor().shape = self.origCursorShape
		self.currentWebScreen.setFocus(False)
		#Hide the web controls
		if self.currentWebScreen.isGame():
			FantasyDemo.rds.fdgui.activateWebGameControls(False)
		else:
			FantasyDemo.rds.fdgui.activateWebControls(False)
		self.currentWebScreen = None
		self.mode = Mode.NONE
		self.cancelMode( Mode.WEB_SCREEN )
		self.actionComplete()

	def onEntityClicked( self, target ):

		# Not doing anything
		if not self.doingAction:

			# Use item
			if self.rightHandItem != None and self.rightHand != -1:
				self.rightHandItem.use( self, target )
			# Use target
			elif target:
				#Don't change the yaw when clicking on WebScreens as this gives better user experience
				if not hasattr (target, "changeYawWhenUsed") or target.changeYawWhenUsed:
					curr_yaw = (target.position - self.position).yaw
					BigWorld.dcursor().yaw = curr_yaw

				# Use target
				target.use()

		# Attacking
		elif self.doingAction == 1 and self.mode == Mode.COMBAT_CLOSE:
			self.closeCombatSwing()
			
		# Web
		elif self.doingAction == 1 and self.mode == Mode.WEB_SCREEN:
			if target: 
				target.use()

	# -------------------------------------------------------------------------
	# Command: Use Communipanion
	# -------------------------------------------------------------------------
	def useCommunipanion( self, isDown ):
		if not isDown:
			return
		if self.doingAction == 0 and self.mode == Mode.NONE:
			# Activate Communipanion.
			print "Activating communipanion"
			self.setUsingCurrentItem( 1 )
		elif self.doingAction == 1 and self.mode == Mode.USING_ITEM:
			# Dectivate Communipanion.
			print "Deactivating communipanion"
			self.setUsingCurrentItem( 0 )

	# -------------------------------------------------------------------------
	# Command: Auto move forward
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "AutoMove" )
	def toggleAutoMove( self, isDown ):
		if self.mode != Mode.NONE: return
		if isDown:
			self.autoMove = not self.autoMove
			self._setForwardMagnitude()

	# -------------------------------------------------------------------------
	# Command: Move Forward
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "MoveForward" )
	def moveForward(self, isDown):
		if isDown:
			leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
			rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )

			if rightIsDown and not leftIsDown:
				self.moveByStrafe = True
				self.physics.userDirected = True
				self.isMoving = True
				BigWorld.setCursor( BigWorld.dcursor() )
				self._enterMouseMove()

			self.autoMove = False
			if self.isMovingToDest:
				self.seeker.cancel( self )

			if self.physics.chasing:
				self.physics.stop()

			self._setForwardMagnitude()
			if self.mode == Mode.COMBAT_CLOSE:
				if self.stance == Avatar.STANCE_BACKWARD:
					nst = Avatar.STANCE_NEUTRAL
				else:
					nst = Avatar.STANCE_FORWARD
				self.takeStance( nst )

			if not self.mouseDown:
				self.enableEntityDirCamera()
				self.isPanning = False
			self.isMoving = True
		else:
			self._setForwardMagnitude()
			self.isMoving = False


	def _setForwardMagnitude( self ):
		'''Look at the keys that are down to work out what the forward/backward
		movement should be.
		'''
		leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
		rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )

		forwardCount = 1 if self.autoMove else 0
		forwardCount += 1 if (leftIsDown and rightIsDown) else 0

		for keys in self.moveForwardKeys:
			allDown = True
			for key in keys:
				if not BigWorld.isKeyDown( key ):
					allDown = False
			if allDown:
				forwardCount += 1
		for keys in self.moveBackwardKeys:
			allDown = True
			for key in keys:
				if not BigWorld.isKeyDown( key ):
					allDown = False
			if allDown:
				forwardCount -= 1

		if forwardCount > 0:
			self.forwardMagnitude =  1.0
		elif forwardCount < 0:
			self.forwardMagnitude = -1.0
		else:
			self.forwardMagnitude =  0.0


	# -------------------------------------------------------------------------
	# Command: Additional Move Forward, but not when the free camera is on.
	# -------------------------------------------------------------------------
	def conditionalMoveForward(self, isDown):
		if not FantasyDemo.isFreeCamera():
			self.moveForward(isDown)

	# -------------------------------------------------------------------------
	# Command: Move Backward
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "MoveBackward" )
	def moveBackward(self, isDown):
		if isDown:
			leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
			rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )

			if rightIsDown and not leftIsDown:
				self.moveByStrafe = True
				self.physics.userDirected = True
				self.isMoving = True
				BigWorld.setCursor( BigWorld.dcursor() )
				self._enterMouseMove()

			self.autoMove = False
			if self.isMovingToDest:
				self.seeker.cancel( self )

			if self.physics.chasing:
				self.physics.stop()

			self._setForwardMagnitude()
			if self.mode == Mode.COMBAT_CLOSE:
				if self.stance == Avatar.STANCE_FORWARD:
					nst = Avatar.STANCE_NEUTRAL
				else:
					nst = Avatar.STANCE_BACKWARD
				self.takeStance( nst )
		else:
			self._setForwardMagnitude()

	# -------------------------------------------------------------------------
	# Command: Additional Move Back, but not when the free camera is on.
	# -------------------------------------------------------------------------
	def conditionalMoveBackward(self, isDown):
		if not FantasyDemo.isFreeCamera():
			self.moveBackward(isDown)

	# -------------------------------------------------------------------------
	# Command: Move Left
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "TurnLeft" )
	def moveLeft(self, isDown):
		if isDown:
			leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
			rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )

			if rightIsDown and not leftIsDown:
				self.moveByStrafe = True
				self.physics.userDirected = True
				self.isMoving = True
				BigWorld.setCursor( BigWorld.dcursor() )
				self._enterMouseMove()

			if self.isMovingToDest:
				self.seeker.cancel( self )

			if self.physics.chasing:
				self.physics.stop()

			self.rightwardMagnitude = max(self.rightwardMagnitude-1.0,-1.0)

			if self.inWoWMode and not self.moveByStrafe and not leftIsDown:
				self.enableEntityDirCamera()
		else:
			self.rightwardMagnitude = min(self.rightwardMagnitude+1.0,1.0)

	# -------------------------------------------------------------------------
	# Command: Additional Move Left, but not when the free camera is on.
	# -------------------------------------------------------------------------
	def conditionalMoveLeft(self, isDown):
		if not FantasyDemo.isFreeCamera():
			self.moveLeft(isDown)

	# -------------------------------------------------------------------------
	# Command: Move Right
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "TurnRight" )
	def moveRight(self, isDown):
		if isDown:
			leftIsDown = BigWorld.isKeyDown( Keys.KEY_LEFTMOUSE )
			rightIsDown = BigWorld.isKeyDown( Keys.KEY_RIGHTMOUSE )

			if rightIsDown and not leftIsDown:
				self.moveByStrafe = True
				self.physics.userDirected = True
				self.isMoving = True
				BigWorld.setCursor( BigWorld.dcursor() )
				self._enterMouseMove()

			if self.isMovingToDest:
				self.seeker.cancel( self )

			if self.physics.chasing:
				self.physics.stop()

			self.rightwardMagnitude = min(self.rightwardMagnitude+1.0,1.0)

			if self.inWoWMode and not self.moveByStrafe and not leftIsDown:
				self.enableEntityDirCamera()
		else:
			self.rightwardMagnitude = max(self.rightwardMagnitude-1.0,-1.0)

	# -------------------------------------------------------------------------
	# Command: Additional Move Right, but not when the free camera is on.
	# -------------------------------------------------------------------------
	def conditionalMoveRight(self, isDown):
		if not FantasyDemo.isFreeCamera():
			self.moveRight(isDown)

	# -------------------------------------------------------------------------
	# Command: Jump Up
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "Jump" )
	def jumpUp(self, isDown):
		if isDown:
			if self.isMovingToDest:
				self.seeker.cancel( self )

			self.upwardMagnitude = min(self.upwardMagnitude+1.0,1.0)
		else:
			self.upwardMagnitude = max(self.upwardMagnitude-1.0,-1.0)

	@BWKeyBindingAction( "FlyMode" )
	def toggleFlyMode( self, isDown ):
		if isDown:
			self.flying = 1 - self.flying
			self.physics.fall = 1 - self.flying
			if self.flying:
				FantasyDemo.addChatMsg( -1, "Fly Mode enabled" )
			else:
				FantasyDemo.addChatMsg( -1, "Fly Mode disabed" )

	# -------------------------------------------------------------------------
	# Command: Toggle Running/Walking Mode
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "SwitchToDash" )
	def switchToDash(self, isDown):
		if isDown:
			self.isDashing = 1
		else:
			self.isDashing = 0

	@BWKeyBindingAction( "SwitchToRun" )
	def switchToRun(self, isDown):
		if isDown:
			self.isRunning = 0
		else:
			self.isRunning = 1


	# -------------------------------------------------------------------------
	# Command: Toggle Cell Boundary Visualisation
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "CellBoundaryVisualisation" )
	def toggleCellBoundaryVisualisation(self, isDown=True):
		if isDown:
			self.showCellBoundsModel = not self.showCellBoundsModel
			self.setupCellBoundsModel()

			self.listeners.cellBoundsEnabled( self.showCellBoundsModel )

			if self.showCellBoundsModel:
				FantasyDemo.addChatMsg( -1, "Cell boundary visualisation enabled." )
			else:
				FantasyDemo.addChatMsg( -1, "Cell boundary visualisation disabled." )


	# -------------------------------------------------------------------------
	# Command: Toggle Turbo Movement Mode
	# -------------------------------------------------------------------------
	@BWKeyBindingAction( "TurboMovementMode" )
	def toggleTurboMovementMode(self, isDown):
		if isDown:
			if self.speedMultiplier > 25.0:
				self.speedMultiplier = 1.0
				FantasyDemo.addChatMsg( -1, 'Run Speed: Normal' )
			else:
				self.speedMultiplier = 2.0 * self.speedMultiplier
				FantasyDemo.addChatMsg( -1, 'Run Speed: x%(s)d'%{'s':int(self.speedMultiplier)} )

	# -------------------------------------------------------------------------
	# Command: Changes to Binocular mode on the player.
	# -------------------------------------------------------------------------
	def binocularsMode( self, enable ):
		if enable and self.guiModeSelected != 2:
			self.actionCommence()
			# make the screen look right
			FantasyDemo.handleCameraKey( forceToStandardCamera = True )

			# Change the turning half life to the camera moves into position immediately
			camera = BigWorld.camera()
			turningHalfLife = camera.turningHalfLife
			camera.turningHalfLife = 0.0
			def restoreTurningHalfLife():
				camera.turningHalfLife = turningHalfLife
			BigWorld.callback( 0.1, restoreTurningHalfLife )

			self.guiMode( 2 )

		elif self.guiModeSelected != 0:
			self.actionComplete()
			# make the screen look right
			self.guiMode( 0 )

	def setUsingCurrentItem( self, enable ):
		if enable:
			self.cell.enterMode( Mode.USING_ITEM, Mode.NO_TARGET, 0 )
			omode = self.mode; self.mode = Mode.USING_ITEM
			self.set_mode( omode )
		else:
			self.cell.cancelMode()
			omode = self.mode;	self.mode = Mode.NONE
			self.set_mode( omode )

	# -------------------------------------------------------------------------
	# Command: Toggle Collision Detection
	# -------------------------------------------------------------------------
	def toggleCollisionDetection(self, isDown):
		if isDown:
			# old style physics flag
			self.physics.collide = 1 - self.physics.collide
			# new style physics flags
			self.physics.collideTerrain = 1 - self.physics.collideTerrain
			self.physics.collideObjects = 1 - self.physics.collideObjects


	@BWKeyBindingAction( "NextPresetModel" )
	def nextPresetModel( self, isDown = True ):
		if isDown:
			if self.mode != Mode.NONE: return

			newAvatarModel = PlayerModel.nextPresetModel( AvatarModel.unpack( self.avatarModel ) )
			packedNewAvatarModel = AvatarModel.pack( newAvatarModel )
			if self._isConnected():
				self.base.setAvatarModel( packedNewAvatarModel )
			else:
				self.avatarModel = packedNewAvatarModel
				self.set_avatarModel()


	@BWKeyBindingAction( "PreviousPresetModel" )
	def previousPresetModel( self, isDown = True ):
		if isDown:
			if self.mode != Mode.NONE: return

			newAvatarModel = PlayerModel.previousPresetModel( AvatarModel.unpack( self.avatarModel ) )
			packedNewAvatarModel = AvatarModel.pack( newAvatarModel )
			if self._isConnected():
				self.base.setAvatarModel( packedNewAvatarModel )
			else:
				self.avatarModel = packedNewAvatarModel
				self.set_avatarModel()


	@BWKeyBindingAction( "NewRandomModel" )
	def newRandomModel( self, isDown = True ):
		if isDown:
			if self.mode != Mode.NONE: return
			
			newModel = AvatarModel.pack( PlayerModel.randomPlayerModel() )
			if self._isConnected():
				self.base.setAvatarModel( newModel )
			else:
				self.avatarModel = newModel
				self.set_avatarModel()

	@BWKeyBindingAction( "RandomiseModelCustomisations" )
	def randomiseModelCustomisations( self, isDown = True  ):
		if isDown:
			if self.mode != Mode.NONE: return
			
			oldModel = AvatarModel.unpack( self.avatarModel )
			newModel = PlayerModel.reCustomisePlayerModel( oldModel )
			if self._isConnected():
				self.base.setAvatarModel( AvatarModel.pack( newModel ) )
			else:
				self.avatarModel = AvatarModel.pack( newModel )
				self.set_avatarModel()


	# -------------------------------------------------------------------------
	# Commands: Switch To Next/Previous Inventory Item
	# -------------------------------------------------------------------------

	@BWKeyBindingAction( "SelectItem" )
	def selectItem( self, isDown, serialNumber ):
		if isDown and not self.doingAction:
			self.inventoryMgr.selectItem( serialNumber )
			self._checkStowAndEquip()

	@BWKeyBindingAction( "NextItem" )
	def nextItem( self, isDown ):
		if isDown and not self.doingAction:
			self.inventoryMgr.selectNextItem( self._filterItem )
			self._checkStowAndEquip()


	@BWKeyBindingAction( "PreviousItem" )
	def previousItem( self, isDown ):
		if isDown and not self.doingAction:
			self.inventoryMgr.selectPreviousItem( self._filterItem )
			self._checkStowAndEquip()


	def _filterItem( self, itemType, itemSerial ):
		'''Do not allow player to select a gun when he is seated
		'''
		return (
				self.mode != Mode.SEATED or
				not ItemLoader.lookupItem( itemType ).canShoot )


	def _checkStowAndEquip( self ):
		@IgnoreCallbackIfDestroyed
		def unstowItem( self, stowPlace ):
			if stowPlace == SHOULDER:
				self.stowToShoulderKey( True )
			elif stowPlace == RIGHT_HIP:
				self.stowToRightHipKey( True )
			elif stowPlace == LEFT_HIP:
				self.stowToLeftHipKey( True )

		try:
			itemIndex  = self.inventoryMgr.currentItemIndex()
			itemSerial = self.inventoryMgr.currentItemSerial()
			stowPlace  = self._stowSerial.index( itemSerial )
			self.inventoryMgr.selectItem( Inventory.NOITEM )
			self.equip( Item.Item.NONE_TYPE )
			BigWorld.callback( 0.4, partial( unstowItem, self, stowPlace ) )
		except ValueError:
			self.equip( self.inventoryMgr.currentItem() )

	# -------------------------------------------------------------------------
	# Command: stow items
	# -------------------------------------------------------------------------

	@BWKeyBindingAction( "StowToShoulder" )
	def stowToShoulderKey( self, isDown ):
		if self._stowItem( isDown, self.rightHand, self.shoulder, 'shoulder' ):
			if hasattr(self.model, "right_hand"):
				self.model.right_hand = None
			self.shoulder = self.rightHand
			self.cell.setShoulder( self.shoulder )
			self.set_shoulder()
			self._stowUpdateInventory( SHOULDER )


	@BWKeyBindingAction( "StowToRightHip" )
	def stowToRightHipKey( self, isDown ):
		if self._stowItem( isDown, self.rightHand, self.rightHip, 'right_hip' ):
			if hasattr(self.model, "right_hand"):
				self.model.right_hand = None
			self.rightHip = self.rightHand
			self.cell.setRightHip( self.rightHip )
			self.set_rightHip()
			self._stowUpdateInventory( RIGHT_HIP )


	@BWKeyBindingAction( "StowToLeftHip" )
	def stowToLeftHipKey( self, isDown ):
		if self._stowItem( isDown, self.rightHand, self.leftHip, 'left_hip' ):
			if hasattr(self.model, "right_hand"):
				self.model.right_hand = None
			self.leftHip = self.rightHand
			self.cell.setLeftHip( self.leftHip )
			self.set_leftHip()
			self._stowUpdateInventory( LEFT_HIP )


	def _stowItem( self, isDown, rightHandItem, stowedItem, hardPoint ):
		if not isDown or self.doingAction:# or self.inCombat():
			return False

		# refuse if item can't be stowed
		if rightHandItem != Item.Item.NONE_TYPE:
			try:
				self.getItem( rightHandItem ).model.node( 'HP_%s' % hardPoint )
			except ValueError:
				print 'Item model does not have hardpoint: HP_%s' % hardPoint
				return False

		# refuse if neighter the right hand nor the
		# stow place is vacant. Or if both are vacant
		holdingItem = rightHandItem != Item.Item.NONE_TYPE
		hasItemInSholder = stowedItem != Item.Item.NONE_TYPE
		if holdingItem == hasItemInSholder:
			return False

		return True


	def _stowUpdateInventory( self, stowPlace ):
		assert stowPlace in STOW_PLACES

		# equip old shoulder item
		oldSerial = self._stowSerial[ stowPlace ]
		try:
			self._stowSerial[ stowPlace ] = self.inventoryMgr.currentItemSerial()
		except ValueError:
			self._stowSerial[ stowPlace ] = Item.Item.NONE_TYPE

		itemType = self.inventoryMgr.selectItem( oldSerial )
		self.equip( itemType, 0 )

		# udpate inventory GUI
		itemIndex = self.inventoryMgr.currentItemIndex()

	# -------------------------------------------------------------------------
	# Command: input event handling
	# -------------------------------------------------------------------------

	def handleMouseEvent( self, event ):
		if self.inWoWMode:
			if self.onMouseMove:
				self.onMouseMove( event.dx, event.dy )
			if self.currentWebScreen != None:
				if self.currentWebScreen.handleMouseMove( event ):
					return True
			return 1
		return 0


	def handleKeyEvent( self, event ):
		if not self.inWorld or event.isRepeatedEvent():
			return False

		# If player is on a vehicle, redirect desired input to vehicle.
		if self.vehicle != None and hasattr( self.vehicle, 'handleKeyEvent' ):
			if self.vehicle.handleKeyEvent( event ):
				return True

		# Check key state against key bindings.
		FantasyDemo.rds.keyBindings.callActionForKeyState( event.key )

		# Update our velocity unless we've been dePlayerised
		# If we're not a PlayerAvatar anymore, the player either pressed
		# a key which yielded control to the server, or we were offline
		# and just reset the entityManager.
		if hasattr( self, "updateVelocity" ):
			self.updateVelocity()

		return False

	def setUpMovementSpeedsFromModel( self ):
		"""
		Set up our movement speeds from the animations.
		In future, we may not want to do this for gameplay reasons,
		but for now it looks best when played at the right speed.
		"""

		self.walkFwdSpeed = 1.0
		self.runFwdSpeed = 2.0
		self.dashFwdSpeed = 2.5
		try:
			self.walkFwdSpeed = self.model.WalkForward.displacement[2] / \
				self.model.WalkForward.duration
			self.runFwdSpeed = self.model.RunForward.displacement[2] / \
				self.model.RunForward.duration
			self.dashFwdSpeed = self.model.DashForward.displacement[2] / \
				self.model.DashForward.duration
		except:
			pass

		self.walkBackSpeed = 1.0
		self.runBackSpeed = 2.0
		self.dashBackSpeed = 2.5
		try:
			self.walkBackSpeed = - self.model.WalkBackward.displacement[2] / \
				(self.model.WalkBackward.duration * 1.5)
			self.runBackSpeed = - self.model.RunBackward.displacement[2] / \
				(self.model.RunBackward.duration * 1.5)
			self.dashBackSpeed = - self.model.RunBackward.displacement[2] / \
				(self.model.RunBackward.duration * 1.5)
		except:
			pass

		# Store our full movement rates.
		self.fullWalkFwdSpeed = self.walkFwdSpeed
		self.fullRunFwdSpeed = self.runFwdSpeed
		self.fullDashFwdSpeed = self.dashFwdSpeed
		self.fullWalkBackSpeed = self.walkBackSpeed
		self.fullRunBackSpeed = self.runBackSpeed
		self.fullDashBackSpeed = self.dashBackSpeed

		# Set up our tired movement rates.
		self.tiredWalkFwdSpeed = self.walkFwdSpeed
		self.tiredRunFwdSpeed = self.runFwdSpeed
		self.tiredDashFwdSpeed = self.runFwdSpeed
		self.tiredWalkBackSpeed = self.walkBackSpeed
		self.tiredRunBackSpeed = self.runBackSpeed
		self.tiredDashBackSpeed = self.runBackSpeed


	# Update the velocity set in our physics controller
	def updateVelocity( self ):

		seeking = False
		if (self.isMovingToDest or
		   (hasattr(self, 'physics') and self.physics.seeking == 1)):
			seeking = True

		# If we're chasing only allow strafing left and right
		if self.physics.chasing:
			#self.physics.velocity = ( self.rightwardMagnitude, 0, 1.5 )
			self.physics.velocity = ( 0, 0, 1.5 )
			return

		# Find out how fast we can go
		if self.isDashing:
			if self.forwardMagnitude >= 0:
				multiplier = self.dashFwdSpeed
			else:
				multiplier = self.dashBackSpeed
		elif self.isRunning:
			if self.forwardMagnitude >= 0:
				multiplier = self.runFwdSpeed
			else:
				multiplier = self.runBackSpeed
		else:
			if self.forwardMagnitude >= 0:
				multiplier = self.walkFwdSpeed
			else:
				multiplier = self.walkBackSpeed

		# The two magnitude values, forwardMagnitude and leftwardMagnitude
		# should lie between 0.0 and 1.0. The vector sum of their values
		# should also lie between 0.0 and 1.0.
		rightwardMagnitude = max(self.rightwardMagnitude,-1.0)
		rightwardMagnitude = min(rightwardMagnitude,1.0)
		forwardMagnitude = max(self.forwardMagnitude,-1.0)
		forwardMagnitude = min(forwardMagnitude,1.0)
		upwardMagnitude = self.upwardMagnitude
		hypotenuse = math.sqrt( forwardMagnitude * forwardMagnitude +
			rightwardMagnitude * rightwardMagnitude )
		if hypotenuse > 1.0:
			forwardMagnitude /= hypotenuse
			rightwardMagnitude /= hypotenuse

		# Check if the Entity should temporarily discount movement. Currently
		# movement should be disabled for gestures and first-person mode.
		if (self.doingAction and self.doingMovableAction < self.doingAction) or \
				self.mode == Mode.SEATED:
				#self.firstPerson or self.mode == Mode.SEATED:
			forwardMagnitude = 0.0
			rightwardMagnitude = 0.0
			upwardMagnitude = 0.0

			# cancel seeking
			if seeking:
				self.seeker.cancel( self )
				seeking = False

		if seeking:
			self.seeker.updateVelocity( self )
			return

		turnMultiplier = multiplier * min( self.speedMultiplier, 8.0 )
		multiplier = multiplier * self.speedMultiplier

		self.physics.brake = 0

		if self.inWoWMode and not self.moveByStrafe:
			self.physics.angular = rightwardMagnitude * turnMultiplier / 3.0
			self.physics.velocity = ( 0,
				upwardMagnitude * multiplier,
				forwardMagnitude * multiplier )
		else:
			self.physics.velocity = (
				rightwardMagnitude * multiplier,
				upwardMagnitude * multiplier,
				forwardMagnitude * multiplier )

		if self.flying or upwardMagnitude > 0:
			self.physics.fall = 0
		else:
			#prevent failling if a fly through is running. We want fly through
			#to be flying all the time (to prevent falling into water)
			if not BigWorld.flyThroughRunning():
				self.physics.fall = 1

		# Set joystick velocity override parameters
		if (self.doingMovableAction or not self.doingAction) and \
				self.mode != Mode.SEATED:
				#(not self.firstPerson) and self.mode != Mode.SEATED:

			#AUSTIN GDC - move all matchCaps into items
			#if 6 in self.am.matchCaps:
			#	jspeeds = ( self.runFwdSpeed, self.sneakBackSpeed,
			#				self.dashFwdSpeed, self.sneakBackSpeed )
			#elif 7 in self.am.matchCaps:
			#	jspeeds = ( self.crouchFwdSpeed, self.crouchBackSpeed,
			#				self.crouchFwdSpeed, self.crouchBackSpeed )
			#elif 3 in self.am.matchCaps:
			#	jspeeds = ( self.runFwdSpeed, self.runBackSpeed,
			#				self.runFwdSpeed, self.runBackSpeed )
			#else:
			jspeeds = ( self.runFwdSpeed, self.runBackSpeed,
						self.dashFwdSpeed, self.dashBackSpeed )
		else:
			jspeeds = ( 0, 0, 0, 0 )

		if not self.isDashing:
			self.physics.joystickFwdSpeed = jspeeds[0]
			self.physics.joystickBackSpeed = jspeeds[1]
		else:
			self.physics.joystickFwdSpeed = jspeeds[2]
			self.physics.joystickBackSpeed = jspeeds[3]

	#
	# PlayerAvatar C++ Interface Note:
	# The identifier 'model' refers to the C++ Python Object Model.
	#
	# Hard points for a model can be accessed as if they were a normal variable
	# of type 'Model'. That is, a hard point may be set to a 'Model' object by
	# direct assignment.
	#
	# eg. self.model.right_hand = "objects/models/gun.model" will attach the gun
	#     model to the model's right hand.
	#
	# Sample HardPoint Names:
	#     right_hand, left_hand, shoulder, right_hip
	#
	# The model can be told to do an action (ie. animation) by specifying the
	# action name as listed in the XML file. This is the name listed by the
	# tag <name>.
	#
	# eg1. self.model.Idle() will cause the model to play the
	#      Idle action's animation immediately without a call-back function.
	#
	# eg2. self.model.BendDown( 0, callBackIdle ) will cause the
	#      BendDown action's animation to be played immediately, specifying
	#      callBackIdle() to be called upon completion of the animation.
	#

	# The identifier 'filter' refers to the type of filtering used for the
	# Entity's movement.

	def unequipItem( self ):
		item = self.inventoryMgr.selectItem( -1 )
		self.equip( item )


	def equip( self, itemType, itemChangeAnim = 1 ):
		if self.rightHand == itemType:
			return

		self.rightHand = itemType          # change localy
		self.cell.setRightHand( itemType ) # tell the world
		self.set_rightHand( itemChangeAnim = itemChangeAnim )



	def setCombatStance( self ):
		self.listeners.combatStanceUpdated( self.inCombat() )
		if self.inCombat():
			# change to combat

			# set target caps to type of combat
			if self.inMeleeCombat():
				# set the entity target picker to choose things we can melee attack
				BigWorld.target.caps( Caps.CAP_CAN_MELEE )
			else:
				# set the entity target picker to choose things we can shoot at
				BigWorld.target.caps( Caps.CAP_CAN_HIT )
				self.cell.enterCombat()

			# if we are targeting something, call focus target to update the reticle.
			if BigWorld.target() != None:
				self.targetFocus( BigWorld.target() )

		else:
			self.set_rightHand( itemChangeAnim = 0 )

			# tell server (and thus all other clients) we have changed mode
			if not self.inMeleeCombat():
				self.cell.leaveCombat()

	# Target focus notifier
	def targetFocus( self, entity ):
		if self.tracker.directionProvider == None:
			return
		if not BigWorld.target.isFull:
			return # doesn't fully match the right target.caps

		FantasyDemo.rds.fdgui.targetFocus( entity )
		
		# if we don't want the players focus, don't rotate the head.
		if hasattr(entity, "grabFocus") and not entity.grabFocus:
			return

		if self.inCombat():
			self.enableTracker( self.gunAimingNodeInfo )
		else:
			self.enableTracker( self.headNodeInfo )
		try:
			self.tracker.directionProvider = BigWorld.DiffDirProvider(
					self.focalMatrix, entity.focalMatrix )
		except:
			self.tracker.directionProvider = BigWorld.DiffDirProvider(
					self.focalMatrix, entity.model.matrix )

	# Target blur notifier
	def targetBlur( self, entity ):
		FantasyDemo.rds.fdgui.targetBlur( entity )

		if self.tracker.directionProvider == None:
			return

		if not self.doingAction:
			self.enableTracker( self.headNodeInfo )

		if self.mode != Mode.DEAD:
			self.tracker.directionProvider = self.entityDirProvider

	# Handle a console command
	def handleConsoleCommand( self, command, theRest = "" ):
		lcommand = command.lower()
		candidates = [ x for x in ConsoleCommands.__dict__.keys() \
						if x.lower().startswith( lcommand ) ]
		#lcommand = unicode( command.lower() )
		#candidates = [ unicode(x) for x in ConsoleCommands.__dict__.keys() \
		#				if unicode(x).lower().startswith( lcommand ) ]

		if len(candidates) > 1:
			exactCandidates = [ x for x in candidates if x.lower() == lcommand ]
			if len(exactCandidates) >= 1:
				candidates = exactCandidates
				if len(candidates) > 1:
					exactCaseCandidates = [ x for x in candidates \
											if x == command ]
					if len(exactCaseCandidates) == 1:
						candidates = exactCaseCandidates

		if len(candidates) == 1:
			getattr( ConsoleCommands, candidates[0] )( self, theRest )
		elif len(candidates) > 1:
			FantasyDemo.addChatMsg( -1, "Ambiguous command '/" + command + \
									"' matches " + str(candidates) )
		else:
			FantasyDemo.addChatMsg( -1, "Unknown command '/" + command + "'" )

	# Handle this string typed at the console
	def handleConsoleInput( self, string ):
		if len(string) > 0 and string[0] == '/':
			FantasyDemo.addChatMsg( -1, string )
			self.handleConsoleCommand( *(string[1:].split( ' ', 1 )) )
		else:
			self.cell.chat( unicode(string) )
			FantasyDemo.addChatMsg( self.id, string )



	# The user wants to shonk
	@BWKeyBindingAction( "ShonkPaper", 0 )
	@BWKeyBindingAction( "ShonkScissors", 1 )
	@BWKeyBindingAction( "ShonkRock", 2 )
	def shonkKey( self, which, isDown = True ):
		if not isDown: return
		if self.doingAction or self.inCombat(): return
		if self.physics.inWater: return
		if self.mode != Mode.NONE: return

		t = BigWorld.target()
		if t == None:
			print "PlayerAvatar::shonkKey: Shonk with who?"
			return

		if not Caps.CAP_CAN_SHONK in t.targetCaps:
			print "PlayerAvatar::shonkKey: not Shonkable"
			return

		# ok, is t already waiting to shonk with us?
		if t.mode == Mode.SHONK and t.modeTarget == self.id:
			self.moveActionCommence()

				# should use some other calc here
			self.seeker.seekPath( self,
				t.model.Shake_B_Accept.seekInv,
				self.walkFwdSpeed,
				5.0,
				0.30,
				partial( self.shonkFound, t, which ) )
		else:
			# tell the server we want to do this
			self.cell.enterMode( 0, BigWorld.target().id, which )


			# just wait for its reply for now, but should
			#  enter the mode here ourselves anyway, like this:
			# self.mode = Mode.SHONK
			# self.set_mode( Mode.NONE )

	def shonkFound( self, t, which, success ):
		# did we make it?
		if not success:
			self.model.Shrug( 0, self.actionComplete )
			return

		# yay we're there!
		t.cell.answerMode( Mode.SHONK, self.id, which )
		# could do something before server reply here too...


	# The user wants to crouch
	@BWKeyBindingAction( "Crouch" )
	def crouchKey( self, isDown = 1 ):
		if not isDown: return
		if self.physics.inWater: return

		if self.mode == Mode.CROUCH:
			self.cell.cancelMode()
			self.mode = Mode.NONE
			self.set_mode( Mode.CROUCH )
		elif self.mode == Mode.NONE and not self.doingAction:
			self.cell.enterMode( Mode.CROUCH, Mode.NO_TARGET, 0 )
			self.mode = Mode.CROUCH
			self.set_mode( Mode.NONE )

		# else do nothing...

	# The user wants to shake hands with someone
	@BWKeyBindingAction( "Handshake" )
	def handshakeKey( self, isDown = 1 ):
		if not isDown: return
		if self.doingAction or self.inCombat(): return
		if self.physics.inWater: return
		if self.mode != Mode.NONE: return

		newMode = Mode.HANDSHAKE

		t = BigWorld.target()
		if t == None:
			print "PlayerAvatar::handshakeKey: Shake hands with who?"
			return

		# ok, is t already waiting to shake hands with us?
		if t.mode == Mode.HANDSHAKE and t.modeTarget == self.id:
			# Has the target started its idle loop yet?
			#~ if not t.inIdle:
				#~ return

			self.moveActionCommence()

			self.seeker.seekPath( self,
				t.model.Shake_B_Accept.seekInv,
				self.walkFwdSpeed,
				5.0,
				0.10,
				partial( self.handshakeFound, t ) )
		else:
			# tell the server we want to do this
			self.cell.enterMode( newMode, BigWorld.target().id, 0 )

			# just wait for its reply for now, but should
			#  enter the mode here ourselves anyway, like this:
			# self.mode = newMode
			# self.set_mode( Mode.NONE )

	def handshakeFound( self, t, success ):
		# did we make it?
		if not success or not t.mode == Mode.HANDSHAKE:
			self.model.Shrug( 0, self.actionComplete )
			return

		# yay we're there!
		t.cell.answerMode( t.mode, self.id, 0 )


	# The user wants to lift someone up
	@BWKeyBindingAction( "PullUp" )
	def pullUpKey( self, isDown = 1 ):
		if not isDown: return
		if self.doingAction or self.inCombat(): return
		if self.physics.inWater: return
		if self.mode != Mode.NONE: return

		if self.rightHand != Item.Item.NONE_TYPE:
			self.unequipItem()

		t = BigWorld.target()
		if t == None:
			print "PlayerAvatar::pullUpKey: Pull up who?"
			return

		# ok, is t already waiting to lift us up?
		if t.mode == Mode.PULLUP and t.modeTarget == self.id:
			self.pullUpPassive( t )
		else:
			#try:
				sofa = self.pullUpActive( t )
				if sofa and sofa < 0:
					print "pullUp: Got to step ", -sofa
			#except Exception, e
			#	print "pullUp: Got to an exception: ", e


	# This function may throw an exception if all is not right
	def pullUpActive( self, t ):
		# OK, see if we can do a pull up from here...
		FDP = BigWorld.findDropPoint
		bumpy = 0.2		# must be < 20cm difference

		# first find the triangle underneath us
		dir = Vector3( math.sin(self.yaw), 0, math.cos(self.yaw) )

		(rfall,rtri) = FDP( self.spaceID, Vector3(self.position) + Vector3(0,2,0) )

		# now while we haven't gone too far
		distOver = 0
		loopCount = 0
		while distOver < 1.5 and loopCount < 10:

			# find the point we want to jump from
			(edge, edgeYaw) = intersectRayWithPolygon( rfall, dir, rtri )

			# peek just over the edge to see if there's an adjoining polygon
			justOver = edge + dir.scale(0.05) + Vector3(0,2,0)
			(nrfall,nrtri) = FDP( self.spaceID, justOver )

			if abs( nrfall.y - edge.y ) > bumpy:
				break	# there isn't, this looks good then

			# ok, there is, try that then
			justOver.y = rfall.y
			distOver += (rfall - justOver).length

			rfall = nrfall
			rtri = nrtri

			loopCount += 1

		edgeup = Vector3( edge.x, edge.y + 2.0, edge.z )
		edgeunder = Vector3( edge.x, edge.y - 1.1, edge.z )
		topH = rfall.y
		botH = rfall.y - 5.0

		# is there space 1.9m behind the edge?
		if abs( FDP( self.spaceID, edgeup - dir.scale(1.9) )[0].y - topH ) > bumpy: return -1

		# is there space 1m behind the edge?
		if abs( FDP( self.spaceID, edgeup - dir )[0].y - topH ) > bumpy: return -2

		# is there space 10cm behind the edge?
		if abs( FDP( self.spaceID, edgeup - dir.scale(0.1) )[0].y - topH ) > bumpy: return -3

		# is there space 10cm over the edge?
		if abs( FDP( self.spaceID, edgeup + dir.scale(0.1) )[0].y - botH ) > bumpy: return -4

		# is there space 90cm over the edge?
		if abs( FDP( self.spaceID, edgeup + dir.scale(0.9) )[0].y - botH ) > bumpy: return -5

		# is there space 10cm under the edge?
		if abs( FDP( self.spaceID, edgeunder - dir.scale(0.1) )[0].y - botH ) > bumpy: return -6

		# is there space 90cm under the edge?
		if FDP( self.spaceID, edgeunder - dir.scale(0.9) )[0].y > topH - 1.0: return -7

		# ok, that'll have to do then.
		self.moveActionCommence()
		stdist = self.model.PullUpActiveBegin.displacement[2] - 1.80;

		self.seeker.seekPath( self,
			tuple( (edge - dir.scale(stdist)).list() + [ edgeYaw ] ),
			self.walkFwdSpeed,
			5.0,
			0.10,
			partial( self.pullUpActiveFound, t) )

		# tell the server we want to do it


	def pullUpActiveFound( self, t, success ):
		if not success:
			self.model.Shrug( 0, self.actionComplete )
		else:
			self.cell.enterMode( Mode.PULLUP, t.id, 0 )


	def pullUpPassive( self, t ):
		self.moveActionCommence()

		self.seeker.seekPath( self,
			t.model.PullUpActiveBegin.seek,
			self.walkFwdSpeed,
			5.0,
			0.10,
			partial( self.pullUpPassiveFound, t ) )


	def pullUpPassiveFound( self, t, success ):
		# did we make it?
		if not success:
			self.model.Shrug( 0, self.actionComplete )
			return

		# yay we're there!
		self.am.matcherCoupled = 0
		#BigWorld.callback( 1.0, partial( t.cell.answerMode,
		#	Mode.PULLUP, self.id, 0 ) )
		t.cell.answerMode( Mode.PULLUP, self.id, 0 )


	# The user wants to bunk someone up
	@BWKeyBindingAction( "PushUp" )
	def pushUpKey( self, isDown = 1 ):
		if not isDown: return
		if self.doingAction or self.inCombat(): return
		if self.physics.inWater: return
		if self.mode != Mode.NONE: return

		if self.rightHand != Item.Item.NONE_TYPE:
			self.unequipItem()

		t = BigWorld.target()
		if t == None:
			print "PlayerAvatar::pushUpKey: Push up who?"
			return

		# ok, is t already waiting to lift us up?
		if t.mode == Mode.PUSHUP and t.modeTarget == self.id:
			self.pushUpPassive( t )
		else:
			#try:
				sofa = self.pushUpActive( t )
				if sofa and sofa < 0:
					print "pushUp: Got to step ", -sofa
			#except Exception, e
			#	print "pullUp: Got to an exception: ", e


	# This function may throw an exception if all is not right
	def pushUpActive( self, t ):
		# OK, see if we can do a pull up from here...
		FDP = BigWorld.findDropPoint
		bumpy = 0.2		# must be < 20cm difference

		# first find the triangle above us
		dir = Vector3( math.sin(self.yaw), 0, math.cos(self.yaw) )

		distBack = 1.5
		loopCount = 0

		droppt = Vector3( self.position ) - dir.scale(distBack) + Vector3(0,7,0)
		(rfall,rtri) = FDP( self.spaceID, droppt )

		# now while we're not too close to the player...
		while distBack > 0.3 and loopCount < 10:

			# find the point we want to grab onto
			(edge, edgeYaw) = intersectRayWithPolygon( rfall, dir, rtri )

			# peek just over the edge to see if there's an adjoining polygon
			justOver = edge + dir.scale(0.05)
			justOver.y += 2.0
			(nrfall,nrtri) = FDP( self.spaceID, justOver )

			if abs( nrfall.y - edge.y ) > bumpy:
				break	# there isn't, this looks good then

			# ok, there is, try that then
			justOver.y = rfall.y
			distBack -= (rfall - justOver).length

			rfall = nrfall
			rtri = nrtri

			loopCount += 1

		edgeup = edge + Vector3( 0, 2.0, 0 )
		edgeunder = edge + Vector3( 0, -1.1, 0 )
		topH = rfall.y
		botH = rfall.y - 5.0

		# is there space 0.9m behind the edge?
		if abs( FDP( self.spaceID, edgeup - dir.scale(0.9) )[0].y - topH ) > bumpy: return -2

		# is there space 10cm behind the edge?
		if abs( FDP( self.spaceID, edgeup - dir.scale(0.1) )[0].y - topH ) > bumpy: return -3

		# is there space 10cm over the edge?
		if abs( FDP( self.spaceID, edgeup + dir.scale(0.1) )[0].y - botH ) > bumpy: return -4

		# is there space 90cm over the edge?
		if abs( FDP( self.spaceID, edgeup + dir.scale(0.9) )[0].y - botH ) > bumpy: return -5

		# is there space 10cm under the edge?
		if abs( FDP( self.spaceID, edgeunder - dir.scale(0.1) )[0].y - botH ) > bumpy: return -6

		# is there space 90cm under the edge?
		if FDP( self.spaceID, edgeunder - dir.scale(0.9) )[0].y > topH - 1.0: return -7

		# ok, that'll have to do then.
		self.moveActionCommence()
		stdist = self.model.PushUpPassiveAccept.displacement[2] - \
			self.model.PushUpActiveBegin.displacement[2] + 0.09;
		tgtpos = Vector3(edge.x, edge.y - 5, edge.z) + dir.scale(stdist)

		print "edge ", edge, ", stdist ", stdist, ", tgtpos ", tgtpos
		self.seeker.seekPath( self,
			tuple( tgtpos.list() + [ edgeYaw ] ),
			self.walkFwdSpeed,
			5.0,
			0.10,
			partial( self.pushUpActiveFound, t) )


	def pushUpActiveFound( self, t, success ):
		if not success:
			self.model.Shrug( 0, self.actionComplete )
		else:
			self.cell.enterMode( Mode.PUSHUP, t.id, 0 )


	def pushUpPassive( self, t ):
		self.moveActionCommence()

		self.seeker.seekPath( self,
			t.model.PushUpActiveBegin.seek,
			self.walkFwdSpeed,
			5.0,
			0.10,
			partial( self.pushUpPassiveFound, t ) )


	def pushUpPassiveFound( self, t, success ):
		# did we make it?
		if not success:
			self.model.Shrug( 0, self.actionComplete )
			return
		self.am.matcherCoupled = 0
		# yay we're there!
		#BigWorld.callback( 1.0, partial( t.cell.answerMode,
		#	Mode.PUSHUP, self.id, 0 ) )
		t.cell.answerMode( Mode.PUSHUP, self.id, 0 )


	# Override from Avatar
	def assail( self ):
		# We don't call Avatar's assail method, because we've already
		# swung the sword. We only get here if the swing didn't
		# begin combat. So we just call actionComplete
		self.actionComplete()

	CLOSE_COMBAT_DISTANCE = 1.5

	# Override from Avatar
	def enterCloseCombatMode( self ):
		Avatar.enterCloseCombatMode( self )

		# We may be in close combat mode but the fight doesn't start
		#  until the server says so (by sending the first packet)
		self.ccPlayerFighting = 0

		self.ccDefence = 100

		if self.ccTarget == None: return

		print "Player now chasing", self.ccTarget.name(), \
			"(id %d)" % self.ccTarget.id
		self.physics.chase( self.ccTarget, PlayerAvatar.CLOSE_COMBAT_DISTANCE, 0.05 )
		self.physics.userDirected = 0
		self.updateVelocity()


	# Override from Avatar
	def leaveCloseCombatMode( self ):
		self.physics.chase( None, 0 )
		self.physics.userDirected = 1
		self.updateVelocity()

		print "Player no longer chasing anyone"

		Avatar.leaveCloseCombatMode( self )


	# Override from Avatar:
	def closeCombatGo( self, assailant, weAreInitiator ):
		if not hasattr( self, "ccPlayerFighting" ): return

		Avatar.closeCombatGo( self, assailant, weAreInitiator )

		if not self.ccPlayerFighting and self.ccTarget:
			#~ BigWorld.targetLockOn( self.ccTarget )
			self.ccPlayerFighting = 1

		self.physics.chase( None, 0 )
		self.updateVelocity()

	#Override from Avatar:
	def closeCombatNo( self, assailant, weAreInitiator ):
		if not hasattr( self, "ccPlayerFighting" ): return

		if self.ccPlayerFighting:
			#~ BigWorld.targetLockOn( None )
			self.ccPlayerFighting = 0

			BigWorld.callback( 2.5, partial( self.closeCombatAutoExit, assailant ) )

		Avatar.closeCombatNo( self, assailant, weAreInitiator )

		# Consider putting the chase back in here ... sort all this
		# out when multiple opponents are done

	# This is a very tentative function to exit CC mode if there
	# is no longer any reson for us to be in it: i.e. our opponent
	# has broken or died
	@IgnoreCallbackIfDestroyed
	def closeCombatAutoExit( self, assailant ):
		# see if we're still fighting the same entity
		if self.mode != Mode.COMBAT_CLOSE: return
		if self.modeTarget != assailant.id: return

		# make sure they're not still fighting us
		if assailant.mode == Mode.COMBAT_CLOSE and \
			assailant.modeTarget == self.id: return

		# ok, let's get out of it then
		self.cell.cancelMode()



	#Override from Avatar:
	def ccPassiveAction( self, res ):
		defMove = res & 7
		if defMove == Avatar.CL_DESPERATE:
			self.ccDefence -= 10
		elif defMove == Avatar.CL_HIT:
			self.ccDefence -= 10
		if self.ccDefence < 0: self.ccDefence = 0
		return Avatar.ccPassiveAction( self, res )

	# This method is called when the player is attacked by another entity
	def ccRespond( self, oth ):
		print "Responding to the attack of ", oth.id, "..."
		self.ccLastAttacker = None

		# Ignore it if we're already doing something
		if self.mode != Mode.NONE or self.doingAction != 0:
			if self.mode == Mode.COMBAT_CLOSE and self.modeTarget == oth.id:
				print "... already attacking this entity"
			else:
				print "... doing something else"
				# Remember our attacker and try again later
				self.ccLastAttacker = oth
			return

		# Change to the sword if we have one
		tempRH = self.getItem( self.rightHand )
		if not tempRH or not tempRH.canSwing:
			def isWield( item ):
				return ItemLoader.lookupItem( item )[0] == Item.Wield
			if self.inventoryMgr.selectSuitableItem( isWield ):
				self.equip( self.inventoryMgr.currentItem(), 0 )
			else:
				print "... no Wield item found in inventory"
				return

		# Find out where they are
		dir = Vector3( self.position ) - Vector3( oth.position )
		if dir.lengthSquared > 0.01: dir.normalise()
		else: dir = Vector3(0,0,1)
		pos = Vector3( oth.position ) + dir.scale( PlayerAvatar.CLOSE_COMBAT_DISTANCE )
		yaw = math.atan2( dir.x, dir.z )

		# Come after this challenger!
		self.moveActionCommence()

		self.seeker.seekPath( self,
			(pos.x,pos.y,pos.z,yaw+math.pi),
			self.runFwdSpeed,
			5.0,
			1.0,
			partial( self.ccRespondOver, oth ) )

	def ccRespondOver( self, oth, success ):
		self.actionComplete()

		# If we didn't get there then give up
		if not success:
			print "... could not reach assailant"
			return

		# Otherwise have at them
		print "... target reached."
		tempRH = self.rightHandItem
		if not tempRH: tempRH = self.getItem( self.rightHand )
		self.closeCombatCommence( tempRH, oth )


	def set_avatarModel( self, oldValue = None ):
		def onModelChanged():
			self.setUpMovementSpeedsFromModel()
			self.set_rightHand( itemChangeAnim = 0 )
			self.set_shoulder()
			self.set_rightHip()
			self.set_leftHip()

		Avatar.set_avatarModel( self, oldValue, onModelChanged )


	# Override from Avatar
	def set_rightHand( self, oldRH = None, itemChangeAnim = 1 ):
		Avatar.set_rightHand( self, oldRH, itemChangeAnim )

	# Override from Avatar
	def set_rightHandEnd( self, itemChangeAnim ):
		oldCombatStance = self.inCombat()
		Avatar.set_rightHandEnd( self, itemChangeAnim )

		# go in or out of combat stance if we need to
		if oldCombatStance != self.inCombat():
			self.setCombatStance()

		# TODO : this should be a PlayerAvatar override of the
		# setRightHandLock method, just in case an item uses its
		# model in equipByPlayer.
		if self.rightHandItem != None:
			self.rightHandItem.equipByPlayer( self )
		else:
			BigWorld.target.caps( Caps.CAP_CAN_USE )

	def _initHealth( self, oldHealth = None ):
		Avatar.set_healthPercent( self, oldHealth )

	def recoil( self, shooter, lockAccuracy ):
		Avatar.recoil( self, shooter, lockAccuracy )

	# Pressed a stance-changing key in close combat mode
	def takeStance( self, newStance ):
		self.cell.setStance( newStance )
		self.stance = newStance
		self.set_stance()

	# An item is telling us that the player should go into close combat mode
	def closeCombatCommence( self, item, target ):
		item.enact(self,target)				# Play the swing

		return # close combat has been disabled until further notice

		if not self._isConnected(): return

		tid = 0
		if target != None:
			tid = target.id
			self.modeTarget = tid				# modeTarget is an OTHER_CLIENT property
		else:
			self.modeTarget = Mode.NO_TARGET	# modeTarget is an OTHER_CLIENT property

		self.stance = Avatar.STANCE_NEUTRAL	# so is stance
		self.cell.assail( tid )			# Tell server about it

		# TODO: Shouldn't do this if no target...
		self.moveActionCommence()				# Wait for result of swing
											#  (so can't change item)

		# Seek to correct position if target is already attacking us
		if target != None and isinstance( target, Avatar ):
			if target.mode == Mode.COMBAT_CLOSE and target.modeTarget == self.id:
				pos = Vector3( target.position )
				yaw = target.yaw
				dir = Vector3( math.sin( yaw ), 0, math.cos( yaw ) )
				pos += dir.scale( PlayerAvatar.CLOSE_COMBAT_DISTANCE )

				# 5s time out, 1m acceptable height difference, no callback
				self.seeker.seekPath( self,
					(pos.x,pos.y,pos.z,yaw+math.pi),
					self.runFwdSpeed,
					5.0,
					1.0 )


	# The player wants to make an attack
	def closeCombatSwing( self ):
		# We now always tell the server when we want to attack,
		# regardless of whether or not the fight has started or
		# we're doing an animation due to the last result message.
		# The server sorts it all out and takes action when it feels like it
		self.cell.setStance( 100 )

		# We need to set a variable here to indicate that we have an attack
		# request outstanding, then do some client tricks to decide when
		# to play the filler: basically, whenever our mode target is also
		# in close combat with us, and we have an attack request in the
		# pipeline, and we're not playing another animation. The tricky
		# bit will be that when the target goes into combat mode (and
		# before the fight has started for real), there'll have to be a
		# method that gets called on us so we can start the filler if
		# we have a swing in the queue... or something.

		#if not self.ccFightStarted: return
		# obv. needs to check previous action finished
		#self.cell.setStance( 100 )
		#self.model.CCFwdActFill()
		#try:
		#	self.ccTarget.model.CCAnyPasFill()
		#except:
		#	pass


	def onNarrowTarget( self, isEnter ):
		pass


	#
	# Returns true if client is connected to BW server
	#
	def _isConnected( self ):
		return bool( BigWorld.server() )
		

	#
	# GDC 2007
	#
	# toggle 'fast' Time of Day mode
	@BWKeyBindingAction( "DemoKey1" )
	def demoKey1( self, isDown ):
		if isDown:
			if not hasattr( self, "demoKey1Pressed" ):
				BigWorld.setWatcher( "Client Settings/Secs Per Hour", 1.0 )
				self.demoKey1Pressed = True
			else:
				BigWorld.setWatcher( "Client Settings/Secs Per Hour", 99999.0 )
				BigWorld.setWatcher( "Client Settings/Time of Day", 15.0 )
				del self.demoKey1Pressed


	#
	# GDC 2007
	#
	# teleport to area 1, outside the dungeon
	@BWKeyBindingAction( "DemoKey2" )
	def demoKey2( self, isDown ):
		if isDown:
			self.tryToTeleport( "", "demo1" )


	#
	# GDC 2007
	#
	# teleport to area 2, near the wharf in the fishing village
	@BWKeyBindingAction( "DemoKey3" )
	def demoKey3( self, isDown ):
		if isDown:
			self.tryToTeleport( "", "demo2" )


	#
	# GDC 2007
	#
	# teleport to area 3, near the orc spawner
	@BWKeyBindingAction( "DemoKey4" )
	def demoKey4( self, isDown ):
		if isDown:
			self.tryToTeleport( "", "demo3" )


	#
	# GDC 2007
	#
	# teleport to area 4, the starting point
	@BWKeyBindingAction( "DemoKey5" )
	def demoKey5( self, isDown ):
		if isDown:
			self.tryToTeleport( "", "demo4" )


	#
	# GDC 2008
	#
	# Toggle random weather changes (client-only so as not to interrupt
	# other demo machines)
	@BWKeyBindingAction( "DemoKey0" )
	def demoKey0( self, isDown ):
		if isDown:
			import Weather
			Weather.weather().toggleRandomWeather()


	#
	# GDC 2008
	#
	# Immediately loop to the previous weather system
	@BWKeyBindingAction( "DemoKeyMinus" )
	def demoKeyMinus( self, isDown ):
		if isDown:
			import Weather
			Weather.weather().nextWeatherSystem( False, True )

	#
	# GDC 2008
	#
	# Immediately loop to the next weather system
	@BWKeyBindingAction( "DemoKeyEquals" )
	def demoKeyEquals( self, isDown ):
		if isDown:
			import Weather
			Weather.weather().nextWeatherSystem( True, True )

	@BWKeyBindingAction( "Gesture00",  0 )
	@BWKeyBindingAction( "Gesture01",  1 )
	@BWKeyBindingAction( "Gesture02",  2 )
	@BWKeyBindingAction( "Gesture03",  3 )
	@BWKeyBindingAction( "Gesture04",  4 )
	@BWKeyBindingAction( "Gesture05",  5 )
	@BWKeyBindingAction( "Gesture06",  6 )
	@BWKeyBindingAction( "Gesture07",  7 )
	@BWKeyBindingAction( "Gesture08",  8 )
	@BWKeyBindingAction( "Gesture09",  9 )
	@BWKeyBindingAction( "Gesture10", 10 )
	@BWKeyBindingAction( "Gesture11", 11 )
	@BWKeyBindingAction( "Gesture12", 12 )
	@BWKeyBindingAction( "Gesture13", 13 )
	@BWKeyBindingAction( "Gesture14", 14 )
	@BWKeyBindingAction( "Gesture15", 15 )
	@BWKeyBindingAction( "Gesture16", 16 )
	@BWKeyBindingAction( "Gesture17", 17 )
	@BWKeyBindingAction( "Gesture18", 18 )
	@BWKeyBindingAction( "Gesture19", 19 )
	@BWKeyBindingAction( "Gesture20", 20 )
	@BWKeyBindingAction( "Gesture21", 21 )
	@BWKeyBindingAction( "Gesture22", 22 )
	@BWKeyBindingAction( "Gesture23", 23 )
	@BWKeyBindingAction( "Gesture24", 24 )
	@BWKeyBindingAction( "Gesture25", 25 )
	@BWKeyBindingAction( "Gesture26", 26 )
	@BWKeyBindingAction( "Gesture27", 27 )
	@BWKeyBindingAction( "Gesture28", 28 )
	@BWKeyBindingAction( "Gesture29", 29 )
	@BWKeyBindingAction( "Gesture30", 30 )
	@BWKeyBindingAction( "Gesture31", 31 )
	@BWKeyBindingAction( "Gesture32", 32 )
	@BWKeyBindingAction( "Gesture33", 33 )
	@BWKeyBindingAction( "Gesture34", 34 )
	@BWKeyBindingAction( "Gesture35", 35 )
	@BWKeyBindingAction( "Gesture36", 36 )
	@BWKeyBindingAction( "Gesture37", 37 )
	@BWKeyBindingAction( "Gesture38", 38 )
	@BWKeyBindingAction( "Gesture39", 39 )
	@BWKeyBindingAction( "Gesture40", 40 )
	@BWKeyBindingAction( "Gesture41", 41 )
	@BWKeyBindingAction( "Gesture42", 42 )
	@BWKeyBindingAction( "Gesture43", 43 )
	@BWKeyBindingAction( "Gesture44", 44 )
	@BWKeyBindingAction( "Gesture45", 45 )
	def playGesture( self, action, isDown = True ):
		if not isDown:
			return

		# Can't gesture while swimming
		if self.physics.inWater: return

		# If the Player is seated, allow only gestures that can be done while
		# moving. That is, only allow gestures that have an alpha blended
		# portion for the lower body.
		if self.mode == Mode.SEATED:
			if not self.gestureActions[action].canMove:
				return

		if not self.doingAction:
			self.actionCommence()

			# pretend the server told us about it
			self.didGesture( action )
			# and tell the server about it
			self.cell.didGesture( action )


	def didGesture( self, actionID ):
		if self.gestureActions[actionID].canMove:
			self.doingMovableAction += 1

		if not self.gestureActions[actionID].canHoldItem and \
				self.rightHand != Item.Item.NONE_TYPE:

			if not self.inCombat():	# check, for safety
				self.unequipItem()

			BigWorld.callback( 0.5,
				partial( Avatar.didGesture, self, actionID ) )
		else:
			Avatar.didGesture( self, actionID )
			
	#---------------------------------
	# Notes Example
	#---------------------------------

	def onAddNote( self, id ):
		if id == 0:
			FantasyDemo.addChatMsg( -1, "Note addition failed" )
		else:
			FantasyDemo.addChatMsg( -1, "Added Note: %d" % id )


	def onGetNotes( self, noteList ):
		if len( noteList ) > 0:
			# Note: Chat messages are currently being forced from unicode
			# to a utf-8 encoded string to be sent to the server and saved
			# into the DB. The corresponding encoding is in ConsoleCommands.py
			for note in noteList:
				FantasyDemo.addChatMsg( -1, "Found note: %d - %s" % ( note[ "id" ], note[ "description" ].decode( "utf8" ) ) )
		else:
			FantasyDemo.addChatMsg( -1, "No Notes Found" )

	# -------------------------------------------------------------------------
	# Section: Items trading
	# -------------------------------------------------------------------------

	def onTradeOfferItem( self, itemSerial ):
		'''Handles item offer events (when the user draggs and
		dropps an item in the trade area in the inventory GUI).
		Do not allow new offers if there is one already on the
		table (the player must cancel the current one first).
		Params:
			itemIndex			index of item in the inventory
		'''
		assert self.mode in ( Mode.TRADE_ACTIVE, Mode.TRADE_PASSIVE )
		assert self._tradeOfferLock == None

		try:
			self._tradeOfferLock = self.inventoryMgr.itemsLock( [itemSerial], 0 )
			self.cell.tradeOfferItemRequest( self._tradeOfferLock, itemSerial )
			self.inventoryWindow.updateInventory(
					self.inventoryItems,
					self.inventoryMgr.availableGoldPieces() )
		except ValueError:
			errorMsg = 'PlayerAvatar.onTradeOfferItem: invalid item (itemSerial=%d)'
			print errorMsg % itemSerial

		except Inventory.LockError:
			errorMsg = 'PlayerAvatar.onTradeOfferItem: lock error (itemSerial=%d)'
			print errorMsg % itemSerial


	def onTradeAccept( self, accept ):
		'''Handles trade commit events (when user clicks
		on the trade button in the inventory gui)
		'''
		assert self.mode in ( Mode.TRADE_ACTIVE, Mode.TRADE_PASSIVE )
		self.cell.tradeAcceptRequest( accept )

	def tradeTry( self ):
		'''Try entering the trade mode
		'''
		partner = BigWorld.target()
		if self.inventoryItems and partner and isinstance( partner, Avatar ):
			self.unequipItem()
			self.moveActionCommence()
			if partner.mode == Mode.TRADE_PASSIVE and \
					partner.modeTarget == self.id:
				self.tradeActiveEngage( partner )
			else:
				self.cell.tradeStartRequest( partner.id )
				self.setModeTarget( partner.id )
			return

		self.disagree()


	def tradeCancel( self ):
		'''Requests cancelation of trade mode
		'''
		self.cell.tradeCancelRequest()


	def tradeActiveEngage( self, partner ):
		'''Try entering the active trade mode. Partner is already waiting
		for us to trade with him (he is in TRADE_PASSIVE mode). Do this in
		two steps: (1) move close to Partner and (2) request trade mode
		Params:
			partner				the trade partner entity
		'''
		def doStep1():
			self._tradePosSeek( partner, doStep2, doFail )

		def doStep2():
			self.cell.tradeStartRequest( partner.id )
			self.setModeTarget( partner.id )

		def doFail():
			self.setModeTarget( Mode.NO_TARGET )
			self.actionComplete()
			self.disagree()

		doStep1()


	def tradeActiveEnterMode( self ):
		'''Called when PlayerAvatar.mode gets set by the cell.
		The active Avatar takes care of setting up the stage,
		animating both characters and showing the trade icon
		'''
		partner = ModeTarget._getModeTarget( self )

		if partner:
			partner.tradeAnimateAccept()
			self.tradeAnimateAccept()
			self.tradeShowGUI( True )


	def tradeActiveLeaveMode( self ):
		'''Called when Avatar.mode gets set by the cell. Cleans the scene.
		'''
		self._tradeLeaveMode()


	def tradePassiveEnterMode( self ):
		'''Called when PlayerAvatar.mode gets set by the cell. Shows the trade icon.
		'''
		pass


	def tradePassiveLeaveMode( self ):
		'''Called when Avatar.mode gets set by the cell. Clears trade icon.
		'''
		self._tradeLeaveMode()


	def tradeDeny( self ):
		'''The cell is denying our request to enter trade mode.
		(maybe partner can't or doesn't want to trade with us).
		'''
		self.setModeTarget( Mode.NO_TARGET )
		self.actionComplete()
		self.disagree()


	def _tradePosSeek( self, partner, successCallback, failCallback ):
		'''Move avatar to the position where the coordinated handshake
		animation can be played. Eventually calls successCallback or
		failCallback depending of the outcome of the seek operation.
		Params:
			partner           partner with whom to do the handshake
			successCallback	callback to be called if seek is successfull
			failCallback		callback to be called if seek fails
		'''
		def onSeek( success ):
			if success:
				successCallback()
			else:
				failCallback()

		self.seeker.seekPath( self,
			partner.model.Shake_B_Accept.seekInv,
			self.walkFwdSpeed,
			5.0,
			0.10,
			onSeek )


	def tradeShowGUI( self, visible ):
		'''Shows/hide inventory GUI in trade mode.
		Params:
			visible				True if GUI is to be shown. False if should be hidden
		'''
		self.updateCursor()


	def tradeOfferItemNotify( self, itemType ):
		'''Cell is notifying us that an item is being offered by trade partner.
		Params:
			itemType				Type of item being offered by partner
		'''
		pass


	def tradeOfferItemDeny( self, tradeItemLock ):
		'''Notifies this avatar that his item offer has been denied
		by the server (maybe it has been locked via web trading).
		Params:
			tradeItemLock		handle to offered item's lock
		'''
		assert self._tradeOfferLock == tradeItemLock
		self._tradeOfferLock = None

		self.inventoryMgr.itemsUnlock( tradeItemLock )
		self.disagree()


	def tradeAcceptNotify( self, accepted ):
		'''Cell is notifying us that our trade partner has accepted our offer.
		Params:
			accepted				True if partner is accepting item. False otherwise
		'''
		pass


	def tradeCommitNotify( self, success, outItemsLock,
			outItemsSerial, outGoldPieces, inItemsTypes,
			inItemsSerials, inGoldPieces ):
		'''Cell is responding to our trade commit request.
		Params:
			success				True if trade was successful. False otherwise
			outItemsLock		Lock of items being traded out
			outItemsSerial		serials of items being traded out
			outGoldPieces		ammount of gold being traded out
			inItemsTypes		array of items being traded in
			inItemsSerials		serials of items being traded in
			inGoldPieces		ammount of gold pieces being traded in
		'''
		# this notification is also used by the commerce system.
		# If this is the case, do a commerce commit notification
		if self.mode == Mode.COMMERCE:
			self._commerceCommitNotify( success, outItemsLock, inItemsTypes )
		elif self._tradeOfferLock != None:
			self._tradeCommitNotify( success, outItemsLock )

		if success:
			serials = self.inventoryMgr.itemsTrade(
					outItemsSerial, outGoldPieces,
					inItemsTypes, inItemsSerials,
					inGoldPieces, outItemsLock )

			self.inventoryWindow.updateInventory(
					self.inventoryItems,
					self.inventoryMgr.availableGoldPieces() )
		else:
			self.inventoryMgr.itemsUnlock( outItemsLock )


	def _tradeCommitNotify( self, success, outItemsLock ):
		'''Takes care of properly updating the trading interface after a
		trade transcation has been completed. Note that the actual items/gold
		transcation will be carried by the tradeCommitNotify method.
		Params:
			success				True if trade was successful. False otherwise
			outItemsLock		lock handle for items being traded out
		'''
		assert self._tradeOfferLock == outItemsLock
		self._tradeOfferLock = None

		if not success:
			ModeTarget._getModeTarget( self ).disagree()
			self.disagree()


	def _tradeLeaveMode( self ):
		'''Common functions for when player avatar leaves the trade mode.
		'''
		self.setModeTarget( Mode.NO_TARGET )
		self.tradeShowGUI( False )
		self.actionComplete()
		if self._tradeOfferLock != None:
			self.cell.itemsUnlockRequest( self._tradeOfferLock )
			self._tradeOfferLock = None

	#---------------------------------
	# XMPP Example
	#---------------------------------

	def onXmppRegisterWithTransport( self, transport ):
		# Because the property is BASE_AND_CLIENT, it will only be propagated
		# on entity creation, so we'll add a dummy record now for convenience.
		self.xmppTransportDetails.append(
			{ "transport": transport, "username": "", "password": "" } )

		registerMsg = "Successfully registered %s account with XMPP gateway" % \
						transport
		FantasyDemo.addChatMsg( -1, registerMsg, FDGUI.TEXT_COLOUR_SYSTEM )


	def onXmppDeregisterWithTransport( self, transport ):
		for transportDetails in self.xmppTransportDetails:
			if transportDetails[ "transport" ] == transport:
				self.xmppTransportDetails.remove( transportDetails )

		deregisterMsg = "Successfully deregistered %s account with XMPP " \
						"gateway" % transport
		FantasyDemo.addChatMsg( -1, deregisterMsg, FDGUI.TEXT_COLOUR_SYSTEM )


	# Callback methods from the XMPP interface on the Base
	def onXmppMessage( self, friendID, transport, message ):
		sender = friendID.split( "/", 1 )[0] + "[IM %s]" % transport
		publishMessage = sender + ": " + message
		FantasyDemo.addChatMsg( -1, publishMessage, FDGUI.TEXT_COLOUR_OTHER_SAY )


	def onXmppRoster( self, roster ):
		# The visitor that will be used to notify us of events
		visitor = XMPP.AvatarRosterVisitor()

		# Update our XMPPRoster
		self.roster.update( roster, visitor )


	def onXmppRosterItemAdd( self, friendID, transport ):
		# The visitor that will be used to notify us of events
		visitor = XMPP.AvatarRosterVisitor()

		# Update our XMPPRoster
		self.roster.add( friendID, transport, rosterVisitor = visitor )


	def onXmppRosterItemDelete( self, friendID, transport ):
		# The visitor that will be used to notify us of events
		visitor = XMPP.AvatarRosterVisitor()

		# Update our XMPPRoster
		self.roster.remove( friendID, transport, rosterVisitor = visitor )


	def onXmppPresence( self, friendID, transport, presence ):
		# The visitor that will be used to notify us of events
		visitor = XMPP.AvatarRosterVisitor()

		if presence == "subscribe":

			# We don't have to add them to our list again.
			if self.roster.isFriend( friendID, transport ):
				return

			# They have subscribed to us, so lets ask them to be our friend too.
			self.base.xmppAddFriend( friendID, transport )

		elif presence == "unsubscribe":
			# TODO: implement this. we don't want to see presence notifications about
			#       friends we are in the middle of deleting.
			self.roster.addPendingFriendRemoval( friendID, transport )

			# Auto-remove anybody from our own roster if they have removed us
			self.base.xmppDelFriend( friendID, transport )

		elif presence == "error":
			# This will most likely be as a result of an invalid transport
			# registration. This message can be changed later if other
			# cases are discovered.
			errorMsg = "Failed to add friend %s. Your account credentials " \
				"for the %s transport may be incorrect." % \
					(friendID, transport)

			FantasyDemo.addChatMsg( -1, errorMsg, FDGUI.TEXT_COLOUR_SYSTEM )

			# Now make sure the roster item is removed for that user.
			self.base.xmppDelFriend( friendID, transport )

		else:

			# Update our XMPPRoster
			self.roster.updatePresence( friendID, transport, presence, visitor )


	def onXmppError( self, message ):
		FantasyDemo.addChatMsg( -1, message )

def intersectRayWithPolygon( raySrc, rayDir, polygon ):
	'''
	Helper function to calculate the intersection of a ray with a
	convex polygon. Used with triangles from the collision scene.
	If passed a non-convex polygon it will return the furthest intersection
	in the direction of rayDir.
	@args Vector3 raySrc, Vector3 rayDir, Sequence( Vector3 ) polygon
	@returns a tuple of the position of intersection, and the yaw of the
		vector perpendicular to the edge of the poly
		rayDir should probably be normalised
	'''
	# shift the origin of the polygon to the ray's start
	spoly = map( lambda pt, raySrc=raySrc: Vector3( pt - raySrc ), polygon )

	# find the edges which are cut by dir (only 2 for a convex polygon)
	cands=[]
	for i in xrange(len(spoly)):
		apt = spoly[i]
		bpt = spoly[(i+1)%len(spoly)]
		across = rayDir.cross2D( apt )
		bcross = rayDir.cross2D( bpt )
		if (across > 0) != (bcross >= 0 ):
			cpt = bpt - apt
			numer = apt.cross2D( cpt )
			denom = rayDir.cross2D( cpt )
			cands.append((apt,cpt,numer/denom))

	# find the one with the biggest (positive) projection
	cands.sort( lambda s,t: -cmp( s[2], t[2] ) )

	# and that's the edge
	edge = raySrc + rayDir.scale( cands[0][2] )

	# find the vector perpendicular to the poly
	edgeParallel = cands[0][1]
	edgePerpendicular = Vector3(-edgeParallel.z, 0, edgeParallel.x)
	if edgePerpendicular.dot(rayDir) < 0:
		edgePerpendicular = -edgePerpendicular
	edgeYaw = math.atan2(edgePerpendicular.x, edgePerpendicular.z)

	return (edge, edgeYaw)
