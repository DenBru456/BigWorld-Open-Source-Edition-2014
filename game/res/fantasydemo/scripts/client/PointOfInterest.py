import BigWorld
import math
from FDGUI import Minimap

# ------------------------------------------------------------------------------
# Section: class PointOfInterest
# ------------------------------------------------------------------------------


class PointOfInterest( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )


	def prerequisites( self ):
		return []


	def onEnterWorld( self, prereqs ):
		self.targetCaps = [ ]
		self.filter = BigWorld.DumbFilter()
		self.focalMatrix = self.matrix
		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model = None


	def use( self ):
		pass


	def name( self ):
		return ''


# PointOfInterest.py
