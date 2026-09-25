# Base bootstrap script

import BigWorld
import Watchers
import srvtest

global wasOnBaseAppDataCalled
wasOnBaseAppDataCalled = False

def onInit( isReload ):
	pass


def onBaseAppData( key, value ):
	print BigWorld.baseAppData[ key ]
	print value
	print BigWorld.baseAppData[ key ] == value
	global wasOnBaseAppDataCalled
	wasOnBaseAppDataCalled = True


# BWPersonality.py
