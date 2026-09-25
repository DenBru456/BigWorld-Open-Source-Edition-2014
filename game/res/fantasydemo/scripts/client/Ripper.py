
import math
import random

import BigWorld
import FantasyDemo

import AvatarModel
import Avatar
from FDGUI import Minimap
import GUI
from Helpers import Caps
from Math import *

class Ripper(

# Important bases
BigWorld.Entity
):
	"""This module implements the Ripper entity type.

	Handles entering/leaving world, and mounting/dismounting.
	"""
	
	stdModel = "sets/vehicles/razor2.model"
	stdFlare = "sets/vehicles/razor_flare.model"
	dustParticles = "particles/ripper_dust.xml"
	breathParticles = "particles/ripper_breath.xml"
	NULL_MODEL_NUMBER = -1

	OUTSIDE_OFFSETX = -0.900
	OUTSIDE_OFFSETZ = 0.587

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.pilotAvatar = None


	def prerequisites( self ):
		prerequisit = []
		prerequisit.append( Ripper.stdModel )
		prerequisit.append( Ripper.stdFlare )
		prerequisit.append( Ripper.dustParticles )
		prerequisit.append( Ripper.breathParticles )
		#prerequisit.append( "maps/fx/environment/dust.tga" )
		return prerequisit


	def onEnterWorld( self, prereqs ):
		self.targetCaps = [Caps.CAP_CAN_USE]

		self.filter = BigWorld.DumbFilter()

		self.model = prereqs[ Ripper.stdModel ]
		self.model.motors[0].entityCollision = 1
		self.model.motors[0].collisionRooted = 1
		self.focalMatrix = self.model.node("HANDPOS_left")

		self.model.root.attach( prereqs[Ripper.dustParticles] )

		breath = prereqs[Ripper.breathParticles]
		breath.system(0).action(1).sleepPeriod = random.randint( 40, 80 ) / 10.0
		self.model.root.attach( breath )

		self.minimapIcon = GUI.load("gui/minimap_icon.gui")
		Minimap.addEntity( self )

		if self.pilotID != -1:
			# the ripper is already being piloted so we need to add
			# the stand-in model and set the idle animations going

			self.model.RIdle()

			self.model.flare = BigWorld.Model( Ripper.stdFlare )
			self.model.flare.Go( 0, self.model.flare.On )

			self.filter = BigWorld.AvatarFilter()

			pilot = BigWorld.entity( self.pilotID )

			self.model.mount = None
		else:
			# the ripper has no pilot so we should set it to being empty
			self.model.Empty()


	# This function is called by avatar when it enters the world.
	def passengerEnterWorld( self, pilot ):
		pilot.model.visible = False
		pilot.model.motors[0].entityCollision = False
		if self.model.mount == None:
			unpackedPilotModel = AvatarModel.unpack( pilot.avatarModel )
			self.model.mount = AvatarModel.create( unpackedPilotModel, BigWorld.Model('') )
			self.model.mount.RipperPilotIdle()
			self.model.mount.visible = True

			pilot.targetCaps = []


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model.mount = None
		self.model.flare = None
		self.model = None


	# The player wants to use us
	def use( self ):
		self.playerActionCommence()
		self.walkToMountPosition()


	def playerActionCommence(self):
		BigWorld.player().moveActionCommence()
		BigWorld.player().allowFirstPersonModeToggle(False)


	def playerActionComplete(self):
		BigWorld.player().actionComplete()
		BigWorld.player().allowFirstPersonModeToggle(True)


	def walkToMountPosition( self, success = True ):
		WALK_TIMEOUT = 10
		VERTICAL_OFFSET_ALLOWED = 2.0
		player = BigWorld.player()

		if not success or self.pilotID != -1:
			player.model.Shrug( 0, player.actionComplete )
			self.playerActionComplete()
			return

		rpos = Vector3( self.position )
		rdir = Vector3( math.sin(self.yaw), 0, math.cos(self.yaw) )
		currOff = Vector3( player.position ) - rpos

		# Is the player is on the wrong side of the Ripper?
		if (currOff * rdir).y < 0:
			roffx = -0.886
			if currOff.dot( rdir ) > 0:
				# Is in front
				roffz = 3.11
			else:
				# Is behind
				roffz = -2.88

			ppos = Vector3( roffz * rdir.x + roffx * rdir.z, 0, roffz * rdir.z - roffx * rdir.x ) + rpos

			player.seeker.seekPath( player,
				(ppos.x, ppos.y, ppos.z, player.yaw),
				player.walkFwdSpeed,
				WALK_TIMEOUT,
				VERTICAL_OFFSET_ALLOWED,
				self.walkToMountPosition )
			return

		( x, y, z ), ( yaw, pitch, roll ) = self.getMountDismountPosition()

		player.seeker.seekPath( player,
			( x, y, z, yaw ),
			player.walkFwdSpeed,
			WALK_TIMEOUT,
			VERTICAL_OFFSET_ALLOWED,
			self.arriveAtMountPosition )


	# This callback is called when the player has finished seeking toward to mount position.
	# 		success 		Describes whether the final seek to the vehicle was successful
	def arriveAtMountPosition( self, success ):
		player = BigWorld.player()

		if not success or self.pilotID != -1:
			player.model.Shrug( 0, player.actionComplete )
			self.playerActionComplete()
			return

		player.allowFirstPersonModeToggle(True)
		player.toggleFirstPersonMode( False )
		player.allowFirstPersonModeToggle(False)

		if player.rightHand != -1:
			player.equip( -1 )

			waitTime = 0.0
			waitTime += player.model.action( 'ChangeItemBegin' ).duration
			waitTime += player.model.action( 'ChangeItemEnd' ).duration

			BigWorld.callback(waitTime, self.cellMountVehicle)
		else:
			self.cellMountVehicle()


	def cellMountVehicle(self):
		if BigWorld.player()._isConnected():
			self.cell.mountVehicle()
		else:
			def mount():
				if not self.isDestroyed:
					self.mountVehicle(1, BigWorld.player().id)

			BigWorld.callback(1, mount)


	# This is a callback seen to all clients to announce that an avatar is boarding the vehicle.
	# At this point the client will have been given control of the ripper from the server and the
	# pilotID should already be set appropriately.
	#		succeeded 				Describes whether the action to board the vehicle was successful
	#		pilotAvatarID			The ID of the avatar boarding the vehicle. This is not nesseseraly
	#								this client's avatar ID.
	def mountVehicle( self, succeeded, pilotAvatarID ):
		# cleanup on mount failure
		if not succeeded:
			if BigWorld.player().id == pilotAvatarID:
				self.playerActionComplete()
			return

		pilot = BigWorld.entities[pilotAvatarID]

		# stop all previous actions
		for actionName in pilot.model.queue:
			pilot.model.action(actionName).stop()
		for actionName in self.model.queue:
			self.model.action(actionName).stop()
		if self.model.mount:
			for actionName in self.model.mount.queue:
				self.model.mount.action(actionName).stop()

		if BigWorld.player() and BigWorld.player().id == pilotAvatarID:

			self.pilotAvatar = pilot
			BigWorld.player(self)

			unpackedPilotModel = AvatarModel.unpack( self.pilotAvatar.avatarModel )
			self.model.mount = AvatarModel.create( unpackedPilotModel, BigWorld.Model('') )

			self.pilotAvatar.model.visible = False
			self.pilotAvatar.physics.collide = False
			self.pilotAvatar.physics.fall = False		# Note: important otherwise apply gravity will alight us from the vehicle

			# setup callback to receive
			# when the animation finishes
			BigWorld.callback(self.model.Board.duration, self.finishMountVehicle)
		else:
			# this client is not controlling this ripper but
			# someone has just hopped on so make it appear to idle

			if pilot and pilot.inWorld:
				unpackedPilotModel = AvatarModel.unpack( pilot.avatarModel )
				self.model.mount = AvatarModel.create( unpackedPilotModel, BigWorld.Model('') )

				pilot.model.visible = False
				pilot.am.entityCollision = False

				pilot.targetCaps = []

			else:
				self.model.mount = None

			self.filter = BigWorld.AvatarFilter()

			# configure the Ripper's action matcher
			self.model.motors[0].entityCollision = True
			self.model.motors[0].collisionRooted = False

		def playIdle():
			if self.isDestroyed:
				return
			self.model.RIdle()
			if self.model.mount:
				self.model.mount.RipperPilotIdle()

		# play the board actions
		self.model.Board().Boarded()
		if self.model.mount:
			self.model.mount.RipperPilotBoard().RipperPilotBoarded()
		BigWorld.callback(self.model.Board.duration, playIdle)

		self.model.flare = BigWorld.Model(Ripper.stdFlare)
		self.model.flare.Go(0, self.model.flare.On)


	def finishMountVehicle( self ):
		if self.isDestroyed:
			return
		self.pilotAvatar.physics.teleport( self.position, ( self.yaw, self.pitch, self.roll ) )
		# Turn off player physics so that player position never changes relative
		# to the ripper. Theoretically, physics should not change player's
		# position but the accumulation of floating point errors means that
		# the player does move slightly with each tick so if you ride on the
		# ripper for an extended period, the player's position could be way off.
		self.pilotAvatar.physics = BigWorld.DUMMY_PHYSICS

		self.physics = BigWorld.HOVER_PHYSICS
		self.physics.turn = 0
		self.physics.thrust = 0
		self.physics.brake = 0
		self.physics.oldStyleCollision = FantasyDemo.rds.oldStyleCollision
		# old style physics flag
		self.physics.collide = 1
		# new style physics flags
		self.physics.collideTerrain = 1
		self.physics.collideObjects = 1
		self.physics.fall = 1
		self.physics.ripperTurnRate = 0.5
		self.physics.ripperZDrag = 0.99


	# This function is a callback sent to all clients with this ripper in their area of interest.
	#		pilotAvatar		The ID of the client avatar that sent the original dismount request.
	# Called by Ripper.dismount() on the cell.
	# When this is called the server has already taken back control of the ripper.
	def dismountVehicle( self, pilotAvatarID ):
		pilot = BigWorld.entity( pilotAvatarID )
		if pilot:
			for actionName in pilot.model.queue:
				pilot.model.action(actionName).stop()
			pilot.am.entityCollision = True

		if BigWorld.player() and BigWorld.player().id == pilotAvatarID:
			pos, dir = self.getMountDismountPosition()
			BigWorld.player().physics.teleport( pos, dir )
			BigWorld.player().model.visible = False

			self.model.flare = None
			self.filter = BigWorld.DumbFilter()

			# play the board actions
			self.model.Alight().Alighted().Empty()
			self.model.mount.RipperPilotAlight().RipperPilotAlighted()

			# setup callback to receive when the animation finishes
			BigWorld.callback( self.model.Alight.duration, self.finishDismountVehicle )
		else:
			self.model.Alight().Alighted().Empty()
			# Pilot may not yet have entered the world
			if self.model.mount != None:
				self.model.mount.RipperPilotAlight().RipperPilotAlighted()

			# setup callback to receive when the animation finishes
			def removeMount(self):
				if not self.isDestroyed:
					self.model.mount = None

				assert isinstance( pilot, Avatar.Avatar )
				pilot.set_avatarModel( pilot.model )

			BigWorld.callback( self.model.Alight.duration, lambda: removeMount( self ) )



	def finishDismountVehicle( self ):
		if BigWorld.player() is not None:
			BigWorld.player().physics.userDirected = True
			BigWorld.player().physics.fall = True
			BigWorld.player().model.visible = True
			self.playerActionComplete()
		if not self.isDestroyed:
			self.model.mount = None
			
		
	# This function produces the position and orientation that the model
	# will need to be standing ( in world space ) to line up with the mount and dismount animations.
	def getMountDismountPosition( self ):
			rpos = Vector3( self.position )
			rdir = Vector3( math.sin(self.yaw), 0, math.cos(self.yaw) )

			roffx = Ripper.OUTSIDE_OFFSETX
			roffz = Ripper.OUTSIDE_OFFSETZ
			ppos = rpos + Vector3(	roffz * rdir.x + roffx * rdir.z,
									0,
									roffz * rdir.z - roffx * rdir.x )
			pyaw = self.yaw + math.pi/2.0

			return ppos, ( pyaw, 0, 0 )


	def cellDismountVehicle(self):
		if BigWorld.player()._isConnected():
			self.cell.dismountVehicle()
		else:
			def dismount():
				if not self.isDestroyed and BigWorld.player():
					self.dismountVehicle(BigWorld.player().id)

			BigWorld.callback(1, dismount)

	def checkAnims( self ):
		"""Overridden by PlayerRipper"""
		pass


	def name( self ):
		return "Ripper"


	vehicleActions = [	"RIdle",
						"RTurnLeft",
						"RTurnRight",
						"Stop",
						"Thrust" ]

	pilotActions = [	"RipperPilotIdle",
						"RipperPilotTurnLeft",
						"RipperPilotTurnRight",
						"RipperPilotStop",
						"RipperPilotThrust" ]

	vehicleTransitionActions = [	"",
									"RTurningLeft",
									"RTurningRight",
									"Stopping",
									"Thrusting" ]

	pilotTransitionActions = [		"",
									"RipperPilotTurningLeft",
									"RipperPilotTurningRight",
									"RipperPilotStopping",
									"RipperPilotThrusting" ]

def create():
	player = BigWorld.player()
	return BigWorld.createEntity('Ripper', player.spaceID, 0, player.position, (0,0,0), {})

# Important - engine searches for Player here
from PlayerRipper import PlayerRipper

#Ripper.py
