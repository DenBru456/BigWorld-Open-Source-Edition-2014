"""
Module implementing the XMPPEventNotifier entity type.

The XMPPEventNotifier is a singleton global entity that use XMPP/Jabber
to broadcasts event notifications and respond to BaseApp watcher queries. 

In the example below, all XMPP clients (FantasyDemo clients, Pidgin,
Gajim, etc) that have the XMPPEventNotifier on their roster will recieve
the message "Player ID 1000 is cheating!":

XMPPEventNotifier.broadcast( u"Player ID 1000 is cheating!" )

To query a watcher value, send a messge in the format "getWatcher
<watcherPath>".

Example:
bigcorp.cto@gmail.com: getWatcher config/numBases
server_of_bigworld@eval.bigworldtech.com: 100
"""

import BigWorld

import XMPPRoster
import xmpp.Connection as XMPPConnection

import os
import pwd

g_user = "server_of_" + pwd.getpwuid( os.getuid() )[0]
g_passwd = g_user


def broadcast( message ):
	if BigWorld.globalBases.has_key( 'XMPPEventNotifier' ):
		notifier = BigWorld.globalBases[ 'XMPPEventNotifier' ]
		notifier.broadcast( unicode( message ) )


BROADCAST_TIMER = 15	# Send a status message every 15 minutes
#BROADCAST_TIMER = 1	# Send a status message every minute


# ------------------------------------------------------------------------------
# Section: class XMPPEventNotifier
# ------------------------------------------------------------------------------

class XMPPEventNotifier( BigWorld.Base ):

	def __init__( self ):
		BigWorld.Base.__init__( self )

		self.registerGlobally( "XMPPEventNotifier", self.onRegisterGlobally )

		self.roster = XMPPRoster.XMPPRoster()

		self.xmppConnection = None


	def onRegisterGlobally( self, success ):
		if success:
			self.xmppConnection = XMPPConnection.Connection( self )
			self.xmppConnection.connect( g_user, g_passwd )

			# Convert minutes to seconds for addTimer
			broadcastPeriod = BROADCAST_TIMER * 60
			self.addTimer( broadcastPeriod, broadcastPeriod )

		else:
			self.destroy()


	def onDestroy( self ):
		# Ensure that the XMPP connection has been destroyed so we don't leave
		# a lingering socket open.
		if self.xmppConnection:
			self.xmppConnection.disconnect()
			self.xmppConnection = None


	def onRestore( self ):
		# The roster must be re-created as we are re-establishing the XMPP
		# connection.
		self.roster = XMPPRoster.XMPPRoster()
		self.xmppConnection = None

		self.xmppConnection = XMPPConnection.Connection( self )
		self.xmppConnection.connect( g_user, g_passwd )


	def onTimer( self, id, userArg ):
		self.broadcast( u"Load: %s entities %s players" %
				(BigWorld.getWatcher( "numBases" ),
				 BigWorld.getWatcher( "numProxies" ) ) )


	def cleanup( self ):
		self.broadcast( u"Server is shutting down" )

		self.xmppConnection.disconnect()
		self.xmppConnection = None

		self.deregisterGlobally( "XMPPEventNotifier" )
		self.destroy()


	def broadcast( self, message ):
		friendsDict = self.roster.friendsByStatus()

		# Combine any friends that aren't offline into the online group
		onlineFriends = []
		for presence in friendsDict.keys():
			if presence == "unavailable":
				continue

			onlineFriends.extend( friendsDict[ presence ] )

		# If there is nobody to talk to, stay as silent as possible
		if not len( onlineFriends ):
			return

		print( "XMPPEventNotifier: "
				"Broadcasting periodic status to %s friends: %s" %
					(len( onlineFriends ), message) )

		# The event notifier currently only supports XMPP friend notification.
		# To change this will require adding a new method to the XMPPRoster
		# to allow returning the friendID,transport along with the presence.
		transport = "xmpp"
		for friendID in onlineFriends:
			self.xmppConnection.friendMessage( friendID, transport, message )


	def onXmppPresence( self, sender, isOnline ):
		if isOnline and BigWorld.time() < 30.0:
			self.xmppConnection.friendMessage( sender, "Server is online" )


	# ---------------------------------------------------------------------
	# Section: xmpp.Connection.ConnectionHandler Methods
	# ---------------------------------------------------------------------

	def onXmppConnectionStateChange( self, newState, oldState ):

		if newState == XMPPConnection.STATE_ONLINE and \
			oldState != XMPPConnection.STATE_ONLINE:

# TODO: remove this print
			print "XMPPEventNotifier: Online!"
			self.xmppConnection.requestRoster()


	def onXmppConnectionError( self, message ):
		print "XMPPEventNotifier::ERROR:", message


	def onXmppConnectionMessage( self, friendID, transport, message ):
		"Respond to 'getWatcher <watcherPath>' message with the watcher value."

		print "XMPPEventNotifier: '%s' [%s] requested '%s'" % \
			(friendID, transport, message)

		# Now reply to the message from our friend
		if message.lower().startswith( "getwatcher" ):
			path = message.split( " ", 1 )[1].strip()
			try:
				result = BigWorld.getWatcher( path )

			except:
				result = "Watcher path not found"

			self.xmppConnection.friendMessage( friendID, transport, result )

		else:
			self.xmppConnection.friendMessage( friendID, transport,
												"Unknown command" )


	def onXmppConnectionRoster( self, roster ):
		self.roster.update( roster )


	def onXmppConnectionRosterItemAdd( self, friendID, transport ):
		self.roster.add( friendID, transport )


	def onXmppConnectionRosterItemDelete( self, friendID, transport ):
		self.roster.remove( friendID, transport )


	def onXmppConnectionPresence( self, friendID, transport, presence ):

		# We only want to process the general friend notifications.
		generalFriendID = friendID.split( "/", 1 )[0]

		if presence == "subscribe":
			# Request being made to become a friend of us

			# Auto-authorise any requests for the time being
			self.xmppConnection.friendAuthorise( friendID, transport )

			# We will add this user as our friend now.
			# We don't have to add them to our list again.
			if self.roster.isFriend( generalFriendID, transport ):
				return

			# They have subscribed to us, so lets ask them to be our friend too.
			self.xmppConnection.friendAdd( generalFriendID, transport )

		elif presence == "unsubscribe":
			# Auto-remove anybody from our own roster if they have removed us
			self.xmppConnection.friendDelete( generalFriendID, transport )

		elif presence == "subscribed":
			pass

		elif presence == "unsubscribed":
			pass

		else:
			# Update our XMPPRoster
			self.roster.updatePresence( generalFriendID, transport, presence )


		return


# -------------------------------------------------------------------------
# Section: Init and destroy singleton
# -------------------------------------------------------------------------

def wakeupXMPPEventNotifier():
	if not BigWorld.globalBases.has_key( "XMPPEventNotifier" ):
		BigWorld.createBaseAnywhere( "XMPPEventNotifier" )


def destroyXMPPEventNotifier():
	if BigWorld.globalBases.has_key( "XMPPEventNotifier" ):
		notifier = BigWorld.globalBases[ "XMPPEventNotifier" ]
		if BigWorld.entities.has_key( notifier.id ):
			notifier.cleanup()

# XMPPEventNotifier.py
