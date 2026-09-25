# Bootstrap script for cell

import BigWorld
import srvtest

def onInit( isReload ):
	pass

def onAppReady( isFromDB ):
	pass

#this implementation is to help the test know when a space is done loading.
#Simplistic and will probably need to be changed with mutiple cells and spaces
numSpacesFullyLoaded = 0
def getNumSpacesFullyLoaded():
	global numSpacesFullyLoaded
	return numSpacesFullyLoaded

BigWorld.addWatcher( "numSpacesFullyLoaded", getNumSpacesFullyLoaded )

def onAllSpaceGeometryLoaded( spaceId, isBootStrap, lastPath ):
	global numSpacesFullyLoaded
	print "Space fully loaded %s" % spaceId
	numSpacesFullyLoaded += 1
