
import BigWorld
import Pixie
from Helpers import Caps
from functools import partial
from FDGUI import Minimap
import random

# ------------------------------------------------------------------------------
# Class Effect:
#
# Effect is the invisible entity that covers spawning of special particle
# effects. Within each different type of effect is a create method.
#
# eg. for the RISING_STREAM effect, there is a createRisingSteam() method;
#     for the BONFIRE effect, there is a createBonfire() method.
#
# These create methods dictate the look and behaviour of the effect. Resource
# editors may modify these methods directly by changing the code inside these
# methods or by changing the parameters passed to them when called in the
# createParticleSystem() method call.
#
# The createParticleSystem() method is the method called by the script to
# generate the particle system representing the effect entity. It in turn
# calls the appropriate create method for the effect.
# ------------------------------------------------------------------------------

class Effect( BigWorld.Entity ):
	# --------------------------------------------------------------------------
	# Every type of entity has a group of sub-types. The effects entity has
	# different types of special effects.
	#
	# The UNKNOWN type value means that the exact effect has not yet been
	# determined. It means that the server will change the type later as
	# more information is allowed to the client.
	# --------------------------------------------------------------------------
	UNKNOWN			= 0		# Use this if no one knows what the effect is.
	RISING_STEAM	= 1		# The steam from grates effect.
	BONFIRE			= 2		# The bonfire with animated fire texture.
	BONFIRE_TWO		= 3		# REDUNDANT: Pure particle flame bonfire. Do not
							# use this because the animated texture fire is
							# more efficient.
	CHIMNEY_SMOKE	= 4		# Rising wisps of smoke into the sky.
	ENERGY_SPHERE	= 5		# Energy stream with trails in a sphere.
	JET_STREAM		= 6		# Steam being jetted from a pipe.
	GROUND_MIST		= 7		# Metre Square block of ground mist.


	# --------------------------------------------------------------------------
	# The displayNames list contains the displayable names for the sub-types
	# of entities. Every type of effects entity has to have a display name.
	# It is safe to check for a valid entity type by looking for it in this
	# dictionary. That is, if the type is found, the entity has a valid type.
	# --------------------------------------------------------------------------
	displayNames = {
		UNKNOWN:			"Unidentified Effect",
		RISING_STEAM:		"Rising Steam",
		BONFIRE:			"Bonfire",
		BONFIRE_TWO:		"Bonfire Old-Style",
		CHIMNEY_SMOKE:		"Chimney Smoke",
		JET_STREAM:			"Jet-Stream",
		ENERGY_SPHERE:		"Energy Sphere",
		GROUND_MIST:		"Ground Mist"
	}
	
	
	particleSystems = {
		UNKNOWN:			"",
		RISING_STEAM:		"particles/rising_steam.xml",
		BONFIRE:			"particles/bonfire.xml",
		BONFIRE_TWO:		"particles/bonfire_two.xml",
		CHIMNEY_SMOKE:		"particles/chimney_smoke.xml",
		JET_STREAM:			"particles/jet_stream.xml",
		ENERGY_SPHERE:		"particles/energy_sphere.xml",
		GROUND_MIST:		"particles/ground_mist.xml"
	}		


	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Defines all variables used by the effect entity. This includes
	#	  setting variables to None.
	#	- Does not call any of the accessor methods. Any variables set are
	#	  for the purposes of stability.
	#	- Checks built-in properties set by the client.
	#	- Builds the list binding actionIDs to actions.
	# --------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity.__init__( self )

		#
		# Set all standard entity variables.
		#
		self.targetCaps = [ Caps.CAP_NEVER ]
		self.filter = BigWorld.DumbFilter()
		self.model = BigWorld.Model( "" )
		self.focalMatrix = self.model.matrix
		self.system = None

		#
		# Set swarm specific variables.
		#
		self.checkProperties()
		
		
	# --------------------------------------------------------------------------
	# Method: prerequisites
	# Description:
	#	- List all resources needed when we enter the world.  These will be
	#	loaded in the background and passed into the onEnterWorld method.
	# --------------------------------------------------------------------------
	def prerequisites( self ):
		return (Effect.particleSystems[self.effectType],)


	# --------------------------------------------------------------------------
	# Method: checkProperties
	# Description:
	#	- Checks all properties defined in the XML file to see if they are
	#	  valid.
	# --------------------------------------------------------------------------
	def checkProperties( self ):
		methodName = "Effect.checkProperties: "

		#
		# Force effectType to a legal value.
		#
		if not hasattr( self, "effectType" ):
			self.effectType = Effect.UNKNOWN
			print methodName + "effectType not initialised."
		else:
			if not self.effectType in Effect.displayNames.keys():
				self.effectType = Effect.UNKNOWN
				print methodName + "effectType initialised to illegal value."

		#
		# Build the effect's name.
		#
		self.effectName = Effect.displayNames[ self.effectType ]


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# Description:
	#	- Sets a time for the effect in appear after the model anchor has been
	#	  drawn.
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		BigWorld.callback( 0.0, partial(self.createParticleSystem,prereqs) )
		Minimap.addEntity( self )


	# --------------------------------------------------------------------------
	# Method: onLeaveWorld
	# Description:
	#	- Destroys the particle system for the effect.
	# --------------------------------------------------------------------------
	def onLeaveWorld( self ):
		Minimap.delEntity( self )


	# --------------------------------------------------------------------------
	# Method: changeTo
	# Description:
	#	- Changes the effectType of the Effect to the value supplied.
	#	- This is a method for debugging purposes to quickly change the type
	#	  of an Effect.
	# --------------------------------------------------------------------------
	def changeTo( self, newType ):
		oldType = self.effectType
		self.effectType = newType
		self.set_effectType( oldType )


	# --------------------------------------------------------------------------
	# Method: set_effectType
	# Description:
	#	- Accessor for the effectType property.
	#	- Called by the client when the server sends an update.
	#	- Should be called by the script when changing the effectType variable.
	# --------------------------------------------------------------------------
	def set_effectType( self, oldType = None ):
		if self.effectType == oldType:
			return

		#
		# Delete the old particle system for the effect.
		#
		if self.system:
			self.model.root.detach( self.system )
			self.system = None

		#
		# Force effect type to a legal value.
		#
		if not self.effectType in Effect.displayNames.keys():
			self.effectType = Effect.UNKNOWN

		#
		# Reset effect name.
		#
		self.effectName = Effect.displayNames[ self.effectType ]

		#
		# Create or recreate the particle system.
		#
		self.createParticleSystem(None)


	# --------------------------------------------------------------------------
	# Method: createParticleSystem
	# Description:
	#	- Dispatches the appropriate method for creating the particle system.
	# --------------------------------------------------------------------------
	def createParticleSystem( self, resourceRefs = None ):
		systemName = Effect.particleSystems[self.effectType]
		
		print "Create EffectType: ", systemName
		#
		# If the resources do not exist, load them in the background.
		#
		if ( resourceRefs == None ):			
			BigWorld.loadResourceListBG((systemName,), self.createParticleSystem)
			return
			
		if self.system != None:
			self.model.root.detach(self.system)
			self.system = None
			
		if systemName in resourceRefs.failedIDs:
			print "EffectType: " + systemName + " failed to load"			
			
		#
		# Create the particle system for the effect depending on its type.
		#
		try:
			self.system = resourceRefs[systemName]
		except KeyError:
			print "Effect entity: Particle system not in resourceRefs", self.id
			return
		except ValueError:
			print "Effect entity: Particle system failed to load", self.id
			return
			
		if self.effectType == Effect.RISING_STEAM:
			self.risingSteamSetup()
		elif self.effectType == Effect.ENERGY_SPHERE:			
			self.energySphereSetup()
			
		if self.system != None:
			self.model.root.attach( self.system )
			
			
	# --------------------------------------------------------------------------
	# Method: energySphereSetup
	# Description:
	#	- Specific setup for energy sphere particles.
	# --------------------------------------------------------------------------
	def energySphereSetup( self ):
		energySphere = self.system
		orbitor = energySphere.system(0).action(10)
		source = energySphere.system(0).action(1)
		sourceRadius = source.getPositionSourceMaxRadius()
		orbitor.point = ( 0, 0 + sourceRadius, 0 )
		
	
	# --------------------------------------------------------------------------
	# Method: risingSteamSetup
	# Description:
	#	- Specific setup for risingSteamSetup particles.
	# --------------------------------------------------------------------------	
	def risingSteamSetup( self ):
		risingSteam = self.system
		for i in xrange( 0, risingSteam.nSystems() ):
			actions = risingSteam.system(i).actions
			for action in actions:
				action.minimumAge = random.random() * 2.0


	# --------------------------------------------------------------------------
	# Method: name
	# Description:
	#	- Part of the entity interface: This allows the client to get a string
	#	  name for the effect.
	# --------------------------------------------------------------------------
	def name( self ):
		return self.effectName


	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#		- Uses the Effect. In most cases, effects cannot be selected nor
	#		  used, but it helps debugging to allow the code to be changed to
	#		  allow it.
	# --------------------------------------------------------------------------
	def use( self ):
		if Caps.CAP_CAN_USE in self.targetCaps:
			player = BigWorld.player()
			player.actionCommence()
			player.model.Shrug( 0, player.actionComplete )


# ------------------------------------------------------------------------------
# A static method which is called to get a list of preload resources.
# ------------------------------------------------------------------------------
def preload( list ):
	preLoadList = []
	
	for i in Effect.particleSystems.values():
		# Preload xml files for particle systems.
		preLoadList.append( i )
		
	list += preLoadList


#Effect.py
