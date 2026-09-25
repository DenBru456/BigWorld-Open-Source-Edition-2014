"""This module implements a light weight Guard entity type."""


import BigWorld
from Avatar import makeModel
from Helpers import Caps
from FDGUI import Minimap


# ------------------------------------------------------------------------------
# Section: class Guard
# ------------------------------------------------------------------------------


class LightGuard( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.canSeePlayer_ = 0
		self.am = BigWorld.ActionMatcher( self )


	def onEnterWorld( self, prereqs ):
		self.am.turnModelToEntity = 0
		self.am.matcherCoupled = 1
		self.am.matchCaps = [2,]
		self.am.entityCollision = 1
		self.am.collisionRooted = 0
		self.am.footTwistSpeed = 0

		self.targetCaps = [ Caps.CAP_CAN_HIT , Caps.CAP_CAN_USE ]
		self.filter = BigWorld.AvatarDropFilter()
		self.set_modelNumber()
		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		#selfAvatar.onLeaveWorld()
		self.targetCaps = [ Caps.CAP_NEVER ]
		Minimap.delEntity( self )
		self.model = None


	def set_modelNumber( self, oldNumber = None ):
		nm = makeModel( self.modelNumber, self.model )
		self.model = nm

		if self.am.owner != None: self.am.owner.delMotor( self.am )
		self.model.motors = ( self.am, )


	def name( self ):
		return "Light Guard"

	def use( self ):
		pass

# LightGuard.py
