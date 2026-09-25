"This module implements the Seat entity."

import BigWorld
import AvatarMode as Mode
import bwdecorators

# ------------------------------------------------------------------------------
# Section: class Seat
# ------------------------------------------------------------------------------

class Seat( BigWorld.Entity ):
	"A Seat entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def sitDownRequest( self, entityID ):
		if self.ownerID == 0:
			self.ownerID = entityID
			BigWorld.entities[ self.ownerID ].enterMode( self.ownerID,
				Mode.SEATED, self.id, 0 )

	def getUpRequest( self, entityID ):
		if self.ownerID == entityID:
			BigWorld.entities[ self.ownerID ].cancelMode( self.ownerID )
			# The Avatar's cancelMode() method will in-turn call this
			# Seat's ownerNotSeated() method to release itself.

	def ownerNotSeated( self ):
		self.ownerID = 0

	@bwdecorators.callableOnGhost
	def onEnteringCell( self ):
		# print "Seat.onEnteringCell:", self.id
		pass

	def onEnteredCell( self ):
		# print "Seat.onEnteredCell:", self.id
		pass

	def onLeavingCell( self ):
		# print "Seat.onLeavingCell:", self.id
		pass

	@bwdecorators.callableOnGhost
	def onLeftCell( self ):
		# print "Seat.onLeftCell:", self.id
		pass

# Seat.py
