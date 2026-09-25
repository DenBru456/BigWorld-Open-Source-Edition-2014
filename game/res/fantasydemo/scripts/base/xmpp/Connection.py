# Known issues:
# - Adding an in game contact from MSN does not show up as being online. This
#   is most likely a problem with the Gateway as no stanzas appear to be
#   received which would prompt a presence update
# - Adding an MSN friend (external client) to an in-game MSN account (internal)
#   will not cause an 'online' presence update to be sent to the internal client
#   account. 

"""XMPP Connection module.

This Connection interface for XMPP (specifically the Ejabber implementation)
has been implemented based on the spefications documented at:

XMPP Core:
 http://xmpp.org/rfcs/rfc3920.html

XMPP Instant Messaging and Presence:
 http://xmpp.org/rfcs/rfc3921.html

XMPP extension - Service Discovery:
 http://xmpp.org/extensions/xep-0030.html
"""

import base64
import hashlib
import logging
import random
import re
import socket

import BigWorld

import Parser as XMPPParser
import Service as XMPPService
import Stanzas

log = logging.getLogger( "XMPP" )

# Incoming buffer size to use when reading from server
RECV_BUFFER_SIZE = 2048


# Connection states
STATE_OFFLINE        = 0 # No active connection
STATE_CONNECT_TCP    = 1 # Establishing TCP socket connection
STATE_REGISTERING    = 2 
STATE_CONNECT_XMPP   = 3 # Performing XMPP connection initialisation
STATE_AUTHENTICATING = 4 # Providing authentication credentials to XMPP server
STATE_ONLINE         = 5 # Online and ready to communicate


class ConnectionHandler( object ):

	def onXmppConnectionStateChange( self, oldState, newState ):
		pass

	def onXmppConnectionError( self, msg ):
		pass

	def onXmppConnectionMessage( self, friendID, transport, msg ):
		pass

	def onXmppConnectionPresence( self, friendID, transport, presence ):
		pass

	def onXmppConnectionRoster( self, roster ):
		pass

	def onXmppConnectionRosterItemAdd( self, friendID, transport ):
		pass

	def onXmppConnectionRosterItemDelete( self, friendID, transport ):
		pass

	def onXmppConnectionTransportAccountRegistered( self, transport,
			username, password ):
		pass

	def onXmppConnectionTransportAccountDeregistered( self, transport ):
		pass


# ----------------------------------------------------------------------
# Section: class Connection
# ----------------------------------------------------------------------

# Refer to http://xmpp.org/rfcs/rfc3921.html
class Connection( object ):

	def __init__( self, connectionHandler ):

		self.connectionHandler = connectionHandler

		self.jid = None
		self.username = None
		self.password = None
		self.resource = None

		self.resolvedHost = None
		self.hostname = None
		self.port     = None

		self.socket = None
		self.parser = None

		self.state = STATE_OFFLINE

		self.stanzaIDs    = {}
		self.nextStanzaID = 0

		self.transports = {}


	def updateState( self, newState ):
		oldState = self.state
		self.state = newState
		self.connectionHandler.onXmppConnectionStateChange( newState, oldState )


	def sendStanza( self, stanza ):
		self.socket.send( stanza )


	def connect( self, username, password, resource = "BigWorld" ):

		# Currently only stored in case we will support reconnection
		self.username = username
		self.password = password
		self.resource = resource

		return self.doConnect()


	# This method performs the actual connection to the Ejabber server.
	def doConnect( self ):
		if not self.username or not self.password:
			log.error( "XMPPConnection: Unable to connect, "
					"no username / password provided." )
			return False

		if self.socket:
			log.error( "XMPPConnection: Unable to connect, "
					"an existing connection exists." )
			return False

		deferredXMPPDetails = XMPPService.details()

		def detailsCallback( (hostname, resolvedHost, port) ):

			self.hostname = hostname
			self.resolvedHost = resolvedHost
			self.port = port

			# User and host in JIDs are case insensitive, use lower for easier
			# comparison
			self.jid = self.username.lower() + "@" + self.hostname.lower() + \
							"/" + self.resource
			self.parser = XMPPParser.XMPPParser()



			# Create the socket for communicating with the XMPP server.
			# TODO: if we remain in STATE_CONNECT_TCP state for too long, we should
			#       fall over.
			self.updateState( STATE_CONNECT_TCP )
			self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.socket.setblocking( False )
			connectionStatus = self.socket.connect_ex(
										(self.resolvedHost, int( self.port )) )

			# Now register the socket with the write file descriptor so we can
			# establish an XMPP connection once the socket is ready for writes.
			BigWorld.registerWriteFileDescriptor(
							self.socket, self.onWriteFileDescriptorAvailable )

		deferredXMPPDetails.addCallback( detailsCallback )

		return True


	# This callback method is invoked in response to
	# BigWorld.registerWriteFileDescriptor
	def onWriteFileDescriptorAvailable( self, socket ):

		# No need to be informed when ready to write again
		BigWorld.deregisterWriteFileDescriptor( self.socket )

		# Now that the socket has been connected, we can safely establish
		# the XMPP connection.
		self.updateState( STATE_CONNECT_XMPP )
		BigWorld.registerFileDescriptor( self.socket, self.onXmppRecvData )
		self.sendStanza(
			"<?xml version='1.0'?>" + Stanzas.STREAM_START % self.hostname )


	def disconnect( self ):
		if not self.socket:
			log.notice( "XMPPConnection: Unable to disconnect, "
					"not currently connected." )
			return False

		if self.state == STATE_CONNECT_TCP:
			BigWorld.deregisterWriteFileDescriptor( self.socket )
		else:
			BigWorld.deregisterFileDescriptor( self.socket )

			self.sendStanza( Stanzas.STREAM_END )

		# Now reset everything that was used
		self.connectionHandler = None

		self.jid = None
		self.username = None
		self.password = None
		self.resource = None

		self.resolvedHost = None
		self.hostname = None
		self.port     = None

		self.socket = None
		if self.parser:
			self.parser.fini()
		self.parser = None

		self.state = STATE_OFFLINE

		self.nextStanzaID = 0
		self.stanzaIDs    = {}

		self.transports = {}

		return True


	# TODO: This should ideally be implemented, but is heavily dependant on
	#       how well the transport gateways respect the XMPP RFCs. Currently
	#       PyMSNt doesn't do a great job, so we can't rely on this for
	#       notification of it coming online.
	def isTransportSupported( self, transport ):

		return True
		#return (self.transports.has_key( transport ) and
		#		self.transports[ transport ] == "available")


	def isTransportDomain( self, jid ):
		return bool( re.match( "\w+\.%s" % self.hostname, jid ) )


	def getTransportFromJID( self, jid ):
		m = re.match( "(\w+)\.%s" % self.hostname, jid )
		if not m:
			return None

		return m.group( 1 ).encode( "utf8" )


	def friendAdd( self, friendID, transport ):

		if self.state != STATE_ONLINE:
			self.connectionHandler.onXmppConnectionError(
								"XMPP connection not online" )
			return False

		if not self.isTransportSupported( transport ):
			self.connectionHandler.onXmppConnectionError(
								"Transport not supported" )
			return False

		# Create a unique ID to identify this removal request with
		stanzaID = self.generateNewID( "roster" )

		self.stanzaIDs[ stanzaID ] = (friendID, transport)

		# Create the JID for our friend
		friendJID = self.xmppCreateJIDWithTransport( friendID, transport )

		# Send the message
		self.sendStanza( Stanzas.rosterAdd( stanzaID, self.jid, friendJID ) )


	# This public method authorises a friend request.
	def friendAuthorise( self, friendID, transport ):
		friendJID = self.xmppCreateJIDWithTransport( friendID, transport )
		self.sendStanza( Stanzas.SUBSCRIBE_ALLOW % (self.jid, friendJID) )


	def friendDelete( self, friendID, transport ):

		if self.state != STATE_ONLINE:
			self.connectionHandler.onXmppConnectionError(
								"XMPP connection not online" )
			return False

		# NB: not enforcing self.isTransportSupported( transport ) here as
		#     it may be possible that a roster item has been inserted for
		#     a transport that we are unable to connect to again and would
		#     like to delete the roster item.

		# Create a unique ID to identify this removal request with
		stanzaID = self.generateNewID( "remove" )

		self.stanzaIDs[ stanzaID ] = (friendID, transport)

		# Send the message
		friendJID = self.xmppCreateJIDWithTransport( friendID, transport )

		self.sendStanza( Stanzas.rosterDel( stanzaID, friendJID ) )

		return True


	def friendMessage( self, friendID, transport, msg ):

		if self.state != STATE_ONLINE:
			self.connectionHandler.onXmppConnectionError(
								"XMPP connection not online" )
			return False

		if not self.isTransportSupported( transport ):
			self.connectionHandler.onXmppConnectionError(
						"Transport '%s' is not online or not supported." %
							transport )
			return False

		friendJID = self.xmppCreateJIDWithTransport( friendID, transport )
		self.sendStanza( Stanzas.MESSAGE % (self.jid, friendJID, msg) )

		return True


	def requestRoster( self ):

		if self.state != STATE_ONLINE:
			self.connectionHandler.onXmppConnectionError(
								"XMPP connection not online" )
			return False

		# Create a unique ID to identify this removal request with
		stanzaID = self.generateNewID( "request_roster" )

		# We don't need to store anything in particular here, so just
		# push in a note about where we were called from.
		self.stanzaIDs[ stanzaID ] = "requestRoster"

		self.sendStanza( Stanzas.queryRoster( stanzaID, self.jid ) )


	# TODO: document this extension somewhere
	# http://xmpp.org/extensions/xep-0100.html
	# This method associates a third-party IM account on the specified
	# transport type with the current connection.
	def transportAccountRegister( self, transport, username, password ):

		if self.state != STATE_ONLINE:
			self.connectionHandler.onXmppConnectionError(
								"XMPP connection not online" )
			return False

		# Can't validate the transport is online here as the transport will
		# not become visible until we provide valid credentials.

		# Create a unique ID to identify this removal request with
		stanzaID = self.generateNewID( "legacy_reg" )

		self.stanzaIDs[ stanzaID ] = (transport, username, password)

		# Send the message
		transportDomain = self.xmppCreateDomainFromTransport( transport )

		self.sendStanza(
				Stanzas.gatewayRegister( stanzaID, self.jid, transportDomain,
											username, password ) )
		return True


	def transportAccountDeregister( self, transport ):

		if self.state != STATE_ONLINE:
			self.connectionHandler.onXmppConnectionError(
								"XMPP connection not online" )
			return False

		# Create a unique ID to identify this removal request with
		stanzaID = self.generateNewID( "legacy_dereg" )

		self.stanzaIDs[ stanzaID ] = transport

		# Send the message
		transportDomain = self.xmppCreateDomainFromTransport( transport )

		self.sendStanza(
				Stanzas.gatewayDeregister( stanzaID, self.jid,
											transportDomain ) )

		return True


	# ----------------------------------------------------------------------
	# Section: Private Helper Methods
	# ----------------------------------------------------------------------

	# This method creates the domain associated with a transport type. While
	# the current implementation is trivial, it may be modified if necessary 
	# to support transports with more complex domain structures.
	def xmppCreateDomainFromTransport( self, transport ):
		return "%s.%s" % (transport.lower(), self.hostname)


	def xmppCreateJIDWithTransport( self, friendID, transport ):
		if transport != "xmpp":
			friendJID = "%s@%s.%s" % ( friendID.replace( "@", "%" ),
										transport, self.hostname )

		else:
			friendJID = friendID

		return friendJID


	def xmppConvertJIDToFriendID( self, jid ):
		transport = "xmpp"

		# NB: chould potentially also strip off resource names here
		match = re.match( "(.*)@(\w+)\.%s" % self.hostname, jid )
		if match:
			# Unmangle any transport specific munging
			friendID = match.group( 1 ).replace( "%", "@" )
			transport = match.group( 2 ).lower()

		else:
			friendID = jid

		# All the XMPP interfaces expect the friendID to be a Unicode string
		if isinstance( friendID, str ):
			friendID = friendID.decode( "utf8" )

		return (friendID, transport)


	# ----------------------------------------------------------------------
	# Section: XMPP Server Stanza Handling Methods
	# ----------------------------------------------------------------------


	def onStateAuthenticating( self, stanza ):
		stanzaName = stanza[ 'name' ]

		stanzaID = getAttr( stanza, 'id' )
		stanzaType = getAttr( stanza, 'type' )

		if stanzaName == 'challenge':
			self.onStanzaAuthChallenge( stanza )

		elif stanzaName == 'success':
			# open new stream to server
			self.parser.newParser()
			self.sendStanza( Stanzas.STREAM_START % self.hostname )

		elif stanzaName == 'stream:features':
			self.sendStanza( Stanzas.BIND_RESOURCE % self.resource )

		elif stanzaName == "iq":

			if stanzaType == 'result':
				if stanzaID == 'bind_2':
					# log resource name bound to
					self.sendStanza( Stanzas.SESSION )
	
				elif stanzaID == 'sess_1':
					# Logon process complete
					self.updateState( STATE_ONLINE )
	
					# Notify all subscribed parties of our presence
					self.sendStanza( Stanzas.presence() )

		elif stanzaName == 'failure':
			self.updateState( STATE_REGISTERING )
			self.sendStanza( Stanzas.REGISTRATION_IQ )

		else:
			log.warning( "Unhandled stanza name: %s", stanzaName )
			log.warning( "%s", stanza )
	


	# ----------------------------------------------------------------------
	# Section: Private Event Methods
	# ----------------------------------------------------------------------


	def onXmppRecvData( self, socket ):

		# TODO: This is checking Bigworld.Base.isDestroyed(), need to find
		#       another way to do this.
		# TODO: Confirm this works as with Dom's commit check.
#		if self.isDestroyed:
#			BigWorld.deregisterFileDescriptor( self.socket )
#			return

		if not self.parser:
			log.warning( "Connection.onXmppRecvData: No parser available." )
			return

		data = self.socket.recv( RECV_BUFFER_SIZE )
		if not data:
			log.warning( "Connection::onXmppRecvData: Disconnecting from "
					"XMPP server, no data available." )
			self.disconnect()
			return

		self.parser.feedData( data )
		stanza = self.parser.pop()

		while stanza:
			#print "\n\n====== RECV DATA: STANZA ====="
			self.handleStanza( stanza )

			try:
				stanza = self.parser.pop()
			except:
				stanza = None


	#@stanzaHandler( STATE_AUTHENTICATING, "success" )
	#def onSuccess( self, stanza ):
	#			# open new stream to server
	#			self.parser.newParser()
	#			self.sendStanza( Stanzas.STREAM_START % self.hostname )


	def handleStanza( self, stanza ):

		stanzaName = stanza[ 'name' ]

		tmpID = getAttr( stanza, 'id' )
		tmpType = getAttr( stanza, 'type' )

		#print "  Stanza: %s [%s] [%s] \t(%s)" % \
		#		( stanzaName, tmpID, tmpType, stateToString( self.state ) )

		# STATE: Connecting
		if self.state == STATE_CONNECT_XMPP:
			if stanzaName == 'stream:features':
				# TODO: why is this not using updateState?
				self.state = STATE_AUTHENTICATING
				self.sendStanza( Stanzas.AUTHENTICATION_START )


		# STATE: Authenticating
		elif self.state == STATE_AUTHENTICATING:
			self.onStateAuthenticating( stanza )


		# STATE: Registering
		elif self.state == STATE_REGISTERING:
			if stanzaName == 'iq' and getAttr( stanza, 'type' ) == 'result':
				if getAttr( stanza, 'id' ) == 'reg1':
					# Lets just assume only username and password are required
					self.sendStanza( Stanzas.REGISTRATION % \
										( self.username, self.password ) )

				elif getAttr( stanza, 'id' ) == 'reg2':
					self.updateState( STATE_AUTHENTICATING )
					self.sendStanza( Stanzas.AUTHENTICATION_START )

			elif stanzaName == 'iq' and getAttr( stanza, 'type' ) == 'error' \
				and getAttr( stanza, 'id' ) == 'reg2':

				log.error( "Connection::handleStanza: An error was "
						"encountered while registering. Disconnecting." )
				self.disconnect()


		# STATE: Online
		elif self.state == STATE_ONLINE:
			if stanzaName == 'message':
				self.onStanzaMessage( stanza )
	
			elif stanzaName == 'presence':
				self.onStanzaPresence( stanza )
	
			elif stanzaName == 'iq':
				self.onStanzaInfoQuery( stanza )


		else:
			### error, unknown state
			log.error( "Connection::handleStanza: Unknown state!" )
			pass


	#--------------------------
	# Stanza ID tracking
	#--------------------------

	# TODO: this ID generation would be nicer if it was in Stanzas.py
	def generateNewID( self, prefix ):
		stanzaID = "%s_%s_%s" % (prefix, id( self ), self.nextStanzaID)
		self.nextStanzaID += 1
		return stanzaID


	#--------------------------
	# Stanza Event Management
	#--------------------------

	def onIQStanza_RosterItemAdd( self, stanza ):
		# This can occur from a /addFriend initiated addition where the remote
		# side (eg: Pidgin) hasn't added us to their list yet.

		# NB: This may already have happened from an 'subscribed' presence
		#     on a Pidgin initiated removal.

		stanzaID = getAttr( stanza, "id" )
		stanzaType = getAttr( stanza, "type" )

		# Check that this is an addition we know about
		if not self.stanzaIDs.has_key( stanzaID ):
			log.warning( "Unknown roster addition message received: %s",
				stanzaID )
			return False

		# Remove the ID from our known ids
		(friendID, transport) = self.stanzaIDs.pop( stanzaID )

		# Now handle success or failure
		if stanzaType == "result":
			# Now notify the client.
			# This does not need to be performed here, as XMPP relies on
			# a presence message indicating 'subscribed' to handle this
			# case. This however might be required to support MSN.
			#self.connectionHandler.onXmppConnectionRosterItemAdd(
			#										friendID, transport )
			return True

		elif stanzaType == "error":
			self.connectionHandler.onXmppConnectionError(
					"An error was encountered while adding a friend "
						"to the roster." )

		return False


	def onIQStanza_RosterItemDelete( self, stanza ):
		# This can occur from a /delFriend initiated deletion where the remote
		# side (eg: Pidgin) hasn't removed us from their list yet.

		# NB: This may already have happened from an 'unsubscribed' presence
		#     on a Pidgin initiated removal.

		stanzaID   = getAttr( stanza, "id" )
		stanzaType = getAttr( stanza, "type" )

		# Check that this is a remove we know about
		if not self.stanzaIDs.has_key( stanzaID ):
			log.warning( "Unknown roster deletion message received: %s",
				stanzaID )
			return False

		# Remove the ID from our known ids
		(friendID, transport) = self.stanzaIDs.pop( stanzaID )

		# Now handle success or failure
		if stanzaType == "result":
			# Now notify the client.
			self.connectionHandler.onXmppConnectionRosterItemDelete(
													friendID, transport )
			return True

		elif stanzaType == "error":
			self.connectionHandler.onXmppConnectionError(
					"An error was encountered while removing '%s' from "
						"the roster." % friendID )

		return False


	def onIQStanza_LegacyRegister( self, stanza ):

		stanzaType = getAttr( stanza, 'type' )
		stanzaID = getAttr( stanza, 'id' )

		# Verify that this was a request we submitted
		if not self.stanzaIDs.has_key( stanzaID ):
			log.notice( "Received unknown legacy network registration "
				"message" )
			return False

		# Remove the ID from our known ids
		(transport, username, password) = self.stanzaIDs.pop( stanzaID )

		if stanzaType == "result":
			self.connectionHandler.onXmppConnectionTransportAccountRegistered(
												transport, username, password )

			# We are supposed supposed to send a roster addition for the
			# new transport gateway.
			#transportDomain = self.xmppCreateDomainFromTransport( transport )

			return True


		elif stanzaType == "error":
			self.connectionHandler.onXmppConnectionError(
					"An error was encountered while registering with "
						"the legacy '%s' network" % transport )

		return False


	def onIQStanza_LegacyDeregister( self, stanza ):

		stanzaType = getAttr( stanza, 'type' )
		stanzaID = getAttr( stanza, 'id' )

		# Verify that this was a request we submitted
		if not self.stanzaIDs.has_key( stanzaID ):
			log.notice( "Received unknown legacy network de-registration "
				"message" )
			return False

		# Remove the ID from our known ids
		transport = self.stanzaIDs.pop( stanzaID )

		if stanzaType == "result":
			self.connectionHandler.onXmppConnectionTransportAccountDeregistered( transport )

			# Should remove the item from the roster now?
			transportDomain = self.xmppCreateDomainFromTransport( transport )

			# Create a unique ID to identify this removal request with
			stanzaID = self.generateNewID( "legacy_roster_del" )

			self.stanzaIDs[ stanzaID ] = (transport)

			self.sendStanza( Stanzas.rosterDel( stanzaID, transportDomain ) )

			return True

		elif stanzaType == "error":
			self.connectionHandler.onXmppConnectionError(
					"An error was encountered while de-registering with "
						"the legacy '%s' network" % transport )

		return False


	def onIQStanza_LegacyRosterDelete( self, stanza ):

		stanzaType = getAttr( stanza, 'type' )
		stanzaID = getAttr( stanza, 'id' )

		# Verify that this was a request we submitted
		if not self.stanzaIDs.has_key( stanzaID ):
			log.notice( "Received unknown legacy network de-registration "
				"message" )
			return False

		# Remove the ID from our known ids
		transport = self.stanzaIDs.pop( stanzaID )

		if stanzaType == "result":
			return True

		elif stanzaType == "error":
			self.connectionHandler.onXmppConnectionError(
					"An error was encountered while de-registering with "
						"the legacy '%s' network" % transport )

		return False


	def onIQStanza_ListFriends( self, stanza ):

		stanzaType = getAttr( stanza, 'type' )

		if stanzaType != "set" and stanzaType != "result":
			return False

		items = [x for x in getChild( stanza, 'query' )[ 'children' ]
					if x['name'] == 'item']

		friendList = []
		for friendItem in items:

			friendJID = getAttr( friendItem, "jid" ).encode( "utf8" )
			(friendID, transport) = self.xmppConvertJIDToFriendID( friendJID )

			subscriptionType = getAttr( friendItem, "subscription" )

			# Don't show this roster item if we aren't a connection owner
			# e.g. 'to' or 'both'.
			# See: http://xmpp.org/rfcs/rfc3921.html
			#      - 7.1.  Syntax and Semantics
			if subscriptionType and (subscriptionType == "none" or
					subscriptionType == "from"):
				continue

			# Don't include ourselves in the roster
			if friendID == self.jid:
				continue

			if self.isTransportDomain( friendID ):
				continue

			friendPresence = {	"friendID": friendID, "transport": transport }
			friendList.append( friendPresence )

		# Pass our current roster through to the client.
		self.connectionHandler.onXmppConnectionRoster( friendList )

		return True


	def onIQStanza_RosterPush( self, stanza ):
		# This appears to be from  http://xmpp.org/rfcs/rfc3921.html
		#  7.2.  Business Rules
		#   .. "roster push" (incoming IQ of type "set" containing
		#   a roster item) ...

		# TODO: IMPORTANT NOTE!!!
		# This 'push' looks to be basically an update of the ejabber
		# roster status. Our roster system is slightly different, in
		# that we are only interested in subscriptions when they are
		# authorised, not a direct mirror of the ejabber roster.

		stanzaType = getAttr( stanza, 'type' )

		if stanzaType == "set":
			stanzaID = getAttr( stanza, 'id' )
			sender = getAttr( stanza, 'from' )

			if not sender:
				# Is from the server
				pass

			else:

				# If the 'jid' is a transport and the roster item is a 'from'
				# subcription (ie: they have us, we don't have them), we are
				# required to add them so it is a bi-directional association.
				query = getChild( stanza, 'query' )
				if query:
					item = getChild( query, 'item' )

					remoteJID = getAttr( item, 'jid' )
					subscription = getAttr( item, 'subscription' )
				
					if remoteJID and self.isTransportDomain( remoteJID ):
						if subscription == "from":
							self.sendStanza(
									Stanzas.presenceSubscribe( self.jid,
															remoteJID ) )

			# Reply to the roster push with an acknowledgement.
			self.sendStanza( Stanzas.rosterSetReply(
								stanzaID, self.jid, sender ) )


	# This method is invoked for Info/Query messages or 'iq' messages. This is
	# a request/response type message.
	# See: http://xmpp.org/rfcs/rfc3920.html#stanzas-semantics-iq
	def onStanzaInfoQuery( self, stanza ):

		stanzaID = getAttr( stanza, 'id' )

		if stanzaID and stanzaID.startswith( "request_roster" ):
			self.onIQStanza_ListFriends( stanza )

		elif stanzaID == 'push':
			self.onIQStanza_RosterPush( stanza )

		elif stanzaID and stanzaID.startswith( "remove" ):
			self.onIQStanza_RosterItemDelete( stanza )

		# A stanzaID with 'roster' is most likely going to be a rosterAdd
		# coming back.
		elif stanzaID and stanzaID.startswith( "roster" ):
			self.onIQStanza_RosterItemAdd( stanza )

		# A registration to a legacy network
		elif stanzaID and stanzaID.startswith( "legacy_reg" ):
			self.onIQStanza_LegacyRegister( stanza )

		# A de-registration to a legacy network
		elif stanzaID and stanzaID.startswith( "legacy_dereg" ):
			self.onIQStanza_LegacyDeregister( stanza )

		# A deletion of a legacy network roster item (post deregistration)
		elif stanzaID and stanzaID.startswith( "legacy_roster_del" ):
			self.onIQStanza_LegacyRosterDelete( stanza )

		else:
			log.notice( "Connection::onStanzaInfoQuery: Received unknown "
					"message ID: %s", stanzaID )


	def onStanzaMessage( self, stanza ):
		isMessage = getAttr( stanza, 'type' ) in [None, 'message', 'chat']
		body = getChild( stanza, 'body' )
		if not isMessage or not body:
			return

		sender = getAttr( stanza, 'from' ).encode( "utf8" )
		(friendID, transport) = self.xmppConvertJIDToFriendID( sender )

		message = body[ 'data' ].encode( "utf8" )

		# Pass the message back to the client now
		self.connectionHandler.onXmppConnectionMessage(
											friendID, transport, message )


	def onStanzaPresence( self, stanza ):
		sender = getAttr( stanza, 'from' ).encode( "utf8" )

		(friendID, transport) = self.xmppConvertJIDToFriendID( sender )

		if not friendID or friendID == self.jid:
			return

		presenceType = getAttr( stanza, 'type' )

		if not presenceType:

			# TODO: It would be useful to be able to track the status of
			#       friends, in the same way games have a /afk command.
			#presenceStatus = getChild( stanza, "show" )
			#if presenceStatus and presenceStatus.has_key( "data" ):
			#	print "Presence status:", presenceStatus[ "data" ]

			presenceType = "available"

		isTransport = self.isTransportDomain( sender )
		if isTransport:
			# Don't send any transport presence through to clients, just
			# update the status of this transports presence

			# If a transport has requested a subscription to us, we should
			# allow it.
			if presenceType == "subscribe":
				self.sendStanza( Stanzas.SUBSCRIBE_ALLOW % (self.jid, sender) )

			transport = self.getTransportFromJID( sender )
			self.transports[ transport ] = presenceType

		else:
			# Notify the client of the presence update
			self.connectionHandler.onXmppConnectionPresence(
									friendID, transport, presenceType )


	# send auth response - see rfc 2831, rfc 3920
	def onStanzaAuthChallenge( self, nextStanza ):
		# TODO: move these methods out
		# H( ... ) in rfc
		def H( s ):
			return hashlib.md5( s ).digest()

		# same as HEX(H( ... )) in rfc
		def HEXH( s ):
			return hashlib.md5( s ).hexdigest()

		# same as HEX(KD( ...,... )) in rfc
		def HEXKD( k, s ):
			return HEXH( '%s:%s' % (k, s) )

		challenge = base64.b64decode( nextStanza[ "data" ] )
		if challenge.startswith( "rspauth" ):
			self.sendStanza( Stanzas.AUTHENTICATION_END )

		else:
			nonce = challenge.split( "nonce=" )[1].split( '"' )[1]
			cnonce = ""
			for i in range( 32 ):
				cnonce += '%x' % random.randint( 0, 15 )

			userHash = H( ':'.join(
							(self.username, self.hostname, self.password) ) )
			A1 = ':'.join( (userHash, nonce, cnonce) )
			A2 = 'AUTHENTICATE:xmpp/%s' % self.hostname

			tmpJoin = ':'.join( (nonce, '00000001', cnonce, 'auth', HEXH( A2 )))
			response = HEXKD( HEXH( A1 ), tmpJoin )

			authBody = Stanzas.AUTHENTICATION_BODY % \
						( self.username, self.hostname, nonce, \
							cnonce, self.hostname, response )

			# Now send it.
			self.sendStanza( Stanzas.AUTHENTICATION_RESPONSE % \
								base64.b64encode( authBody ) )



# ----------------------------------------------------------------------
# Section: Helper functions for Stanza access
# ----------------------------------------------------------------------

def getAttr( stanza, name ):
	return stanza[ "attr" ].get( name )


def getChild( stanza, name ):
	for c in stanza[ "children" ]:
		if c[ "name" ] == name:
			return c

	return None


def stateToString( state ):
	if state == STATE_OFFLINE:
		return "Offline"
	elif state == STATE_CONNECT_TCP:
		return "Establishing Socket"
	elif state == STATE_REGISTERING:
		return "Registering connection"
	elif state == STATE_CONNECT_XMPP:
		return "Connecting to XMPP server"
	elif state == STATE_AUTHENTICATING:
		return "Authenticating with XMPP server"
	elif state == STATE_ONLINE:
		return "Online"
	else:
		return "Unknown"

# xmpp/Connection.py
