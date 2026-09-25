import bwtest
from helpers.cluster import ClusterController

# We know these from WorldEditor
HEIGHT_AT_ORIGIN = 19.59
HOLE_X = -90
HOLE_Z = 70

# BaseTerrainBlock::NO_TERRAIN in lib/terrain/base_terrain_block.cpp
HEIGHT_AT_HOLE = -1000000


class TerrainTest( bwtest.TestCase ):
	name = "Terrain Test"
	description = "Test bots terrain"
	tags = []


	def setUp( self ):
		self.cc = ClusterController( "simple_space/res" )
		self.addCleanup( self.cc.clean )
		self.cc.start()
		self.addCleanup( self.cc.stop )
		self.cc.startProc( "bots", 1 )


	def tearDown( self ):
		self.cc.stop()
		self.cc.clean()


	def step1( self ):
		"""Test BigWorld.addSpaceGeometryMapping"""

		# Load the space geometry and check callback results
		snippet = """
		def onMappingLoaded( spaceID, name ): srvtest.finish( (spaceID, name ) )
		import BWPersonality
		BWPersonality.onSpaceGeometryLoaded = onMappingLoaded
		BigWorld.addSpaceGeometryMapping( 1, None, "spaces/main" )
		"""
		spaceID, name = self.cc.sendAndCallOnApp( "bots", snippet = snippet )
		self.assertEqual( spaceID, 1 )
		self.assertEqual( name, "main" )


	def step2( self ):
		"""Test BigWorld.getHeightAtPos"""

		# Check height on the hill
		snippet = """
		from Math import Vector3
		point = Vector3( 0, 0, 0 )
		height = BigWorld.getHeightAtPos( 1, point )
		srvtest.finish( height )
		"""
		height = self.cc.sendAndCallOnApp( "bots", snippet = snippet )
		height = round( height, 2 )
		self.assertEqual( height, HEIGHT_AT_ORIGIN )

		# Check height in hole
		snippet = """
		from Math import Vector3
		point = Vector3( %s, 0, %s )
		height = BigWorld.getHeightAtPos( 1, point )
		srvtest.finish( height )
		""" % (HOLE_X, HOLE_Z)
		height = self.cc.sendAndCallOnApp( "bots", snippet = snippet )
		self.assertEqual( height, HEIGHT_AT_HOLE )


	def step3( self ):
		"""Test positive BigWorld.collide"""

		# Do collision check starting from above and finishing below
		snippet = """
		from Math import Vector3
		src = Vector3( 0, -%s, 0 )
		dst = Vector3( 0, %s+1, 0 )
		result = BigWorld.collide( 1, src, dst )
		srvtest.finish( result )
		""" % (HEIGHT_AT_ORIGIN, HEIGHT_AT_ORIGIN)
		hit, tri, mat = self.cc.sendAndCallOnApp( "bots", snippet = snippet )

		# Hit is Vector3
		self.assertEqual( hit[0], 0 )
		self.assertEqual( round( hit[1], 2 ), HEIGHT_AT_ORIGIN )
		self.assertEqual( hit[2], 0 )

		# Tri is 3 Vector3 verts
		self.assertTrue( len( tri ), 3 )
		self.assertTrue( len( tri[0] ), 3 )
		self.assertTrue( len( tri[1] ), 3 )
		self.assertTrue( len( tri[2] ), 3 )


	def step4( self ):
		"""Test negative BigWorld.collide"""

		# Do collision check starting from above and finishing still above
		snippet = """
		from Math import Vector3
		src = Vector3( 0, -%s*2, 0 )
		dst = Vector3( 0, -%s, 0 )
		result = BigWorld.collide( 1, src, dst )
		srvtest.finish( result )
		""" % (HEIGHT_AT_ORIGIN, HEIGHT_AT_ORIGIN)
		result = self.cc.sendAndCallOnApp( "bots", snippet = snippet )

		self.assertFalse( result )

		# Do collision check in the hole
		snippet = """
		from Math import Vector3
		src = Vector3( %s, -%s, %s )
		dst = Vector3( %s, %s+1, %s )
		print src
		print dst
		result = BigWorld.collide( 1, src, dst )
		srvtest.finish( result )
		""" % (HOLE_X, HEIGHT_AT_ORIGIN, HOLE_Z, HOLE_X,  HEIGHT_AT_ORIGIN,
			HOLE_Z)
		result = self.cc.sendAndCallOnApp( "bots", snippet = snippet )

		self.assertFalse( result )
