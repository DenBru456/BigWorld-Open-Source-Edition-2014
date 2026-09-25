import time

class CellLayout( object ):
	"""
	This class wraps access to the CellAppMgr's space BSP debugging watchers
	"""

	def __init__( self, cc ):
		self.__spaces = cc.getWatcherData( "spaces", "cellappmgr", None )
		self.__debugging = cc.getWatcherData( "debugging", "cellappmgr", None )
		# Take over load balancing duties now
		# TODO: Other watchers mentioned in "Fixed Cell Boundaries" in
		# "Debugging, Profiling and Benchmarking Guide"
		self.__debugging.getChild( "shouldLoadBalance" ).set( "False" )

	def __getSpaceBSP( self, spaceID ):
		# spaces is keyed by spaceID
		if spaceID is None:
			spaces = self.__spaces.getChildren()
			assert len( spaces ) == 1, "Need SpaceID if more than one space exists"
			spaceBSP = spaces[ 0 ].getChild( "bsp" )
		else:
			spaceBSP = self.__spaces.getChild( str( spaceID ) ).getChild( "bsp" )
		return spaceBSP

	def setLayout( self, spaceID = None ):
		"""
		Four splits, at +- 100 in both horizonal and vertical.
		The idea is to ensure that anything more than 100 units from origin is on a
		different CellApp to the origin
		Split 1: Horizontal@-100=> [(-inf, -inf)=>(inf, -100), (-inf, -100)=>(inf, inf)]
		Split 2: Vertical@-100 in (-inf, -100)=>(inf, inf): [(-inf, -100)=>(-100,inf), (-100, -100)=>(inf,inf)]
		Split 3: Horizontal@100 in (-100, -100)=>(inf,inf): [(-100,-100)=>(inf,100), (-100,100)=>(inf,inf)]
		Split 4: Vertical@100 in (-100,-100)=>(inf,100): [(-100,-100)=>(100,100), (100,-100)=>(inf,100)]
		"""
		spaceBSP = self.__getSpaceBSP( spaceID )
		spaceBSP.getChild( "isLeaf" ).set( "False" )
		time.sleep( 2 )
		spaceBSP.getChild( "position" ).set( "-100.0" )
		spaceBSP.getChild( "left" ).getChild( "isLeaf" ).set( "True" )
		spaceBSP.getChild( "right" ).getChild( "isLeaf" ).set( "False" )
		time.sleep( 2 )
		spaceBSP.getChild( "right" ).getChild( "position" ).set( "-100.0" )
		spaceBSP.getChild( "right" ).getChild( "left" ).getChild( "isLeaf" ).set( "True" )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "isLeaf" ).set( "False" )
		time.sleep( 2 )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "position" ).set( "100.0" )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "left" ).getChild( "isLeaf" ).set( "False" )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "right" ).getChild( "isLeaf" ).set( "True" )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "left" ).getChild( "position" ).set( "100.0" )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "left" ).getChild( "left" ).getChild( "isLeaf" ).set( "True" )
		spaceBSP.getChild( "right" ).getChild( "right" ).getChild( "left" ).getChild( "right" ).getChild( "isLeaf" ).set( "True" )
		# TODO: Ensure that (0,0) in on a different CellApp to the other children.

	def clearLayout( self, spaceID = None ):
		"""
		Get rid of all splits, put everything into one cell
		"""
		spaceBSP = self.__getSpaceBSP( spaceID )
		spaceBSP.getChild( "isLeaf" ).set( "True" )
		time.sleep( 2 )

	def getCellAppID( self, position, spaceID = None ):
		"""
		If spaceID is None, we must only have one space...
		"""
		spaceBSP = self.__getSpaceBSP( spaceID )
		return self.__getCellAppIDRecurse( position, spaceBSP )

	def __getCellAppIDRecurse( self, position, BSPNode ):
		if BSPNode.getChild( "isLeaf" ).value:
			return BSPNode.getChild( "app" ).getChild( "id" ).value
		if BSPNode.getChild( "isHorizontal" ).value:
			posVal = position[ 2 ]
		else:
			posVal = position[ 0 ]
		splitPos = BSPNode.getChild( "position" ).value
		if posVal < splitPos:
			return self.__getCellAppIDRecurse( position, BSPNode.getChild( "left" ) )
		else:
			return self.__getCellAppIDRecurse( position, BSPNode.getChild( "right" ) )

