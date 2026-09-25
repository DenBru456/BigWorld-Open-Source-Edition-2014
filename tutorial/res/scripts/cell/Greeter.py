import BigWorld
import Avatar
import random

MESSAGES = [ 
	"Hello BigWorld", 
	"Have a nice day", 
	"I greet, therefore I am" 
]

class Greeter( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )

		# We've just been created. We will set up our trap in here.
		self.addProximity( self.radius, 0 )

	def onEnterTrap( self, entityEntering, range, controllerID ):
		print "Greeter.onEnterTrap", self.id, entityEntering, range, controllerID, self.activated

		# If we are not active, do nothing.
		if not self.activated:
			return

		# An entity has entered the trap. Since we get notified when any
		# entity enters the trap, we need to filter it out by type.
		if not isinstance( entityEntering, Avatar.Avatar ):
			return

		# Tell all the clients that we are greeting this person.
		self.allClients.greet( entityEntering.id, random.choice(MESSAGES) )		


	def toggleActive( self, sourceID ):
		# Called from the client to toggle our activation state.
		# Note that the Exposed keyword adds an argument containing the ID of 
		# the Avatar entity who called us. We can use this for validation such 
		# as making sure they are close enough to perform this action.

		print "Greeter.toggleActive (self.id=%d, sourceID=%d)" % (self.id, sourceID)

		# Get the entity who called us. If the entity can't be found then they
		# obviously not near by so just bail out.
		try:
			sourceEntity = BigWorld.entities[ sourceID ]
		except KeyError:
			return

		# Get the distance between ourself and the Avatar
		dist = sourceEntity.position.distTo( self.position )

		# Do a check to make sure they are close enough.
		if dist > self.radius:
			return

		# All good, toggle our state. The activated property will be automatically 
		# propagated to all clients once this server tick is complete.
		self.activated = not self.activated

# Greeter.py 
