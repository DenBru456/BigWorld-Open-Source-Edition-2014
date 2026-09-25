import BigWorld
from Helpers import Caps
import math
import Beast
from FDGUI import Minimap


# ------------------------------------------------------------------------------
# Section: class AlertBeastTrigger
# ------------------------------------------------------------------------------


class AlertBeastTrigger( BigWorld.Entity ):
	
	MODEL_NAME = "sets/temperate/props/flagstone_slab.model"
	
	def __init__( self ):
		BigWorld.Entity.__init__( self )


	def prerequisites( self ):
		return [AlertBeastTrigger.MODEL_NAME, ]


	def onEnterWorld( self, prereqs ):
		try:
			self.model = BigWorld.PyModelObstacle( AlertBeastTrigger.MODEL_NAME, self.matrix, False )
		except:
			pass
		self.targetCaps = []
		self.filter = BigWorld.DumbFilter()
		self.trap = BigWorld.addPot( self.matrix, self.trapRadius, self.triggerTrap )
		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.model = None
		BigWorld.delPot( self.trap )
		self.trap = 0


	def triggerTrap( self, entered, handle ):
		if BigWorld.player() == None:
			return
		for e in Beast.ENTITIES_IN_WORLD:
			if isinstance( e, Beast.Beast ):
				if (e.position - BigWorld.player().position).length < self.findBeastRadius:
					if entered:
						e.cell.addKnownEntity( BigWorld.player().id )
					else:
						e.cell.removeKnownEntity( BigWorld.player().id )


	def use( self ):
		pass
	

	def name( self ):
		return ''


# AlertBeastTrigger.py
