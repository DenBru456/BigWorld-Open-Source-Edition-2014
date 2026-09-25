"This module implements some utility methods."

import BigWorld
import random
import math
import LightGuardPatrolRoutes
import TeleportPoint

# Currently unused
#def offset(radius):
#	return random.randrange(-radius/2, radius/2)

def offset2(radius):
	angle = random.random()*6.28
	c = math.cos(angle)
	s = math.sin(angle)
	r = random.random()*radius/2.0 + radius/2.0
	return (r*c,r*s)

GUARD_TYPE = "LightGuard"
# GUARD_TYPE = "Guard"

def addGuards( count ):
	if GUARD_TYPE == "LightGuard":
		patrollingLightGuards( count )
	elif GUARD_TYPE == "Guard":
		spawnGuards( count )
	else:
		print "util.addGuards: Unknown GUARD_TYPE: %s" % GUARD_TYPE
	return GUARD_TYPE

def removeGuards( count ):
	if GUARD_TYPE == "LightGuard":
		return removeLightGuards( count )
	elif GUARD_TYPE == "Guard":
		return despawnGuards( count )
	else:
		print "util.addGuards: Unknown GUARD_TYPE: %s" % GUARD_TYPE
		return 0

### LightGuard Code ###

def patrollingLightGuards( count, modelNumber = 0):
	for i in range(count):
		# We know that LightGuards start at node index 0
		pathIndex = LightGuardPatrolRoutes.randomList()
		nodeIndex = random.randrange(
						len( LightGuardPatrolRoutes.patrolPath( pathIndex ) ) )
		startLoc = LightGuardPatrolRoutes.patrolNode( pathIndex, nodeIndex )

		# TODO: Make this createBaseAnywhere. The removal currently assumes
		# that they are local.
		BigWorld.createBaseLocally( "LightGuard",
				modelNumber = modelNumber,
				patrolListIndex = pathIndex,
				patrolNode = nodeIndex,
				position = startLoc,
				direction = ( 0,0,0 ),
				createOnCell = TeleportPoint.find( "fantasy" ).cell )

def removeLightGuards( count ):
	removed = 0
	allGuards = [ e for e in BigWorld.entities.values() \
				if e.className == "LightGuard" ]
	allGuardsCount = len( allGuards )

	if count > allGuardsCount:
		print "Request for removal of %d %s's cannot be satisified, only " \
			"%d exist. Removing all." % ( count, "LightGuard",
				allGuardsCount )

	for entity in allGuards:
		if hasattr( entity, "cell" ):
			entity.destroyCellEntity()
		else:
			entity.destroy()
		removed += 1
		if removed == count:
			break

	return removed

### End LightGuard Code ###

# Sends a message to entity[id] or all entities
# if no id specified.
# Returns: number of entities a message was sent to. 
def systemMessage( msg, id = None ):
	count = 0
	if id:
		entity = BigWorld.entities[id]
		if hasattr( entity, "messageToClient" ):
			entity.messageToClient( msg )
			count = 1
	else:
		for i in BigWorld.entities.values():
			if hasattr( i, "messageToClient" ):
				i.messageToClient( msg )
				count += 1

	return count

def entitiesOfType( t ):
	return [e for e in BigWorld.entities.values() if e.className == t]

# util.py
