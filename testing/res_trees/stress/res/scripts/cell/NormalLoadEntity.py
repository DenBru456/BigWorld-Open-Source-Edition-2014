"This module implements the NormalLoadEntity entity."

import BigWorld
import random

class NormalLoadEntity( BigWorld.Entity ):

	#-------------------------------------------------------------------------
	# Constructor.
	#-------------------------------------------------------------------------

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.moveVelocity = random.randrange( 1, 10 )
		self.move()

	#-------------------------------------------------------------------------
	# This method decides where we want to move to next. It can be anywhere
	# within the space bounds.
	#-------------------------------------------------------------------------

	def move( self ):
		self.moveToPoint( self.generateDestination(), self.moveVelocity )

	#-------------------------------------------------------------------------
	# This method generates a random position on the xz space to move to.
	#-------------------------------------------------------------------------	
	def generateDestination( self ):
		minX = self.spaceBounds['minX']
		minY = self.spaceBounds['minY']
		maxX = self.spaceBounds['maxX']
		maxY = self.spaceBounds['maxY']

		destination = random.randrange( minX, maxX ), 0, random.randrange( minY, maxY )

		return destination

	#-------------------------------------------------------------------------
	# This callback handles when the entity has reached it's destination so
	# that we can give it a new destination to keep it moving.
	#-------------------------------------------------------------------------
	def onMove( self, controllerId, userData ):
		self.move()
