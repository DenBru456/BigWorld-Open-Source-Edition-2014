from cell_layout import CellLayout

import aoi_helper
from helpers.cluster import ClusterController

import time

class AoITestCase( object ):
	"""
	This mixin manages spawning and moving Entities in a space
	so that they fufill whichever AoI conditions are required by
	the test.
	It provides some methods which can be used directly as steps in
	an automated test case.
	The subclass must also inherit from TestCase
	"""
	def __init__( self, entityAppealRadius = 0, witnessAppealRadius = 0, singleCell = True ):
		# Test Configuration
		self.__aoiRadius = 500
		self.__appealRadius = entityAppealRadius
		self.__witnessAppealRadius = witnessAppealRadius
		self.__singleCell = singleCell
		self.__botPosition = ( 0, 0, 0 )
		self.__witnessType = "Avatar"
		self.__entityType = "Other"

		# Current test status
		self.__spaceID = None
		self.__witnessID = None
		self.__inAoIIDs = []
		self.__inAppealIDs = []
		self.__outOfAoIIDs = []

		self.__entityRotation = 0
		self.__inAoIShift = 0
		self.__inAoIDistance = self.__aoiRadius / 2
		if self.__appealRadius > 0:
			self.__inAppealShift = 1
			self.__inAppealDistance = self.__aoiRadius + ( self.__appealRadius / 2 )
			self.__outOfAoIShift = 2
		else:
			self.__outOfAoIShift = 1
		self.__outOfAoIDistance = self.__aoiRadius + self.__appealRadius + 500


	def __validateStartPositions( self ):
		# Validate our starting positions.
		for pos in self.__inAoIPositions():
			self.assertTrue( aoi_helper.aoiCheck( self.__botPosition, pos, self.__aoiRadius, 0 ), "inAoI position outside AoI" )
		for pos in self.__inAppealPositions():
			self.assertFalse( aoi_helper.aoiCheck( self.__botPosition, pos, self.__aoiRadius, 0 ), "inAppeal position in AoI" )
			self.assertTrue( aoi_helper.aoiCheck( self.__botPosition, pos, self.__aoiRadius, self.__appealRadius ), "inAppeal position outside AoI" )
		for pos in self.__outOfAoIPositions():
			self.assertFalse( aoi_helper.aoiCheck( self.__botPosition, pos, self.__aoiRadius, 0 ), "outOfAoI position in AoI" )
			self.assertFalse( aoi_helper.aoiCheck( self.__botPosition, pos, self.__aoiRadius, self.__appealRadius ), "outOfAoI position in appeal radius" )


	def __cardinalPosition( self, distance, slot ):
		"""
		Get the position at distance from origin given cardinal slot:
        247
        1 6
		035
		"""
		self.assertTrue( slot >= 0 and slot < 8 )
		if slot == 0:
			return ( -distance, 0, -distance )
		elif slot == 1:
			return ( -distance, 0, 0 )
		elif slot == 2:
			return ( -distance, 0, distance )
		elif slot == 3:
			return ( 0, 0, -distance )
		elif slot == 4:
			return ( 0, 0, distance )
		elif slot == 5:
			return ( distance, 0, -distance )
		elif slot == 6:
			return ( distance, 0, 0 )
		elif slot == 7:
			return ( distance, 0, distance )


	def __currentPosition( self, shift, slot ):
		"""
		Determine the position of the given slot at the given shift
		"""
		self.assertTrue( shift >= 0 )
		if self.__appealRadius > 0:
			self.assertTrue( shift < 3 )
		else:
			self.assertTrue( shift < 2 )

		if shift == 0:
			return self.__cardinalPosition( self.__inAoIDistance, slot )
		elif shift == 1 and self.__appealRadius > 0:
			return self.__cardinalPosition( self.__inAppealDistance, slot )
		else:
			return self.__cardinalPosition( self.__outOfAoIDistance, slot )


	def __inAoIPositions( self ):
		"""
		The list of eight positions of the entities that spawned in AoI
		"""
		self.assertTrue( self.__entityRotation >=0 and self.__entityRotation < 8 )
		return [ self.__currentPosition( self.__inAoIShift,
			( x + self.__entityRotation ) % 8 ) for x in range( 8 ) ]


	def __inAppealPositions( self ):
		"""
		The list of eight positions of the entities that spawned in Appeal Radius
		or an empty list if we have no Appeal Radius
		"""
		self.assertTrue( self.__entityRotation >=0 and self.__entityRotation < 8 )
		if self.__appealRadius == 0:
			return []
		return [ self.__currentPosition( self.__inAppealShift,
			( x + self.__entityRotation ) % 8 ) for x in range( 8 ) ]


	def __outOfAoIPositions( self ):
		"""
		The list of eight positions of the entities that spawned out of AoI
		"""
		self.assertTrue( self.__entityRotation >=0 and self.__entityRotation < 8 )
		return [ self.__currentPosition( self.__outOfAoIShift,
			( x + self.__entityRotation ) % 8 ) for x in range( 8 ) ]


	def __verifyPositionsOnBot( self, destroyed = False ):
		"""
		Check that the bot is seeing things that are in AoI and not things
		that are out of AoI
		"""
		# TODO: Verify positions, not just visibility
		if self.__witnessID is None:
			return
		time.sleep( 2 )

		if self.__appealRadius > 0:
			outOfAoIShiftValue = 2
		else:
			outOfAoIShiftValue = 1

		for entityID in self.__inAoIIDs:
			expected = self.__inAoIShift < outOfAoIShiftValue and not destroyed
			aoi_helper.verifyExistsInBotsAoI( self.__cc, self.__witnessID, entityID, expected = expected )

		for entityID in self.__inAppealIDs:
			expected = self.__inAppealShift < outOfAoIShiftValue and not destroyed
			aoi_helper.verifyExistsInBotsAoI( self.__cc, self.__witnessID, entityID, expected = expected )

		for entityID in self.__outOfAoIIDs:
			expected = self.__outOfAoIShift < outOfAoIShiftValue and not destroyed
			aoi_helper.verifyExistsInBotsAoI( self.__cc, self.__witnessID, entityID, expected = expected )


	def __setCellLayout( self ):
		"""
		Arrange our Cell Layout after creating a space.
		"""
		self.assertTrue( self.__spaceID is not None, "Cannot setup cells until we have a space" )
		if self.__singleCell:
			self.__layout.clearLayout()
			test = self.assertEqual
		else:
			self.__layout.setLayout()
			test = self.assertNotEqual

		botAppID = self.__layout.getCellAppID( self.__botPosition, self.__spaceID )

		for pos in self.__inAoIPositions() + self.__inAppealPositions() + self.__outOfAoIPositions():
			test( self.__layout.getCellAppID( pos, self.__spaceID ), botAppID )


	def tearDown( self ):
		"""
		Clean up any left over server state
		Called even if self.setUp() failed.
		"""
		self.__cc.stop()
		self.__cc.cleanSecondaryDBs()
		self.__cc.clean()


	def __setAppealRadius( self, entityType, appealRadius ):
		def setAppealRadiusLineEditor( line ):
			if line.strip() == "<root>":
				line = "%s\t<AppealRadius> %d </AppealRadius>\n" % ( line, appealRadius )
			elif "AppealRadius" in line:
				line = "\n"
			return line

		return self.__cc.lineEditResTreeFile( "scripts/entity_defs/%s.def" % ( entityType, ), setAppealRadiusLineEditor )


	### Everything below here is available to be used as a step in the test cases. ###

	def setUp( self ):
		"""
		Get our server cluster ready
		"""
		self.__validateStartPositions()
		self.__cc = ClusterController( "aoi/res" )
		self.__cc.setConfig( "cellApp/defaultAoIRadius", str( self.__aoiRadius ) )
		self.assertTrue( self.__setAppealRadius( self.__entityType, self.__appealRadius ), "Failed to set AppealRadius for %s" % ( self.__entityType, ) )
		self.assertTrue( self.__setAppealRadius( self.__witnessType, self.__witnessAppealRadius ), "Failed to set AppealRadius for %s" % ( self.__witnessType, ) )
		self.__cc.start()
		self.__cc.startProc( "bots", 1, 0 )
		if not self.__singleCell:
			# Multi-cell tests need five cellapps.
			self.__cc.startProc( "cellapp", 4, 0 )
		self.assertTrue( self.__cc.waitForServerSettle() )
		
		self.__cc.loadSnippetModule( "baseapp", 1, "aoi/test_aoi_baseapp")
		self.__cc.loadSnippetModule( "bots", path = "aoi/test_aoi_bots")
		numCellApps = 1 + 4*(not self.__singleCell)
		for i in range(numCellApps):
			self.__cc.loadSnippetModule( "cellapp", i+1, "aoi/test_aoi_cellapp")
		
		self.__layout = CellLayout( self.__cc )


	def spawnWitness( self ):
		"""
		Spawn a witness into the world.
		"""
		newSpace = self.__spaceID is None

		self.assertTrue( self.__witnessID is None, "Witness already spawned" )

		botID, spaceID = aoi_helper.spawnBotWitness( self.__cc, self.__botPosition, self.__layout, self.__spaceID )
		if self.__spaceID is None:
			self.__spaceID = spaceID
		else:
			self.assertEqual( self.__spaceID, spaceID, "Witness spawned into wrong space" )
		self.__witnessID = botID

		if newSpace:
			self.__setCellLayout()
		else:
			self.__verifyPositionsOnBot()


	def spawnEntities( self ):
		"""
		Spawn our full set of entities into the world.
		"""
		newSpace = self.__spaceID is None

		for pos in self.__inAoIPositions():
			entityID, spaceID = aoi_helper.spawnEntity( self.__cc, self.__entityType, pos, self.__layout, self.__spaceID )
			if self.__spaceID is None:
				self.__spaceID = spaceID
			else:
				self.assertEqual( self.__spaceID, spaceID, "Entity spawned into wrong space" )
			self.__inAoIIDs.append( entityID )

		for pos in self.__inAppealPositions():
			entityID, spaceID = aoi_helper.spawnEntity( self.__cc, self.__entityType, pos, self.__layout, self.__spaceID )
			if self.__spaceID is None:
				self.__spaceID = spaceID
			else:
				self.assertEqual( self.__spaceID, spaceID, "Entity spawned into wrong space" )
			self.__inAppealIDs.append( entityID )

		for pos in self.__outOfAoIPositions():
			entityID, spaceID = aoi_helper.spawnEntity( self.__cc, self.__entityType, pos, self.__layout, self.__spaceID )
			if self.__spaceID is None:
				self.__spaceID = spaceID
			else:
				self.assertEqual( self.__spaceID, spaceID, "Entity spawned into wrong space" )
			self.__outOfAoIIDs.append( entityID )

		if newSpace:
			self.__setCellLayout()
		else:
			self.__verifyPositionsOnBot()


	def moveEntities( self, inAoI = 0, inAppealRadius = 0, outOfAoI = 0, rotate = 0 ):
		"""
		Move entities around.
		All entities move outwards according to the parameters:
		Levels are inAoI, inAppealRadius (if appealRadius > 0), outOfAoI
		We also rotate through the positions as a ring, wrapping the array.
		This takes effect from the current positions, so the result is the
		sum of this and all previous moveEntities calls.
		"""
		oldInAoIPositions = self.__inAoIPositions()
		oldInAppealPositions = self.__inAppealPositions()
		oldOutOfAoIPositions = self.__outOfAoIPositions()
		self.__entityRotation = ( self.__entityRotation + rotate ) % 8
		if self.__appealRadius == 0:
			shiftMod = 2
			self.assertEqual( inAppealRadius, 0 )
		else:
			shiftMod = 3
			self.__inAppealShift = ( self.__inAppealShift + inAppealRadius ) % shiftMod
		self.__inAoIShift = ( self.__inAoIShift + inAoI ) % shiftMod
		self.__outOfAoIShift = ( self.__outOfAoIShift + outOfAoI ) % shiftMod

		for entityID, oldPos, pos in zip( self.__inAoIIDs, oldInAoIPositions, self.__inAoIPositions() ):
			aoi_helper.entityMoveImmediately( self.__cc, entityID, oldPos, pos, self.__layout, self.__spaceID )

		for entityID, oldPos, pos in zip( self.__inAppealIDs, oldInAppealPositions, self.__inAppealPositions() ):
			aoi_helper.entityMoveImmediately( self.__cc, entityID, oldPos, pos, self.__layout, self.__spaceID )

		for entityID, oldPos, pos in zip( self.__outOfAoIIDs, oldOutOfAoIPositions, self.__outOfAoIPositions() ):
			aoi_helper.entityMoveImmediately( self.__cc, entityID, oldPos, pos, self.__layout, self.__spaceID )


	def destroyEntities( self ):
		"""
		Destroy all our spawned entities.
		"""
		for entityID, pos in zip( self.__inAoIIDs, self.__inAoIPositions() ):
			aoi_helper.entityDestroy( self.__cc, entityID, pos, self.__layout, self.__spaceID )

		for entityID, pos in zip( self.__inAppealIDs, self.__inAppealPositions() ):
			aoi_helper.entityDestroy( self.__cc, entityID, pos, self.__layout, self.__spaceID )

		for entityID, pos in zip( self.__outOfAoIIDs, self.__outOfAoIPositions() ):
			aoi_helper.entityDestroy( self.__cc, entityID, pos, self.__layout, self.__spaceID )

		# Check that entities are gone, no matter where they were.
		self.__verifyPositionsOnBot( destroyed = True )

		self.__inAoIIDs = []
		self.__inAppealIDs = []
		self.__outOfAoIIDs = []

		if self.__witnessID is None:
			self.__spaceID = None
