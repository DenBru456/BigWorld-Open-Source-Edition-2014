import BigWorld
import srvtest
import BWPersonality

@srvtest.testSnippet
def waitForBotToEnterWorld( entityID ):
	BWPersonality.waitForBotToEnterWorld( entityID )
	# srvtest.finish() will be triggered when the Bot has a spaceID
	
@srvtest.testSnippet
def verifyExistOnBot( expected, botEntityID, otherEntityID):
	if expected:
		test = srvtest.assertTrue
		failure = "Entity not in AoI"
	else:
		test = srvtest.assertFalse
		failure = "Entity unexpectedly in AoI"
	srvtest.assertTrue( BigWorld.bots.has_key( botEntityID ) )
	test( BigWorld.bots[botEntityID ].entities.has_key( otherEntityID ), failure )
	srvtest.finish()
	
@srvtest.testSnippet
def positionBot( entityID, position ):
	srvtest.assertTrue( BigWorld.bots.has_key( entityID ), "Entity not found" )
	clientApp = BigWorld.bots[ entityID ]
	srvtest.assertNotEqual( 0, clientApp.spaceID, "Bot is not in a space" )
	
	clientApp.position = position
	
	clientAppPos = ( clientApp.position.x, clientApp.position.y, clientApp.position.z )
	srvtest.assertEqual( position, clientAppPos, "Bot is out of position" )
	srvtest.finish()

@srvtest.testSnippet	
def checkBotPosition( entityID, position ):
	srvtest.assertTrue( BigWorld.bots.has_key( entityID ), "Entity not found" )
	clientApp = BigWorld.bots[ entityID ]
	srvtest.assertNotEqual( 0, clientApp.spaceID, "Bot is not in a space" )
	clientAppPos = ( clientApp.position.x, clientApp.position.y, clientApp.position.z )
	srvtest.assertEqual( position, clientAppPos, "Bot is out of position" )
	srvtest.finish()
