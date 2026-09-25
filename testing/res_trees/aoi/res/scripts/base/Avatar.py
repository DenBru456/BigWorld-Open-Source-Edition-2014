import BigWorld

# Must derive from BigWorld.Proxy instead of BigWorld.Base if this entity type
# is to be controlled by the player.
class Avatar( BigWorld.Proxy ):

	def __init__( self ):

		BigWorld.Proxy.__init__( self )


	def onClientDeath( self ):

		# When the client disconnects, we want to make sure our cell entity
		# doesn't hang around.
		if self.hasCell:
			self.destroyCellEntity()
		else:
			self.destroy()


	def onLoseCell( self ):

		# Once our cell entity is destroyed, it's safe to clean up the Proxy.
		# We can't just call self.destroy() in onClientDeath() above, as
		# destroyCellEntity() is asynchronous and the cell entity would still
		# exist at that point.
		self.destroy()

# Avatar.py
