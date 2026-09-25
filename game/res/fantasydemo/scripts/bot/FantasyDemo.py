import BigWorld

dormantBots = []
curTick = 0

def onClientAppDestroy( playerID ):
	print "onClientAppDestroy called on id: ", playerID
	#BigWorld.bots[playerID].entities[playerID].base.logOff()


def onBotsReady():
	print "onBotsReady called"

def onLoseConnection( playerID ):
	global dormantBots
	print "bot client %d lost connection with server" % playerID
	print "put it in the dormant list for reactivation later"
	dormantBots.append( BigWorld.bots[playerID] )
	return False #don't destroy the bot client

def onTick():
	global curTick, dormantBots
	curTick = curTick + 1
	#check roughly every 3 seconds and bring one dormant bot online
	if curTick % 30 == 0 and len(dormantBots) > 0: 
		i = dormantBots[0]
		print "bring bot %s online" % i.loginName
		i.logOn()
		dormantBots = dormantBots[1:]
		curTick = 0


def onSpaceDataCreated( playerID, spaceID, key, data ):
	print "onSpaceDataCreate( %d ): spaceID %d, key %d added data: %s" % ( playerID, spaceID, key, data )


def onSpaceDataDeleted( playerID, spaceID, key, data ):
	print "onSpaceDataDeleted( %d ): spaceID %d, key %d deleted data: %s" % ( playerID, spaceID, key, data )
