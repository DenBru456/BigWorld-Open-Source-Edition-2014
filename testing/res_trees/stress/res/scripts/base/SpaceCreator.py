import BigWorld

class SpaceCreator( BigWorld.Base ):

	def __init__( self ):
		BigWorld.Base.__init__( self )

		# Create this entity in a new space
		self.createInNewSpace( shouldPreferThisMachine = True )
		self.cell.addGeometryMapping( self.spaceDir )
		
	def onLoseCell( self ):
		# Once our cell entity is destroyed, it's safe to clean up the Proxy.
		# We can't just call self.destroy() in onClientDeath() above, as
		# destroyCellEntity() is asynchronous and the cell entity would still
		# exist at that point.
		self.destroy()
