"This module implements the DustDevil entity."

import BigWorld
import Math
import math

# ------------------------------------------------------------------------------
# Section: class DustDevil
# ------------------------------------------------------------------------------


# The dust devil follows a simple path.

XSPEED = 0.3	# metres per tick
ZSPEED = 0.3	# metres per tick
XANGLE = 0.24	# radians per second
ZANGLE = 0.27	# radians per second

class DustDevil( BigWorld.Entity ):
	"A DustDevil entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.addTimer( 0, 0.1 )

	def onTimer( self, timerID, userID ):
		now = BigWorld.time()

		newPosition = Math.Vector3( self.position )
		newPosition.x += XSPEED * math.sin(XANGLE * now)
		newPosition.z += ZSPEED * math.cos(ZANGLE * now)

		rayPosition = Math.Vector3( newPosition)
		rayPosition.y += 10.0

		result = BigWorld.collide( self.spaceID, rayPosition, newPosition )

		if result != None:
			self.position = result[0]
		else:
			self.position = newPosition


# DustDevil.py
