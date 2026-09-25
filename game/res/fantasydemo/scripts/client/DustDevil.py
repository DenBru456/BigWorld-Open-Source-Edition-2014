import BigWorld
import Pixie
import random
from Helpers import Caps
from FDGUI import Minimap

DUMMY_MODEL = "objects/models/null_model.model"
PARTICLE_SYSTEM = "sets/desert/particles/dust_devil.xml"

# ------------------------------------------------------------------------------
# Section: class DustDevil
# ------------------------------------------------------------------------------
class DustDevil( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.targetCaps = [ Caps.CAP_NEVER ]
		self.filter = BigWorld.AvatarDropFilter()

		
	def prerequisites( self ):
		return ( PARTICLE_SYSTEM, DUMMY_MODEL )


	def onEnterWorld( self, prereqs ):
		self.model = prereqs[ DUMMY_MODEL ]
		self.particles = prereqs[ PARTICLE_SYSTEM ]
		self.model.root.attach(self.particles)
		self.model.visibleAttachments = 1
		Minimap.addEntity( self )


	def onLeaveWorld( self ):
		Minimap.delEntity( self )
		if hasattr(self, "particles"):
			self.model.root.detach( self.particles )
			self.particles = None
			del self.particles
		self.model = None

	def name( self ):
		return "Dust Devil"


#DustDevil.py
