import time

def aoiCheck( witnessPos, entityPos, range, appealRadius = 0):
	"""
	Return True if the entity position will be in witnessPos's AoI
	"""
	return abs( witnessPos[ 0 ] - entityPos[ 0 ] ) <= range + appealRadius and \
		abs( witnessPos[ 2 ] - entityPos[ 2 ] ) <= range + appealRadius


def spawnBotWitness( cc, position, cellLayout, spaceID = None ):
	"""
	spaceID = None means "In a new space"
	Returns ( botID, spaceID )
	"""

	cc.bots.add( 1 )
	# TODO: Get new Bot ID from this somehow?
	# Delay to ensure bot has logged in
	time.sleep( 2 )

	entityID = cc.callOnApp( "baseapp", 1, "giveCellToAvatar",
							 spaceID = spaceID, position = position )

	cc.callOnApp( "bots", snippetName = "waitForBotToEnterWorld", 
				entityID = entityID )
	time.sleep( 1 )
	botCheckPosition( cc, entityID, position )
	realSpaceID = validateEntityPosition( cc, entityID, position, cellLayout, spaceID )
	if spaceID is not None:
		assert spaceID == realSpaceID, "Bot found in wrong space"
	return ( entityID, realSpaceID )


def spawnEntity( cc, entityType, position, cellLayout, spaceID = None ):
	entityID = cc.callOnApp( "baseapp", 1, "createEntity",
							spaceID = spaceID, entityType = entityType,
							position = position )
	time.sleep(0.2)
	realSpaceID = validateEntityPosition( cc, entityID, position, cellLayout, spaceID )
	if spaceID is not None:
		assert spaceID == realSpaceID, "Entity found in wrong space"
	return ( entityID, realSpaceID )


def verifyExistsInBotsAoI( cc, botEntityID, otherEntityID, expected = True ):
	cc.callOnApp( "bots", snippetName = "verifyExistOnBot",
				expected = expected, botEntityID = botEntityID,
				otherEntityID = otherEntityID )


def validateEntityPosition( cc, entityID, position, cellLayout, spaceID = None ):
	"""
	Confirms that an entity is at the given position, and returns
	its spaceID.
	"""
	cellAppID = cellLayout.getCellAppID( position, spaceID )
	return cc.callOnApp( "cellapp", cellAppID, "validateEntitySpacePosition",
						entityID = entityID, position = position )


def entityMoveToPoint( cc, entityID, oldPosition, position, acceleration, maxSpeed, cellLayout, spaceID = None ):
	"""
	Moves an entity to a position and returns the controller id
	"""
	cellAppID = cellLayout.getCellAppID( oldPosition, spaceID )
	return cc.callOnApp( "cellapp", cellAppID, "entityMoveToPosition",
						entityID = entityID, position = position,
						acceleration = acceleration, maxSpeed = maxSpeed)

def botMove( cc, entityID, position ):
	"""
	Moves a bot to a position
	"""
	cc.callOnApp( "bots", snippetName = "positionBot", entityID = entityID,
				position = position )


def botCheckPosition( cc, entityID, position ):
	"""
	Checks that a bot is in the given position
	"""
	cc.callOnApp( "bots", snippetName = "checkBotPosition", 
				entityID = entityID, position = position )


def entityMoveImmediately( cc, entityID, oldPosition, position, cellLayout, spaceID = None ):
	"""
	Moves a Cell entity to a position
	"""
	cellAppID = cellLayout.getCellAppID( oldPosition, spaceID )
	return cc.callOnApp( "cellapp", cellAppID, "entityMoveImmediately",
						entityID = entityID, oldPosition = oldPosition,
						position = position )


def entityDestroy( cc, entityID, oldPosition, cellLayout, spaceID = None ):
	"""
	Destroy a Cell entity
	"""
	cellAppID = cellLayout.getCellAppID( oldPosition, spaceID )
	return cc.callOnApp( "cellapp", cellAppID, "entityDestroy",
						entityID = entityID, oldPosition = oldPosition )

