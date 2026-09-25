
from Wield import Wield

import BigWorld
import Math
import Pixie

from functools import partial

from bwdebug import *

class Axe( Wield ):
	'''This class is for testing local node offsets.'''

	PARTICLE_NAME = "particles/staff_fireball.xml"
	
	def __init__( self, itemType, prereqs = None ):
		Wield.__init__( self, itemType, prereqs )

		# Particle system is rotated
		self.particleRotation = Math.Matrix()
		self.particleRotation.setRotateY( 90.0 )

		# Something to attach to axe
		Pixie.createBG( Axe.PARTICLE_NAME, self.onAttachedItem1Created )

	def onAttachedItem1Created( self, attachedItem ):
		self.attachedItem1 = attachedItem

		if self.attachedItem1 is None:
			ERROR_MSG( "Axe.onAttachedItem1Created failed to load test asset" )
			return

		# Offset from root node
		self.offsetMatrix1 = Math.Matrix()

		# Get root node with local offset
		self.node1 = self.model.node( '', self.offsetMatrix1 )
		self.node1.attach( self.attachedItem1 )

		# Attach to one side of axe
		self.offsetMatrix1.setTranslate( (-0.5, 0, 0) )

		# Particle system is rotated
		self.offsetMatrix1.preMultiply( self.particleRotation )
		
		Pixie.createBG( Axe.PARTICLE_NAME, self.onAttachedItem2Created )

	def onAttachedItem2Created( self, attachedItem ):
		self.attachedItem2 = attachedItem

		if self.attachedItem2 is None:
			ERROR_MSG( "Axe.onAttachedItem2Created failed to load test asset" )
			return

		# Offset from root node
		self.offsetMatrix2 = Math.Matrix()

		# Get root node with local offset
		self.node2 = self.model.node( '', self.offsetMatrix2 )
		self.node2.attach( self.attachedItem2 )

		# Attach to other side of axe
		self.offsetMatrix2.setTranslate( (+0.5, 0, 0) )

		# Particle system is rotated
		self.offsetMatrix2.preMultiply( self.particleRotation )

	def use( self, user, target ):

		if user is None:
			return False

		user.model.SwingSword()

		return True
