# Common Door functionality shared between client and cell

from GameData import DoorData

def getOpeningDirection( testPosition, doorPosition, doorDirection ):
	n = doorDirection
	isInFront = n.dot( testPosition ) > n.dot( doorPosition )
	if isInFront:
		return DoorData.STATE_OPEN_OUTWARD
	else:
		return DoorData.STATE_OPEN_INWARD
