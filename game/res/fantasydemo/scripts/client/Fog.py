import BigWorld
from FDGUI import Minimap

# ------------------------------------------------------------------------------
# Class Fog:
#
# Fog is the invisible entity that provides an area of fog
#
# These create method dictates the look at behaviour of the effect.
#
# ------------------------------------------------------------------------------

class Fog( BigWorld.Entity ):

	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Defines all variables used by the Fog. This includes
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
		self.targetCaps = []
		self.filter = BigWorld.AvatarDropFilter()
		self.model = BigWorld.Model( "" )

		#
		# Set fog emitter specific variables.
		#
		self.density = 5
		self.innerRadius = 35
		self.outerRadius = 50
		self.colour = ( self.red << 16 ) \
				| ( self.green << 8 ) \
				| ( self.blue )		
		self.emitterID = None		

	# TODO : need a set_Red, set_Green, set_Blue etc.

	# --------------------------------------------------------------------------
	# Method: checkProperties
	# Description:
	#	- Checks all properties defined in the XML file to see if they are
	#	  valid.
	# --------------------------------------------------------------------------
	def checkProperties( self ):
		# methodName = "Fog.checkProperties: "
		pass


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# Description:
	#	- Sets a time for the effect in appear after the model anchor has been
	#	  drawn.
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		self.emitterID = BigWorld.addFogEmitter( 
				self.position,
				self.density,
				self.innerRadius ,
				self.outerRadius ,
				self.colour,
				True )
		Minimap.addEntity( self )


	# --------------------------------------------------------------------------
	# Method: onLeaveWorld
	# Description:
	#	- Destroys the fog emitter
	# --------------------------------------------------------------------------
	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		BigWorld.delFogEmitter( self.emitterID )
		self.emitterID = None


	# --------------------------------------------------------------------------
	# Method: name
	# Description:
	#	- Part of the entity interface: This allows the client to get a string
	#	  name for the fogEmitter.
	# --------------------------------------------------------------------------
	def name( self ):
		return "Fog"


#Fog.py
