# Base bootstrap script

import BigWorld
import unit_tests


def onInit( isReload ):
	pass


def onBaseAppReady( isBootstrap, didAutoLoadEntitiesFromDB ):
	# Only on the first baseapp
	if isBootstrap:
		# Create a Space entity that will create a space with our geometry.
		BigWorld.createBaseLocally( "Space", spaceDir = "spaces/main" )

	unit_tests.runTests()

# BWPersonality.py
