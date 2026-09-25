"This module implements the Building entity."

import BigWorld

# ------------------------------------------------------------------------------
# Section: class Building
# ------------------------------------------------------------------------------

class Building( BigWorld.Entity ):
	"A Building entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.modelName = self.models[ self.stage ]

	def construct( self, source ):
		se = BigWorld.entities[ source ]
		if se.position.distSqrTo( self.position ) > 10000: return

		if self.stage < len( self.models ) - 1:
			self.stage += 1
			self.modelName = self.models[ self.stage ]

	def destruct( self, source ):
		se = BigWorld.entities[ source ]
		if se.position.distSqrTo( self.position ) > 10000: return

		if self.stage > 0:
			self.stage -= 1
			self.modelName = self.models[ self.stage ]

# Building.py
