import BigWorld
from Helpers import Caps
import random
from FDGUI import Minimap


STATE_FLYING = 0
STATE_LANDING = 1

NUM_BOIDS = 30

# ------------------------------------------------------------------------------
# Section: class Flock
# ------------------------------------------------------------------------------

class Flock( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.targetCaps = [ Caps.CAP_NEVER ]
		self.filter = BigWorld.BoidsFilter()
		
		
	def prerequisites( self ):
		list = []
		for i in xrange(0,NUM_BOIDS):
			 list.append( "characters/npc/crow/crow.model" )
		return list	


	def onEnterWorld( self, prereqs ):
		boidModels = prereqs.values()
		for model in boidModels:			
			model.outsideOnly = 1
			self.addModel( model )
			model.Flap( -5 * random.random() )

		for boid in self.models:
			boid.visible = (self.state == STATE_FLYING)

		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		self.models = []


	def set_state( self, oldState ):
		assert( 1 or oldState ) # Not used

		if self.state == STATE_FLYING:
			for boid in self.models:
				boid.visible = 1


	def boidsLanded( self ):
		landedBoids = filter(lambda x, pos=self.position: x.position == pos, self.models)
		for boid in landedBoids:
			boid.visible = 0
			
	def name( self ):
		return "Flock"


#Flock.py
