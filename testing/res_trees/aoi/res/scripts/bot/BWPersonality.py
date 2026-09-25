# Bot bootstrap script

import BigWorld
import srvtest

__waitingForBotToEnterWorld = None
def waitForBotToEnterWorld( botID ):
	global __waitingForBotToEnterWorld
	srvtest.assertEqual( None, __waitingForBotToEnterWorld )
	__waitingForBotToEnterWorld = botID

__waitingForBotToHaveEntities = None
def waitForBotToHaveEntities( botID ):
	global __waitingForBotToHaveEntities
	srvtest.assertEqual( None, __waitingForBotToHaveEntities )
	__waitingForBotToHaveEntities = botID

def onClientAppDestroy( botID ):
	global __waitingForBotToEnterWorld
	if botID == __waitingForBotToEnterWorld:
		__waitingForBotToEnterWorld = None
		srvtest.fail( "Bot was destroyed before entering world" )
		srvtest.finish()

	global __waitingForBotToHaveEntities
	if botID == __waitingForBotToHaveEntities :
		__waitingForBotToHaveEntities  = None
		srvtest.fail( "Bot was destroyed before witnessing entities" )
		srvtest.finish()

def onTick():
	global __waitingForBotToEnterWorld
	if __waitingForBotToEnterWorld is not None:
		if not BigWorld.bots.has_key( __waitingForBotToEnterWorld ):
			__waitingForBotToEnterWorld = None
			srvtest.fail( "Bot was destroyed before entering world" )
			srvtest.finish()
		elif BigWorld.bots[ __waitingForBotToEnterWorld ].spaceID != 0:
			__waitingForBotToEnterWorld = None
			srvtest.finish()

	global __waitingForBotToHaveEntities
	if __waitingForBotToHaveEntities  is not None:
		if not BigWorld.bots.has_key( __waitingForBotToHaveEntities  ):
			__waitingForBotToHaveEntities  = None
			srvtest.fail( "Bot was destroyed before witnessing entities" )
			srvtest.finish()
		elif len(BigWorld.bots[ __waitingForBotToHaveEntities  ].entities) > 1:
			__waitingForBotToHaveEntities  = None
			srvtest.finish()

# BWPersonality.py
