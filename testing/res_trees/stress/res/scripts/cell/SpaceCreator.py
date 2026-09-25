import BigWorld

class SpaceCreator( BigWorld.Entity ):

	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def onDestroy( self ):
		# Destroy this space and all entities in it
		self.destroySpace()

	def addGeometryMapping( self, geometryToMap ):
		#This base informs us what geometry to map
		BigWorld.addSpaceGeometryMapping( self.spaceID, None, geometryToMap )
