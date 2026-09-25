
from Ripper import Ripper
from Helpers import BWKeyBindings

import BigWorld
from Helpers import Caps
from FDGUI.Minimap import Minimap
from functools import partial
import GUI
from Helpers.BWKeyBindings import BWKeyBindingAction
from Helpers import PSFX

import FantasyDemo

class PlayerRipper( Ripper, BWKeyBindings.BWActionHandler ):
	"""Handles when the Ripper becomes a player/non-player,
	dismounting and steering."""

	def onBecomePlayer( self ):
		self.setupActionList()
		FantasyDemo.rds.keyBindings.addHandler( self )

		self.filter = BigWorld.PlayerAvatarFilter()

		FantasyDemo.cameraType( FantasyDemo.rds.FLEXI_CAM )

		self.forwardThrust = 0.0
		self.backwardThrust = 0.0
		self.leftwardTurn = 0.0
		self.rightwardTurn = 0.0
		self.thrustStrength = 2.5

		self.doingAction = 0

		BigWorld.target.caps( Caps.CAP_NONE )

		self.wantTurn = 0
		self.wantMove = 1

		self.pilotAvatar.physics.teleport( self.position, ( 0, 0, 0 ) )

		if self.model.inWorld:
			self.checkAnims()

		# Remove old minimap dot
		#Minimap.delEntity( self )
		# Add minimap player arrow
		self.minimapIcon = GUI.load("gui/minimap_icon.gui")
		self.minimapHandle = FantasyDemo.rds.fdgui.minimap.m.add(self.matrix, self.minimapIcon)


	def onBecomeNonPlayer( self ):
		self.pilotAvatar = None
		self.filter = BigWorld.DumbFilter()
		self.keyBindings = []
		FantasyDemo.rds.keyBindings.removeHandler( self )

		# Remove minimap player arrow
		# Check if minimap still exists
		# eg. if the game is shutting down
		if hasattr( FantasyDemo.rds.fdgui, "minimap" ):
			FantasyDemo.rds.fdgui.minimap.m.remove( self.minimapHandle )
		# FDGUI.Minimap.remove() uses hasattr to determine if we have a
		# minimap icon.
		del self.minimapHandle
		# Add old minimap dot
		#Minimap.addEntity( self )


	def handleKeyEvent( self, event ):
		if event.isRepeatedEvent() or not ( self.physics != None and self.inWorld ):
			return False

		FantasyDemo.rds.keyBindings.callActionForKeyState( event.key )

		self.updateThrust()

		return True


	def updateThrust( self ):
		if self.physics == None:
			return

		if not self.doingAction and self.physics.ripperZDrag < 1:
			self.physics.thrust = self.thrustStrength * ( self.forwardThrust -
				self.backwardThrust )
			self.physics.turn = self.rightwardTurn - self.leftwardTurn
		else:
			self.physics.thrust = 0
			self.physics.turn = 0

		self.checkAnims()


	# Handle dismount key event.
	#		isDown	The state of the key.
	@BWKeyBindingAction( "EscapeKey" )
	def beginDismount( self, isDown ):
		# Check that we have not already disembarked
		if ( not isDown ) or BigWorld.player() != self:
			return

		# initPhysics() re-enables collision and falling.
		self.pilotAvatar.initPhysics()
		self.pilotAvatar.physics.collide = False
		self.pilotAvatar.physics.fall = False

		# Turn off the ripper so it drops to the ground
		self.physics.userDirected = False
		self.physics.ripperElasticity = 0
		self.physics.ripperDesiredHeightFromGround = 0
		self.physics.ripperTurnRate = 0

		self.model.flare.Stop( 0, self.model.flare.Off )

		# wait for Ripper to fall to the ground
		BigWorld.callback( 0.5, self.dismountStep )


	# This function is recursively called until the ripper comes to a rest.
	def dismountStep( self ):
		if self != BigWorld.player():
			return
		# continue to wait if the Ripper has not yet come to a halt
		if self.physics.moving:
			BigWorld.callback( 0.5, self.dismountStep )
			return

		# park the Ripper
		self.physics = BigWorld.STANDARD_PHYSICS
		self.physics.thrust = 0
		self.physics.brake = 1
		self.physics.ripperZDrag = 1
		self.model.motors[0].entityCollision = 1
		self.model.motors[0].collisionRooted = 1

		# Make the avatar the player again.
		# Note: This will change the type of the ripper from a PlayerRipper
		# to a Ripper so PlayerRipper functions will not be available from now on.
		BigWorld.player( self.pilotAvatar )

		self.playerActionCommence()
		BigWorld.player().model.visible = False
		BigWorld.player().physics.fall = False

		self.cellDismountVehicle()


	# Update the animations of the ripper and pilot model
	# This is run only on the controlling client as it requires
	# parameters from the physics object.
	# This code will ultimately be replaced by an action matcher
	# but for now the action matcher does not provide the functionality
	# required to animate both the ripper and the pilot.
	# Note: Called by Physics::hoverStyleTick()
	def checkAnims( self ):
		if self.physics == None:
			return

		if self.physics.ripperZDrag < 1:
			if self.physics.thrust < 0:
				self.physics.brake = -self.physics.thrust
				self.physics.thrust = 0
			else:
				self.physics.brake = 0

		ethrust = self.physics.thrust
		ethrust -= self.physics.brake
		if ethrust > 1: ethrust = 1

		# Animation only below here

		if len( self.model.queue ) > 0 and self.model.queue[0] == 'Alight':
			return

		self.wantTurn = self.physics.turn
		if self.wantTurn < 0 : self.wantTurn = -1
		if self.wantTurn > 0 : self.wantTurn = 1

		self.wantMove = ethrust
		if self.wantMove < 0 : self.wantMove = -1
		if self.wantMove > 0 : self.wantMove = 1

		if self.wantTurn != 0:
			act = (self.wantTurn+1)/2 + 1
		elif self.wantMove != 0:
			act = (self.wantMove+1)/2 + 3
		else:
			act = 0

		act = int(act)

		ripperAction = self.model.action(Ripper.vehicleActions[act])
		ripperAction()
		BigWorld.callback(
			ripperAction.duration - ripperAction.blendOutTime - 0.0001,
			partial( self.playTransitionAction, act,
					 self.wantTurn, self.wantMove ) )

		if self.model.mount:
			self.model.mount.action(Ripper.pilotActions[act])()


	# This function is a callback used by checkAnims to handle actions
	# that transition between different behaviours (turning, stopping etc).
	def playTransitionAction( self, act, oldTurn, oldMove ):
		# If the player logs off while on the ripper, a callback to this may still be pending.
		# In this case, the class of self will have changed and we won't be able to do this.
		if not isinstance( self, PlayerRipper ):
			return

		if self.wantTurn != oldTurn or self.wantMove != oldMove:
			return

		if Ripper.vehicleTransitionActions[act] == "":
			return

		if self.model.queue[0] == 'Alight':
			return

		self.model.action( Ripper.vehicleTransitionActions[act] )()
		if self.model.mount:
			self.model.mount.action( Ripper.pilotTransitionActions[act] )()


	# This function is necessary to use the chat consol while the Ripper is the player.
	def handleConsoleInput( self, string ):
		if self.pilotAvatar:
			self.pilotAvatar.cell.chat( unicode(string) )
			FantasyDemo.addChatMsg( self.id, string )


	# This method handles collision callbacks from the ripper physics.
	def onCollide( self, newMomentum, collidePosition, severity, triangleFlags ):
		speed = newMomentum.length

		if speed > 0.5:
			PSFX.worldExplosion( self.model, newMomentum, collidePosition, triangleFlags, 50 )

			# severity is a dot product between old and new momentum.
			# thus if less than zero, it was a head-on collision,
			# around to +1 which is a minor glance

			# Sound calls disabled because sound events are missing from soundbank.

# 			if ( severity < 0.5 ):
# 				self.model.playSound( "seeker/explosion" )
# 			else:
# 				self.model.playSound( "players/hurt" )


	@BWKeyBindingAction( "MoveForward" )
	def moveForward( self, isDown ):
		if isDown:
			self.forwardThrust = 1.0
		else:
			self.forwardThrust = 0.0


	@BWKeyBindingAction( "MoveBackward" )
	def moveBackward( self, isDown ):
		if isDown:
			self.backwardThrust = 1.0
		else:
			self.backwardThrust = 0.0


	@BWKeyBindingAction( "TurnLeft" )
	def	turnLeft( self, isDown ):
		if isDown:
			self.leftwardTurn = 1.0
		else:
			self.leftwardTurn = 0.0


	@BWKeyBindingAction( "TurnRight" )
	def turnRight( self, isDown ):
		if isDown:
			self.rightwardTurn = 1.0
		else:
			self.rightwardTurn = 0.0


	@BWKeyBindingAction( "MoveUpward" )
	def moveUpward( self, isDown ):
		if isDown:
			self.physics.thrustAxis = (0,1,0)
			self.thrustStrength = 5.0
		else:
			self.physics.thrustAxis = (0,0,1)
			self.thrustStrength = 2.5


	def name( self ):
		return "Player Ripper"
