# --------------------------------------------------------------------------
# This is an Entity Implementation Script.  It defines how an entity will interact with the BigWorld Engine.
# Each entity will inherit from BigWorld.Entity, which is the run-time definition of the internal Entity class.
# The parent/base class has several methods defined, which BigWorld will call as required.  An entity may override 
# as many of these as are required to implement their intended functionality.  A complete list is provided in the 
# BigWorld Python Interface documentation under Entity.

# For every property declared in its Entity Definition Script, an entity may also implement a set_<property name> 
# function.  This will be called whenever BigWorld changes the variable.  The flags parameter in the Entity 
# Definition Script determines which components of BigWorld will be able to see and hence alter it.

# The entity implementation may also call any of the methods outlined in the BigWorld Python Interface as well as 
# defining its own for internal or cross script use (eg, Avatar.py (player) interacting with seat.py).
# --------------------------------------------------------------------------


import BigWorld
import FantasyDemo
import math
from functools import partial
from Helpers import Caps
from FDGUI import Minimap
from Math import Vector3
from GameData import SeatData

# --------------------------------------------------------------------------
# Class:  Seat
# Description:
#	- Implements the behaviour of a seat in the game.
#	- Inherits from BigWorld.Entity - Any necessary functions should be overridden.
# --------------------------------------------------------------------------
class Seat( BigWorld.Entity ):
	"""
	The Seat Entity allows any Entity to sit down upon it as long as the
	sitting Entity implements the following methods:

	Animation/Action Requirements for the Avatar:

	Sitting down uses two animations: the first sits the Avatar down on the
	chair; the second is an idle in the chair. Both are encapsulated within
	three actions: SitOnChair, IdleOnChair, and RiseFromChair.

	The sitting animation begins with the model at an offset from origin.
	Here, the origin is taken to be the position of the chair. Animating
	through the frames will cause the model to be seated on the chair,
	ending at the origin. The action for the Avatar must be called
	'SitOnChair', and it must be a coordinated action with a short
	blend-out time, 0.0001 seconds.

	The idle animation is a short idle with the character seated. The model
	will be at the origin when playing this animation. The action for the
	Avatar must be called 'IdleOnChair', and it must be a filler action with
	short blend-in and blend-out times.

	The getting-up animation is the reverse of the sitting down animation.
	It starts with the model at origin and ends with the model at an offset
	from the origin. The action for the Avatar must be called
	'RiseFromChair' and it must be a coordinated action with a short
	blend-in time.


	Client/Server Procedure for Sitting Down:

	The player is defined as the Avatar of client that initiates the sitting
	down. The echo is defined as the Avatar of the player as seen by another
	client's player.

	The player begins by selecting the Seat and using its use() method. The
	use() method determines whether the player wishes to sit down or get up.

	Sitting down begins with the Seat telling the player to move into
	position. This position is determined from the Seat's position and
	facing, taking into account the offset point of the SitOnChair
	animation of the player's model.

	The echos do not activate the seek - they move into position by virtue
	of movement updates to the server, sent by the player.

	Once the player is in position, the Seat entity sends a request to
	itself on the server. It will also set local flag stating that the
	player is waiting to sit down on it; this is for contention in case
	someone other player is granted the seat.

	The Seat instance on the server will accept the sit-down request unless
	someone else is seated on it, or it has just awarded it to another
	player. There is no explicit rejection message: The Seat merely changes
	its ownerID property to the entity ID of the Avatar seated upon it. The
	server's Seat will also initiate a request for a mode change for its
	owner, from Avatar.MODE_NONE to Avatar.MODE_SEATED.

	Changing the ownerID property will propagate down to the clients. It
	removes the targetable capability of the Seat, making it unselectable.
	If the player is waiting to sit down and the ownerID is not the player,
	it counts as a rejection, thus breaking the player's wait.

	Changing the server Avatar's mode will propagate down to the clients. It
	is this mode change that initiates the sit-down. As sitting down is a
	residual action, it should be a mode; hence getting up and sitting down
	are both initiated by mode changes.


	Present Implementation: At present, the Avatar knows about the Seat
	class and two of its methods. When it receives a mode change, it 
	calls the imported methods, sitDown() and getUp() to do so.

	Future Implementation: Later, the Avatar will receive a mode change
	along with a class ID (or perhaps instance ID - I am not sure about
	sending instance IDs because the instance might not have arrived to
	the client at the time of the mode change.). This class ID will be
	sent the mode change by the player and its echoes, removing the need
	for the Avatar to know about the Seat class.


	Client/Server Procedure for Getting Up:

	Present Implementation: At present, the player will check its useKey
	method and eventually decide to call its seat instance's use method.

	Future Implementation: Not decided yet. Perhaps during the change of
	state, the Avatar calls a well-defined method, which is added-to
	when the Avatar sits down.

	The seat's use method will send a get-up request to the server's Seat.
	This will cause the Seat to request its owner to initiate a mode
	change back to Avatar.MODE_NONE. The server Avatar will send a reply
	back to the server Seat, telling it that the Avatar is now standing up.
	The server Seat will then set its ownerID back to zero, freeing itself
	for any subsequent sit-down requests.

	Setting the ownerID property back to zero will propagate down to the
	clients. It re-enables the targetable capability of the Seat, making
	it available for use.

	Changing the server Avatar's mode will propagate down to the clients;
	which in turn, initiate the actions needed to return to a standing
	position.


	Enactment Procedure for Sitting Down:

	The entity's position and yaw do not change as a result of the sitting
	down. Rather, it is the model's position and yaw that are changed.
	The first step requires that the action matcher is decoupled from the
	entity. If the entity is the player and not an echo, it must also
	ensure that the entity's position is not inherited by the model once
	the action is complete, ie. calling actionComplete(). This is because
	the player's override of actionComplete() will force the ActionMatcher
	to recouple the model with the entity's position and yaw.

	Due to collisions for client-side entities, each echo of the player
	may ended up in a slightly different place. To ensure that the model is
	in the right place, its yaw and position are set to that of the entity
	before the animation is played. Collision detection is turned off for
	that entity as well.

	The SitOnChair action is played first, while scheduling the IdleOnChair
	action to immediately start roughly at the end of it. Simultaneously,
	as the SitOnChair animation is ending, the sitDownEnded callback method
	is invoked.

	Since the SitOnChair is a coordinated action, it will have its first
	frame transform inversely applied to each frame of the animation,
	leaving it to start at 'origin' instead of the offset. This makes the
	model appear to move from its current position into that of the chair.
	Unfortunately, as soon as the animation is finished, it must teleport
	the model to the new position otherwise the model will bounce back to
	its old position when the ActionMatcher defaults the next action to
	idle standing. The sitDownEnded method uses the nextFrameTeleport
	to do this when it is called after the end of the SitOnChair action.

	The nextFrameTeleport method is used to move the Avatar's model between
	the start and end of the SitOnChair and RiseFromChair animations, and
	vice-versa.

	It is important to force the IdleOnChair action to be scheduled
	immediately after the SitOnChair action. Hence the explicit callback()
	was set up. Without it, the action matcher will still try to blend with
	the standing idle, causing the model to bounce back to its old position
	for a single frame. This produces the flicker effect.

	Likewise, when doing the teleport, the move has to occur just after the
	SitOnChair has blended out and on the first frame of the newly started
	IdleOnChair. The IdleOnChair has the same reference point as the
	standing idle action, and hence will appear to bounce the model back
	to the old position if not timed properly.

	Once the teleport is done. The actionComplete method can be called
	for the sit-down part of nextFrameTeleport. Since the positions are
	not inherited on recoupling, the player's entity position will not be
	affected by the model's new position.


	Enactment Procedure for Getting Up:

	The rise methods are similar. The concept is similar, move the model's
	position and yaw, but leave the entity's actual position and yaw alone.

	It may seem strange to teleport the model on the first frame of the
	RiseFromChair action, but the properties of a coordinated action are
	asymmetric for animations played in reverse. That means, the inverse
	transform of the first frame is applied to every frame, not the
	inverse transform of the last frame, as might be expected for the
	animation.

	This would force the first frame to be a negative offset to the
	model's present position. The counter to this is to move the model's
	position to the inverse of the seek position (position offset from
	the origin at the start of the animation.) The offset would then
	place the model back at it's old current position.

	This teleport has to be at the very start of the RiseFromChair
	animation, hence the next-frame call-back for nextFrameTeleport.

	Finally, only when the RiseFromChair action is complete, can the
	actionComplete() method is called. Calling it earlier will allow
	the player to move around before the animation is done.
	"""



	############################################################################
	# The following are member functions that override the BigWorld.Entity     #
	# class or are intrinsic to the class itself (ie, the constructor).        #
	############################################################################


	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Defines all variables used by the seat entity. This includes
	#	  setting variables to None.
	#	- Does not call any of the accessor methods. Any variables set are
	#	  for the purposes of stability.
	#	- Checks built-in properties set by the client.
	# --------------------------------------------------------------------------
	def __init__( self ):
		#
		# Initialise the parent component (BigWorld.Entity).
		#
		BigWorld.Entity.__init__( self )

		#
		# Set all standard entity variables.
		#
		self.targetCaps = [ Caps.CAP_CAN_USE ]
		self.filter = BigWorld.DumbFilter()
		self.model = None
		self.playerWaitingToSit = False

		#
		# Set seat specific variables.
		#
		self.checkProperties()
		
		
	# ------------------------------------------------------------------------------
	# Method: prerequisites
	# Description:
	#	- This method is called between __init__ and onEnterWorld, and allows the
	#	class to load any resources it will need.  By the time this is called, all
	#	of the entity properties are set and can be used to determine exactly which
	#	resources to ask for.
	# ------------------------------------------------------------------------------
	def prerequisites( self ):
		return [ SeatData.modelNames[self.seatType] ]


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# Description:
	#	- Overridden from BigWorld.Entity
	#	- Called when entity is to become a part of the game universe.
	#	- Sets the model for the seat.
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		#
		# Make sure the model is properly set.
		#
		self.set_seatType()

		#
		# Set target capabilities according to ownerID.
		#
		self.set_ownerID()
		
		#
		# Create a minimap icon
		#
		Minimap.addEntity( self )


	# --------------------------------------------------------------------------
	# Method: onLeaveWorld
	# Description:
	#	- Overridden from BigWorld.Entity
	#	- Called when entity is to be removed from the game universe.  Does nothing in this case
	# --------------------------------------------------------------------------
	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model = None



	# --------------------------------------------------------------------------
	# Method: name
	# Description:
	#	- Overridden from BigWorld.Entity
	#	- Allows the client to get a string name for the entity.
	# --------------------------------------------------------------------------
	def name( self ):
		return SeatData.displayNames[ self.seatType ]


	# --------------------------------------------------------------------------
	# Method: modeTargetFocus
	# Description:
	#	- Overridden from BigWorld.Entity
	#	- Notifies the entity that it has been targeted.  Does nothing in this case.
	# --------------------------------------------------------------------------
	def modeTargetFocus( self, targeter ):
		pass


	# --------------------------------------------------------------------------
	# Method: modeTargetBlur
	# Description:
	#	- Overridden from BigWorld.Entity
	#	- Notifies the entity that it has been untargeted.  Does nothing in this case.
	# --------------------------------------------------------------------------
	def modeTargetBlur( self, targeter ):
		pass


	############################################################################
	# These member functions are used by BigWorld to inform entity when a      #
	# value has been changed.  The name is derived from the property name      #
	# described in the associated Entity Definition File.                      #
	############################################################################


	# --------------------------------------------------------------------------
	# Method: set_seatType
	# Description:
	#	- Called by the client when the cell sends an update.
	#	- Should also be called by the script, rather than setting variable directly.
	# --------------------------------------------------------------------------
	def set_seatType( self, oldType = None ):
		methodName = "Seat.set_seatType: "

		if self.seatType == oldType:
			return

		#
		# Force effect type to a legal value.
		#
		if not self.seatType in SeatData.displayNames.keys():
			print methodName + "seatType set to illegal value."
			self.seatType = SeatData.UNKNOWN

		#
		# Make sure the model is properly set.
		#
		if not self.seatType in SeatData.modelNames.keys():
			self.model = None
			print methodName + "seatType has no model."
		else:
			self.model = BigWorld.Model( SeatData.modelNames[ self.seatType ] )
			if self.model != None:
				self.model.motors[0].collisionRooted = 1


	# --------------------------------------------------------------------------
	# Method: set_ownerID
	# Description:
	#	- Called by the client when the server sends an update.
	#	- Should also be called by the script, rather than setting variable directly.
	# --------------------------------------------------------------------------
	def set_ownerID( self, oldOwnerID = None ):
		if self.ownerID == oldOwnerID:
			return

		#
		# Set target capabilities.
		#
		if self.ownerID == 0:
			self.targetCaps = [ Caps.CAP_CAN_USE ]
			if self.model != None:
				self.model.motors[0].entityCollision = 0
		else:
			self.targetCaps = []
			if self.model != None:
				self.model.motors[0].entityCollision = 1

		#
		# Break player out of waiting mode if player was waiting to sit down,
		# but someone else sat down first.
		#
		if self.playerWaitingToSit:
			self.playerWaitingToSit = False
			if self.ownerID != BigWorld.player().id:
				self.sitDownCancelled()
			

	# --------------------------------------------------------------------------
	# Note:  No need to implement set_channel() as it was declared as PRIVATE, hence won't be changed by BigWorld.
	# The variable may still be changed by other means, however...
	# --------------------------------------------------------------------------


	############################################################################
	# The following are additional member functions that are used by other     #
	# scripts or internal to this class.  BigWorld is not aware of them.       #
	############################################################################


	# --------------------------------------------------------------------------
	# Method: checkProperties
	# Description:
	#	- Checks all properties defined in the XML file to see if they are
	#	  valid.
	# --------------------------------------------------------------------------
	def checkProperties( self ):
		methodName = "Seat.checkProperties: "

		#
		# Make sure seatType is defined.
		#
		if not hasattr( self, "seatType" ):
			self.seatType = SeatData.UNKNOWN
			print methodName + "seatType not initialised."
		else:
			if not self.seatType in SeatData.displayNames.keys():
				self.seatType = SeatData.UNKNOWN
				print methodName + "seatType initialised to illegal value."


	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- Provides interface to interact with entity, in this case, it allows the user to sit down on the seat.
	# --------------------------------------------------------------------------
	def use( self ):
		if Caps.CAP_CAN_USE in self.targetCaps and self.ownerID == 0:
			self.moveToSitDownPosition()
		else:
			player = BigWorld.player()
			if self.ownerID == player.id and not player.waitingToStand:
				player.waitingToStand = True
				player.actionCommence()
				self.cell.getUpRequest()


	# --------------------------------------------------------------------------
	# Method: moveToSitDownPosition
	# Description:
	#	- This method moves the player to the position required for
	#	  sitting down.
	# --------------------------------------------------------------------------
	def moveToSitDownPosition( self ):
		player = BigWorld.player()
		pos = Vector3( self.position )

		player.seeker.seekPath( player,
			player.model.SitOnChair.getSeekInv(
				pos.x, pos.y, pos.z, self.yaw + math.pi ),
			player.walkFwdSpeed,
			5,
			0.30,
			self.moveToSitDownPositionEnded )
		player.am.turnModelToEntity = True


	# --------------------------------------------------------------------------
	# Method: moveToSitDownPositionEnded
	# Description:
	#	- This method should only be used by the moveToSitDownPosition()
	#	  method as a call-back after the seek (move-to) phase has occurred.
	#	- The move-to phase could fail, hence the success flag has to be
	#	  checked.
	# --------------------------------------------------------------------------
	def moveToSitDownPositionEnded( self, success ):
		player = BigWorld.player()
		player.actionCommence()

		if not success or self.ownerID != 0:
			self.sitDownCancelled()
		else:
			# TBD:PW The wait period is only to allow the other clients to
			# catch up - this is a temporary solution until the client has
			# a proper implementation of event queues.
			self.playerWaitingToSit = True
			BigWorld.callback( 0.5, self.cell.sitDownRequest )
			# Set the mode target here because it's an other clients property
			player.modeTarget = self.id


	# --------------------------------------------------------------------------
	# Method: sitDownCancelled
	# Description:
	#	- This method should only be used by the moveToSitDownPosition()
	#	  method as a call-back after the seek (move-to) phase has occurred.
	#	- The move-to phase could fail, hence the success flag has to be
	#	  checked.
	# --------------------------------------------------------------------------
	def sitDownCancelled( self ):
		player = BigWorld.player()
		player.model.Shrug( 0, player.actionComplete )


#####################
# End of class Seat #
#####################


############################################################################
# The following functions do not really belong to the seat.  Rather, they  #
# represent the functionality of the entity interacting with the seat.     #
############################################################################


# ------------------------------------------------------------------------------
# Method: sitDown
# Description:
#	- This is a class method called by an Avatar when it changes
#	  state to Avatar.MODE_SEATED.
#	- It begins the sit-down animation and times the seated idle
#	  animation to occur directly after it by using a call-back method.
# ------------------------------------------------------------------------------
def sitDown( entity ):
	# don't sit back down if we're in the middle of standing up.
	if entity.isStandingUp == True:
		return

	entity.am.entityCollision = False

	if entity == BigWorld.player():
		entity.am.inheritOnRecouple = False
	else:
		entity.am.turnModelToEntity = True
		entity.actionCommence()

	entity.am.matcherCoupled = False

	lastKnownSeat = BigWorld.entity(entity.modeTarget)
	#~ print entity
	#~ print entity.id
	#~ print entity.modeTarget
	#~ print lastKnownSeat
	pos = Vector3( entity.position )
	seekPos = entity.model.SitOnChair.getSeekInv( pos.x, pos.y, pos.z,
		lastKnownSeat.yaw + math.pi )

	entity.model.yaw = seekPos[3]
	#entity.model.yaw = entity.yaw
	entity.model.position = entity.position

	if lastKnownSeat.seatType == SeatData.WOODEN_STOOL | lastKnownSeat.seatType == SeatData.LOSPEC_STOOL:
		sound = "players/sit_stool"
	else:
		sound = "players/sit_generic"
	#if entity.modelNumber == nn:
	#	sound = "players/sit_armour"	
	# BigWorld.playFx(sound, entity.position)

	entity.model.SitOnChair().SitOnChairEnd()
	entity.sitIdleCalbackID = BigWorld.callback( entity.model.SitOnChair.duration,
		partial( sitDownEnded, entity.id ) )


# ------------------------------------------------------------------------------
# Method: sitDownEnded
# Description:
#	- This is the call-back method used by the sitDown() method when
#	  its sit-down animation is completed.
#	- The entity sitting down does not have its position changed; only
#	  its model positions need to be teleported at the end of this
#	  routine.
# ------------------------------------------------------------------------------
def sitDownEnded( entityID ):
	entity = BigWorld.entity( entityID )
	if entity is None:
		return
	entity.sitIdleCalbackID = None
	entity.model.IdleOnChair()
	nextFrameTeleport( entity, 0 )


# ------------------------------------------------------------------------------
# Method: standUp
# Description:
#	- This is a class method called by an Avatar when it leaves the
#	  Avatar.MODE_SEATED state.
#	- It begins the get-up animation and times the model teleport back
#	  to the the entity's actual position.
# ------------------------------------------------------------------------------
def standUp( entity ):
	# stop the player from attempting to sit if we want to stand up
	entity.isStandingUp = True
	# kill the sitting idle callback if we were starting to sit
	if entity.sitIdleCalbackID != None:
		BigWorld.cancelCallback( entity.sitIdleCalbackID )
		entity.sitIdleCalbackID = None
		nextFrameTeleport( entity, 0 )
		
	if entity == BigWorld.player():
		if not entity.waitingToStand:
			entity.actionCommence()
		entity.waitingToStand = False

	entity.am.entityCollision = False

	nextFrameTeleport( entity, 1 )
	entity.model.RiseFromChair().Idle()
	BigWorld.callback( entity.model.RiseFromChair.duration + 0.1,
		partial( standUpEnded, entity.id ) )

	# BigWorld.playFx("players/unsit_stool", entity.position)



# ------------------------------------------------------------------------------
# Method: standUpEnded
# Description:
#	- This is the class call-back method used by the standUp() method
#	  when its stand-up animation is completed.
# ------------------------------------------------------------------------------
def standUpEnded( entityID ):
	entity = BigWorld.entity( entityID )
	if entity is None:
		return
	entity.model.Idle.stop()
	entity.actionComplete()
	entity.isStandingUp = False


# ------------------------------------------------------------------------------
# Method: nextFrameTeleport
# Description:
#	- This is a class call-back method that activates at the next
#	  frame. It is necessary to use a call-back method to ensure that
#	  the model teleport occurs after the animation has ended.
#	- The paramater animation is 0 for the sit-down and 1 for the stand-up
#	  animations respectively.
# ------------------------------------------------------------------------------
def nextFrameTeleport( entity, animation ):
	oldModelPos = Vector3( entity.model.position )

	if animation == 0:
		newModelPos = entity.model.SitOnChair.getSeek(
			oldModelPos.x, oldModelPos.y, oldModelPos.z, entity.model.yaw )
		entity.am.entityCollision = False
	elif animation == 1:
		newModelPos = entity.model.SitOnChair.getSeekInv(
			oldModelPos.x, oldModelPos.y, oldModelPos.z, entity.model.yaw )
		entity.am.entityCollision = True
	else:
		newModelPos = ( oldModelPos.x, oldModelPos.y, oldModelPos.z,
			entity.model.yaw )

	entity.model.position = newModelPos[0:3]
	entity.model.yaw = newModelPos[3]

	if entity == BigWorld.player():
		FantasyDemo.camera(0).limitVelocity = 1

	if animation == 0:
		entity.actionComplete()


##################
# End of Seat.py #
##################
