# Base bootstrap script

import BigWorld
import srvtest


def onInit( isReload ):
	pass


def onBaseAppReady( isBootstrap, didAutoLoadEntitiesFromDB ):
	# Only on the first baseapp
	if isBootstrap:
		# Create a Space entity that will create a space with our geometry.
		BigWorld.createBaseLocally( "Space", spaceDir = "spaces/main" )


# BWPersonality.py
