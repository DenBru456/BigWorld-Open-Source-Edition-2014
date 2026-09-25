# Base bootstrap script

import BigWorld


def onInit( isReload ):
	pass


def onAppReady( isBootstrap, didAutoLoadEntitiesFromDB ):
	# Only called on the first BaseApp process to startup
	if isBootstrap:
		# Create a Space entity that will create a space with our geometry.
		BigWorld.createBaseLocally( "Space", spaceDir = "spaces/main" )

# BWPersonality.py
