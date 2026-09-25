# Base bootstrap script

import BigWorld
import Watchers
import srvtest

wasOnBaseAppDataCalled = False

def onInit( isReload ):
	pass


def onBaseAppData( key, value ):
	global wasOnBaseAppDataCalled
	wasOnBaseAppDataCalled = True


def onBaseAppReady( isBootstrap, didAutoLoadEntitiesFromDB ):
	# Only on the first baseapp
	if isBootstrap:
		# Create a Space entity that will create a space with our geometry.
		BigWorld.createBaseLocally( "Space", spaceDir = "spaces/main" )


# BWPersonality.py
