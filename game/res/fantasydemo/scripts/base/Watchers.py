import BigWorld
import util
import traceback
from bwdecorators import functionWatcher, functionWatcherParameter

import XMPPEventNotifier


# Add Guards
# -----------------------------------------------------------------------------
@functionWatcher( "command/addGuards",
		BigWorld.EXPOSE_LEAST_LOADED,
		"Add an arbitrary number of patrolling guards into the world." )
@functionWatcherParameter( int, "Number of guards to add" )
def addGuardReturnMessage( numGuards ):
	try:
		type = util.addGuards( numGuards )
		return "Added %s guards of type '%s'." % ( numGuards, type )
	except:
		traceback.print_exc()
		return "Failed to add guards."


# Remove Guards
# -----------------------------------------------------------------------------
@functionWatcher( "command/removeGuards",
		BigWorld.EXPOSE_LEAST_LOADED,
		"Remove an arbitrary number of patrolling guards from the world." )
@functionWatcherParameter( int, "Number of guards to remove" )
def delGuardReturnMessage( numGuards ):
	try:
		count = util.removeGuards( numGuards )
		return "Removed %s guards." % count
	except:
		traceback.print_exc()
		return "Failed to remove guards."


# System Message
# -----------------------------------------------------------------------------
@functionWatcher( "command/systemMessage",
		BigWorld.EXPOSE_BASE_APPS,
		"Send a global system message to all clients." )
@functionWatcherParameter( str, "Message to send" )
def sendSystemMessage( msg ):
	resultMsg = ""
	try:
		resultMsg = "Message sent to %s clients." % util.systemMessage( msg )

	except:
		resultMsg = "Failed to send system message."

	return resultMsg


@functionWatcher( "command/xmppBroadcast",
		BigWorld.EXPOSE_BASE_APPS,
		"Broadcast an XMPP message" )
@functionWatcherParameter( str, "Message to broadcast" )
def xmppBroadcast( msg ):
	if not BigWorld.globalBases.has_key( "XMPPEventNotifier" ):
		return "No XMPPEventNotifier"

	notifier = BigWorld.globalBases[ "XMPPEventNotifier" ]
	if not BigWorld.entities.has_key( notifier.id ):
		return "No local XMPPEventNotifier"

	if type( msg ) is str:
		msg = msg.decode( "utf8" )
	notifier.broadcast( msg )
	return "Message sent"


# Watchers.py
