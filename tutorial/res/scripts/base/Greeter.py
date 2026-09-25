import BigWorld

class Greeter( BigWorld.Base ):

	def __init__( self ):
		BigWorld.Base.__init__( self )

		# The SpaceLoader is telling us which space to create ourselves in by
		# providing a "mailbox" to the cell part of the SpaceLoader. Given this
		# cell mailbox the engine is able to determine where to create our own
		# cell part.
		self.createCellEntity( self.createOnCell )

	def onLoseCell( self ):
		# Destroy ourselves once we've lost our cell part.
		self.destroy()

# Greeter.py
