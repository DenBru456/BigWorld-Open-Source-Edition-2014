"This module centralises the fixed patrol routes used by the LightGuard"

import math
import Math
import random

# ------------------------------------------------------------------------------
# Patrol Lists
# ------------------------------------------------------------------------------

# Module initialisation stuff

PATROL_LISTS = []

def circ(path):
	q = path[:]
	q.reverse()
	path += q

def initPatrolLists():
	global PATROL_LISTS
	# These two paths are disabled to keep LightGuards away from
	# the populated areas, to avoid confusion between these and Guards
#	path_new = [(61,-3,7,3),
#		(138,-22,13,3),
#		(134,-22,10,3),
#		(155,-24,2,2),
#		(229,-18,12,2),
#		(269,-19,13,2),
#		(292,-17,-6,2),
#		(208,-10,-28,2),
#		(405,-6,-28,3),
#		(443,-21,-34,2),
#		(462,-44,-5,2),
#		(545,-105,28,3),
#		(591,-112,1,2),
#		(612,-104,-33,3),
#		(705,-107,-64,15),
#		(731,-113,-206,10),
#		(941,-118,-265,50)
#	]
#	circ(path_new)

#	path_alt = [
#		(52,-3,6,2),
#		(86,-16,13,2),
#		(174,-27,3,2),
#		(177,-44,51,5),
#		(162,-43,80,2),
#		(132,-24,135,2),
#		(125,-42,187,2),
#		(109,-20,240,2),
#		(129,-7,310,2),
#		(97,9,333,2),
#		(-150,0,8,50)
#	]
#	circ(path_alt)

	path_north = [
		(-312, 0,  994, 250),
		( 800, 0,  750, 250),
		( -44, 0, 1254, 250),
		( 853, 0, 1237, 250)
	]

	PATROL_LISTS = \
		[#path_new, path_alt, path_north, path_north, path_north,
		path_north]

initPatrolLists()

# Private utility code

def offset2(radius):
	"""
	Pick a random 2D offset in the outer half of a given radius
	"""
	angle = random.random()*2.0*math.pi
	c = math.cos(angle)
	s = math.sin(angle)
	r = math.sqrt( random.random() )*radius
	return (r*c,r*s)

# Actual Module Interface

def randomList():
	"""
	Select a random listIndex
	"""
	return random.randrange( 0, len( PATROL_LISTS ) )

def validListIndex( listIndex ):
	"""
	Verify that the given listIndex is a valid list
	"""
	if listIndex >= len( PATROL_LISTS ) or listIndex < 0:
		return False
	return True

def nextNodeIndex( listIndex, nodeIndex ):
	"""
	Returns the next nodeIndex after the current one
	"""
	return ( nodeIndex + 1 ) % len( PATROL_LISTS[ listIndex ] )

def patrolPath( listIndex ):
	return PATROL_LISTS[ listIndex ]

def patrolNode( listIndex, nodeIndex ):
	"""
	Returns the randomised position of the requested patrol Node
	"""
	point = PATROL_LISTS[ listIndex ][ nodeIndex ][ 0:3 ]
	xyOffset = offset2( PATROL_LISTS[ listIndex ][ nodeIndex ][ 3 ] )

	return Math.Vector3( point[ 0 ] + xyOffset[ 0 ], point[ 1 ],
		point[ 2 ] + xyOffset[ 1 ] )

