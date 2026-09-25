import BigWorld
from FDGUI import Minimap
from GameData import MovingPlatformData

# This implements the MovingPlatform on the Client.
class MovingPlatform( BigWorld.Entity ):
	
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		
		if not hasattr( self, "platformType" ):
			self.platformType = MovingPlatformData.DEFAULT
		else:
			if not self.platformType in MovingPlatformData.modelNames.keys():
				self.platformType = MovingPlatformData.DEFAULT

	def prerequisites( self ):
		return [ MovingPlatformData.modelNames[self.platformType] ]


	# This is called by BigWorld when the Entity enters AoI, through creation or movement.
	def onEnterWorld( self, prereqs ):
		self.set_platformType()

		# Set appropriate filter for server controlled Entity
		self.filter = BigWorld.AvatarFilter()
		self.model.vehicleID = self.id

		Minimap.addEntity( self )
	
	# --------------------------------------------------------------------------
	# Method: set_platformType
	# Description:
	#	- Called by the client when the cell sends an update.
	#	- Should also be called by the script, rather than setting variable directly.
	# --------------------------------------------------------------------------
	def set_platformType( self, oldType = None ):
		methodName = "MovingPlatform.set_platformType: "

		if self.platformType == oldType:
			return

		#
		# Force to a legal value.
		#
		if not self.platformType in MovingPlatformData.modelNames.keys():
			print methodName + "platformType set to illegal value."
			self.platformType = MovingPlatformData.DEFAULT

		#
		# Make sure the model is properly set.
		#
		if not self.platformType in MovingPlatformData.modelNames.keys():
			self.model = None
			print methodName + "platformType has no model."
		else:
			self.model = BigWorld.PyModelObstacle( MovingPlatformData.modelNames[ self.platformType ], self.matrix, True )
			self.model.vehicleID = self.id

	# This is called by BigWorld when the Entity leaves AoI, through creation or movement.
	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model = None


	def name( self ):
		return "Moving Platform"


# MovingPlatfrom.py
