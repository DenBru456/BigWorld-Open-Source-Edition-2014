import BigWorld

# --------------------------------------------------------------------------
# Class:  Avatar
# --------------------------------------------------------------------------
class Avatar( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.clientApp.stop()
