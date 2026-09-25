# Ripper.py
"This module implements the Ripper entity."

import BigWorld

# ------------------------------------------------------------------------------
# Section: Ripper
# ------------------------------------------------------------------------------
class Ripper( BigWorld.Entity ):
	NULL_MODEL_NUMBER = -1

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.startPosition = self.position
		self.startDirection = self.direction


	# Called by the client to attempt to board the ripper and then notify all clients about this.
	#		sourceAvatar	The ID of the avatar on the calling client.
	def mountVehicle( self, sourceAvatarID ):
		try:
			avatar = BigWorld.entities[ sourceAvatarID ]
		except:
			return

		if self.teleportTimer:
			self.cancel( self.teleportTimer )
			self.teleportTimer = 0

		# Check the Ripper is not already occupied.
		if self.controlledBy != None:
			self.ownClient.mountVehicle( False, avatar.id )
			return

		# Set the pilot ID. This value is used to set the up 
		# the pilot model when the Ripper enters the world.
		self.pilotID = sourceAvatarID

		# Give control of the Ripper to the client. At this point the 
		# client Ripper will get a .physics member.
		self.controlledBy = avatar.base

		# Move the Avatar into the vehicle's space. The avatar's world 
		# space position is maintained across the transition.
		avatar.requestBoardVehicle( self.id )

	def passengerBoarded( self, sourceAvatarID ):
		# Notify all clients about the Ripper being mounted.
		self.allClients.mountVehicle( True, sourceAvatarID )

	# Called by the client to attempt to dismount the ripper and then notify all clients about this.
	#		sourceAvatar	The ID of the avatar on the calling client.
	def dismountVehicle( self, sourceAvatarID ):
		if sourceAvatarID != self.pilotID:
			print 'Ripper: Non-pilot attempting to dismount', self.id, sourceAvatarID, self.pilotID
			return

		self.teleportTimer = self.addTimer( 10.0 * 60.0, 0.0 )

		# Return the Ripper to the server's control.
		self.controlledBy = None

		# Set the pilot ID back to None
		self.pilotID = -1

		try:
			avatar = BigWorld.entities[ sourceAvatarID ]
		except:
			# Notify all clients about the Ripper being dismounted.
			self.allClients.dismountVehicle( sourceAvatarID )
			return

		print 'dismountVehicle', avatar.vehicle

		# Return the avatar to world space. Note: after setting pilotID and controlledBy
		avatar.requestAlightVehicle( self.id )

	def passengerAlighted( self, sourceAvatarID ):
		# Notify all clients about the Ripper being dismounted.
		self.allClients.dismountVehicle( sourceAvatarID )


	def onLoseControlledBy( self, id ):
		self.dismountVehicle( id )

	def onTimer( self, timerId, userId ):
		if timerId != self.teleportTimer:
			print "Ripper.onTimer: Wrong timerId", timerId, self.teleportTimer
		self.position = self.startPosition
		self.direction = self.startDirection

# Ripper.py
