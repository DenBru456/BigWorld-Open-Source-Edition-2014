import BigWorld

# ------------------------------------------------------------------------------
# Section: class RipperBot
# ------------------------------------------------------------------------------

class RipperBot( BigWorld.Proxy ):
	def __init__( self ):
		BigWorld.Proxy.__init__( self )
		
	def clientDead( self ):
		print "Help: The base just told us (ripper %d) we're dead!" % self.id
		self.cell.die()

	def onLoseCell( self ):
		self.destroy()

# RipperBot.py
