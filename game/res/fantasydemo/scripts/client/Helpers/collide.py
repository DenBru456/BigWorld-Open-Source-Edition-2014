# -----------------------------------------------------------------------------
# file: collide
# Description:
#	- ???
# -----------------------------------------------------------------------------

import BigWorld
import Math
import math


[ COLLIDE_ENTITY,
	COLLIDE_TERRAIN,
	COLLIDE_NONE,
	COLLIDE_OTHER ] = range(4)

def collide( x, y ):
	player = BigWorld.player()
	if player is None:
		return COLLIDE_OTHER, None

	entity = BigWorld.target()
	if entity and entity != player:
		#make sure this is exact hit. This is needed especially for arcade machines (web) to make collide more exact.
		if hasattr( entity, "intersectMouseCoordinates" ):
			locationX, locationY  = entity.intersectMouseCoordinates( x, y )
			if locationX != -1 or locationY != -1:
				return COLLIDE_ENTITY, entity
		else:
			return COLLIDE_ENTITY, entity

	spaceID = player.spaceID
	src, dst = getMouseTargettingRay( )
	terrain = BigWorld.collide( spaceID, src, dst )
	if terrain:
		return COLLIDE_TERRAIN, terrain[0]
	else:
		return COLLIDE_NONE, dst

def cameraCollide( x, y ):
	'''
	Do a collide form the camera.
	'''
	camera = BigWorld.camera()
	if camera is None:
		return COLLIDE_OTHER, None

	entity = BigWorld.target()
	if entity is not None:
		# Make sure this is exact hit.
		# This is needed especially for arcade machines (web) to make
		# collide more exact.
		if hasattr( entity, "intersectMouseCoordinates" ):
			locationX, locationY  = entity.intersectMouseCoordinates( x, y )
			if locationX != -1 or locationY != -1:
				return COLLIDE_ENTITY, entity
		else:
			return COLLIDE_ENTITY, entity

	spaceID = camera.spaceID
	src, dst = getMouseTargettingRay()
	if spaceID != 0:
		terrain = BigWorld.collide( spaceID, src, dst )
		if terrain:
			return COLLIDE_TERRAIN, terrain[0]
	return COLLIDE_NONE, dst

def getMouseTargettingRay():
	mtm = Math.Matrix( BigWorld.MouseTargettingMatrix() )
	src = mtm.applyToOrigin()
	far = BigWorld.projection().farPlane
	dst = src + mtm.applyToAxis(2).scale( far )
	return src, dst
