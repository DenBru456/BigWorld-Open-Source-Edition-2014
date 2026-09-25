import math
import ItemBase

# --------------------------------------------------------------------------
# This module contains all the data that describes the various creature
# types.  It is used by the client, server and tools.
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Every type of entity has a group of sub-types. The creature entity for
# example, may have striffs, young striffs, and dune striders as sub-types.
# A sub-type for a creature is meant to be enough to define its game
# mechanics. The variable storing the sub-type of the entity is named by
# its class name followed by 'Type'.
#
# The UNKNOWN type value means that the creature type has not been sent
# by the server. It means that the server will change the type later as
# more information is allowed to the client.
# --------------------------------------------------------------------------
UNKNOWN			= 0
STRIFF			= 1
STRIFF_YOUNG	= 2
CHICKEN			= 3
SPIDER			= 4
CRAB			= 5
RAT				= 6


# --------------------------------------------------------------------------
# Each entity has a state variable that is comprised of their name followed
# by the identfier, 'State'. The creatureState variable can take the
# following legal values.
#
# The ALLOWED_STATE should always be set to the last value allowed by the
# creature state.
# --------------------------------------------------------------------------
DEAD			= 0
DEAD_GIBBED		= 1
ALIVE			= 2
HIDDEN			= 3
ALLOWED_STATE	= 3


# --------------------------------------------------------------------------
# Each creature entity has actions (specified by an actionID) that it can
# perform. This value is used by the server to tell the creature to perform
# certain actions. The IDLE actionID is the default action.
#
# The ALLOWED_ACTION should always be set to the last value allowed by the
# actionID.
# --------------------------------------------------------------------------
IDLE			= 0			# Stand around, do nothing in general.
GRAZE			= 1			# Peck at ground.
STRETCH			= 2			# Shake, wiggle, or stretch limbs.
DIE_KILLED		= 3			# Fall to the ground, dead.
DIE_GIBBED		= 4			# Explode into gory chunks.
EMIT_SOUND		= 5			# Emits a random creature sound.
HIDE			= 6			# Play a hide sequence, go into HIDDEN mode
REVEAL			= 7			# Reveals oneself from HIDDEN
ALLOWED_ACTION	= 7


# --------------------------------------------------------------------------
# Each creature entity has a list of actions (specified by actionIDs) that
# it can perform.  If the entry does not exist, the creature ignores the
# request.
# --------------------------------------------------------------------------
allowedActions = {
	UNKNOWN			: (),
	STRIFF			: (IDLE, GRAZE, STRETCH, DIE_KILLED, DIE_GIBBED),
	STRIFF_YOUNG	: (IDLE, GRAZE, STRETCH, DIE_KILLED, DIE_GIBBED),
	CHICKEN			: (IDLE, GRAZE, STRETCH, DIE_KILLED),
	SPIDER			: (IDLE, DIE_KILLED, HIDE, REVEAL),
	CRAB			: (IDLE, DIE_KILLED),
	RAT				: (IDLE, DIE_KILLED),
}


# --------------------------------------------------------------------------
# Creatures that can hide/reveal themselves have sfx for this activity.
# --------------------------------------------------------------------------
hideFX = {	
	SPIDER			: ("sfx/spider_hide.xml", "sfx/spider_hide.xml")
}


# --------------------------------------------------------------------------
# Creatures have hit fx (hit by fireball, arrow, whatever)
# --------------------------------------------------------------------------
hitFX = {
	STRIFF			: "sfx/striff_explosion.xml",
	STRIFF_YOUNG	: "sfx/striff_explosion.xml",
	CHICKEN			: "sfx/chicken_explosion.xml",
	SPIDER			: "sfx/spider_explosion.xml",
	CRAB			: "sfx/spider_explosion.xml",
	RAT				: "sfx/rat_explosion.xml",
}


# --------------------------------------------------------------------------
# With the exception of the UNKNOWN type, every type of creature has a
# corresponding model type. The index to this dictionary is stored in the
# variable creatureType. Creatures with no model defined should still have
# an entry in this dictionary, albeit with the value 'None'.
# --------------------------------------------------------------------------
modelNames = {
	UNKNOWN:			None,
	STRIFF:				"characters/npc/fd_striff/striff.model",
	STRIFF_YOUNG:		"characters/npc/fd_striff/striff.model",
	CHICKEN:			"characters/npc/chicken/chicken.model",
	SPIDER:				"characters/npc/spider/spider.model",
	CRAB:				"characters/npc/crab/crab.model",
	RAT:				"characters/npc/rat/models/rat.model",
}


# --------------------------------------------------------------------------
# Not every type of entity can be destroyed in a spectacular fashion. Those
# that can, however, use an additional model when dying in such a manner.
# The index to this dictionary is stored in the variable creatureType.
# Creatures without a 'gibbed' death should still have an entry in this
# dictionary, albeit with the value 'None'.
# --------------------------------------------------------------------------
gibbedModelNames = {
	UNKNOWN:			None,
	STRIFF:				"characters/npc/striff/striff_gib.model",
	STRIFF_YOUNG:		"characters/npc/striff/striff_gib.model",
	CHICKEN:			"characters/npc/striff/striff_gib.model",
	SPIDER:				None,	
	CRAB:				None,	
	RAT:				None,
}


# --------------------------------------------------------------------------
# Occasionally creatures drop body parts when killed.  These are dropped
# items the player can pick up and add to their inventory.
#
# tuple is (item number, amount to spawn)
# --------------------------------------------------------------------------
bodyPartsItem = {
	UNKNOWN:			(None, None),
	STRIFF:				(ItemBase.ItemBase.DRUMSTICK_TYPE, 2),
	STRIFF_YOUNG:		(ItemBase.ItemBase.DRUMSTICK_TYPE, 1),
	CHICKEN:			(None, None),
	SPIDER:				(ItemBase.ItemBase.SPIDER_LEG_TYPE, 1),
	CRAB:				(None, None),
	RAT:				(None, None),
}


# --------------------------------------------------------------------------
# The displayNames list contains the displayable names for the sub-types
# of entities. Every type of creature entity has to have a display name.
# It is safe to check for a valid creature type by looking for it in this
# dictionary. That is, if the type is found, the creature has a valid type.
# --------------------------------------------------------------------------
displayNames = {
	UNKNOWN:			"Unidentified Creature",
	STRIFF:				"Striff",
	STRIFF_YOUNG:		"Young Striff",
	CHICKEN:			"Chicken",
	SPIDER:				"Spider",
	CRAB:				"Crab",
	RAT:				"Rat",
}




# --------------------------------------------------------------------------
# The randomSounds list contains the identifier for a category of random
# sounds emitted by creatures as well as a minimum and maximum random time
# delay between noises. If no value, None is found, the creature will not
# make any random noises. The time delay value is in seconds.
# 	e.g. ( "creatures/striff_young/grunt", 2, 8 )
# --------------------------------------------------------------------------
randomSounds = {
	UNKNOWN:			None,
	STRIFF:				None,
	STRIFF_YOUNG:		None,
	CHICKEN:			None,
	SPIDER:				None,
	CRAB:				None,	
	RAT:				None,
}


# --------------------------------------------------------------------------
# The runSpeed is a tuple of (minSpeed, maxSpeed) used for when creatures
# start barneying around.
# --------------------------------------------------------------------------
runSpeed = {
	UNKNOWN:		(0.5, 7.5),
	STRIFF:			(0.5, 7.5),
	STRIFF_YOUNG:	(0.5, 7.5),
	CHICKEN:		(0.7, 1.5),
	SPIDER:			(0.5, 7.5),
	CRAB:			(0.2, 0.5),
	RAT:			(0.5, 7.5),
}


# --------------------------------------------------------------------------
# The healthTable is a tuple of (initialHealth, maxHealth) used for when creatures
# spawn in the world.
# --------------------------------------------------------------------------
healthTable = {
	UNKNOWN:		(100, 100),
	STRIFF:			(100, 100),
	STRIFF_YOUNG:	( 50,  50),
	CHICKEN:		( 25,  25),
	SPIDER:			(100, 100),
	CRAB:			( 25,  25),
	RAT:			( 25,  25),
}


# --------------------------------------------------------------------------
# Whether or not this creature aligns to the ground its on, or is always
# upright
# --------------------------------------------------------------------------
alignToGround = {
	UNKNOWN:		False,
	STRIFF:			False,
	STRIFF_YOUNG:	False,
	CHICKEN:		False,
	SPIDER:			True,
	CRAB:			True,
	RAT:			True,
}


# --------------------------------------------------------------------------
# The collideWithPlayersWhenAlive table shows what collision options should
# be used when creature is alive
# usage:
# am.entityCollision = collideWithPlayersWhenAlive[ self.creatureType ][0]
# am.collisionRooted = collideWithPlayersWhenAlive[ self.creatureType ][1]
# --------------------------------------------------------------------------
collideWithPlayersWhenAlive = {
	UNKNOWN:		(False, False),
	STRIFF:			(True, True),
	STRIFF_YOUNG:	(True, True),
	CHICKEN:		(False, False),
	SPIDER:			(True, True),
	CRAB:			(False, False),
	RAT:			(False, False),
}


# --------------------------------------------------------------------------
# The collideWithPlayersWhenDead table shows what collision options should
# be used when creature is dead
# usage:
# am.entityCollision = collideWithPlayersWhenDead[ self.creatureType ][0]
# am.collisionRooted = collideWithPlayersWhenDead[ self.creatureType ][1]
# --------------------------------------------------------------------------
collideWithPlayersWhenDead = {
	UNKNOWN:		(False, False),
	STRIFF:			(False, True),
	STRIFF_YOUNG:	(False, True),
	CHICKEN:		(False, False),
	SPIDER:			(False, True),
	CRAB:			(False, False),
	RAT:			(False, True),
}

FLEE_TURN_DISTANCE = 1.5
FLEE_RUN_DISTANCE  = 10
FLEE_SCARED_FACTOR = 2.0
MAX_YAW_DELTA = (math.pi / 32)
CHASE_STOP_RANGE = 4.0
CHASE_OWNER_RANGE = 6.0
FLEE_RANGE = 20.0
ATTENTION_RANGE = 25.0
FORGET_OWNER_RANGE = 100.0