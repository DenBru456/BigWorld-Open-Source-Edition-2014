"This module implements the RipperBot entity."

import BigWorld

# ------------------------------------------------------------------------------
# Section: class RipperBot
# ------------------------------------------------------------------------------

class RipperBot( BigWorld.Entity ):
	"A RipperBot entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		print "Made a ripper"

	def die( self ):
		print "Someone told ripper ", str(self.id), " to die ... bye bye!"
		self.destroy()

# RipperBot.py
