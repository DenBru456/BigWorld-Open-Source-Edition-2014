# Cell bootstrap script

import BigWorld
import srvtest



def onInit( isReload ):
	pass


def onCellAppReady( isFromDB ):
	pass


gFirstSpaceID = 0
gSpaceIDHook = None

def onSpaceData( spaceID, entryID, key, value ):
	print "[bwtest] onSpaceData: ", spaceID, key
	#if 0 <= key and key <= 255:
	#	return

	global gFirstSpaceID
	global gSpaceIDHook

	gFirstSpaceID = spaceID
	if gSpaceIDHook is not None:	
		print "[bwtest] onSpaceData: called the hook! "
		gSpaceIDHook( spaceID )


def hookOnSpaceID( callback ):
	global gSpaceIDHook
	gSpaceIDHook = callback


def getSpaceID():
	global gFirstSpaceID
	return gFirstSpaceID

# BWPersonality.py
