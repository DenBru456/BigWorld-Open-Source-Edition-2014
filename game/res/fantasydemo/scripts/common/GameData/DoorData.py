# This module contains constant data associated with the Door entity type.

# Notes about expected door action names:
#
# For doors to open inward and outward based on where the opener is,
# the following actions must exist:
#
# * DoorOpeningInward
# * DoorOpeningOutward
# * DoorOpenInward
# * DoorOpenOutward
# * DoorClosingInward
# * DoorClosingOutward
# * DoorClosed
#
# Otherwise, for doors that only ever open in one direction must have
# the following actions:
#
# * DoorOpening
# * DoorOpen
# * DoorClosing
# * DoorClosed
#

TOWER_DOOR		= 0
MINSPEC_DOOR	= 1

displayNames = {
	TOWER_DOOR:		"Door",
	MINSPEC_DOOR:	"Door",
}

editorDisplayNames = {
	TOWER_DOOR:		"Tower Door",
	MINSPEC_DOOR:	"Minspec Door",
}

modelNames = {
	TOWER_DOOR:		"sets/temperate/props/tower_door/model/tower_door.model",
	MINSPEC_DOOR:	"sets/minspec/props/house/models/door.model"
}

STATE_CLOSED 		= 0
STATE_OPEN_INWARD	= 1
STATE_OPEN_OUTWARD	= 2
