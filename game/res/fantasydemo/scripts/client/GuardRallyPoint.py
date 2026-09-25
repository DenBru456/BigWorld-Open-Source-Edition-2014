import BigWorld
import math
from FDGUI import Minimap


# ------------------------------------------------------------------------------
# Section: class GuardRallyPoint
# ------------------------------------------------------------------------------


class GuardRallyPoint( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )


	def prerequisites( self ):
		return [ self.modelName ]


	def onEnterWorld( self, prereqs ):
		self.model = prereqs[self.modelName]
		self.targetCaps = []
		self.filter = BigWorld.DumbFilter()
		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model = None


	def use( self ):
		pass


	def name( self ):
		return 'GuardRallyPoint'


# GuardRallyPoint.py
