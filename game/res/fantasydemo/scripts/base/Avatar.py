import BigWorld
import CustomErrors
from AvatarCommon import AvatarCommon
import random
from functools import partial
import TradeHelper
import TradingSupervisor
import Inventory
import ItemBase
import FDConfig
from GameData import FantasyDemoData
import TeleportPoint
import AvatarModel
import PlayerModel
import GuardSpawner
from NoteReporter import NoteReporter
from KeepAlive import KeepAlive
import ThrottledMethods

import xmpp.Client as XMPPClient
import xmpp.Connection as XMPPConnection
import XMPPEventNotifier

from twisted.internet import defer

import ResMgr
import json
from bwdebug import *

# Should a log on be allowed if an entity is already logged in?
ALLOW_NEW_LOG_ONS = False

def spiralGeneratorFunc():
	pos = [0, 0]
	axis = True
	direction = True
	numSteps = 1
	iter = numSteps
	while True:
		yield pos
		pos[ axis ] += [-1, 1][ direction ]
		iter -= 1
		if iter == 0:
			axis = not axis
			if axis:
				direction = not direction
				numSteps += 1
			iter = numSteps

spiralGenerator = spiralGeneratorFunc()

class Avatar( BigWorld.Proxy, AvatarCommon, NoteReporter,
		XMPPClient.Client, KeepAlive ):

	# item lock states
	TRADE_OFFERING 			= 1
	TRADE_OFFER 			= 2
	TRADE_REPLYING 			= 3
	TRADE_REPLY 			= 4
	TRADE_ACCEPTING 		= 5
	TRADE_REJECTED 			= 6
	TRADE_REPLY_CANCELLING 	= 7
	TRADE_OFFER_CANCELLING 	= 8

	def __init__( self ):
		BigWorld.Proxy.__init__( self )
		AvatarCommon.__init__( self )
		NoteReporter.__init__( self )
		XMPPClient.Client.__init__( self )
		KeepAlive.__init__( self )

		import ItemBase
		items = []
		for i in self.inventoryItems:
			items.append(i)
		self.inventoryItems = items

		# List of friend base mailboxes. If friend is online, mailbox is not
		# None.
		# friendBases[i] is mailbox for friendsList[i].
		self.friendBases = []

		self.initInventory()

		# self.playerName initialised below


	def onLoggedOn( self, logOnData ):
		"""Called after __init__ if we were created for a log on"""
		pass


	def initInventory( self ):
		self.inventoryMgr = Inventory.InventoryMgr( self )

		# allocate item serials if we don't already have them
		# e.g. for new items
		for item in self.inventoryItems:
			if item['serial'] == -1:
				item['serial'] = self.inventoryMgr._genItemSerial()


	def onEntitiesEnabled( self ):
		self.cancelKeepAlive()

		# The initial position of the Avatar could be set here but it is
		# currently set to the TeleportPoint's position in the cell's
		# Avatar.__init__() method.
		#self.cellData[ "position" ] = FantasyDemoData.REALMS[ self.realm ].spaces[0].startPosition

		self.basePlayerName = self.cellData[ "playerName" ]

		self.cellData['avatarModel'] = AvatarModel.pack( self.persistentAvatarModelData )

		self.initFriendsList()

		# Create at teleport point. Cell entity sets the position
		self.createCellEntity( self.getTeleportPoint().cell )

		# Don't allow bots to connect to the XMPP server, it results in a lot
		# of undesired accounts being created.
		if not self.isBot() or FDConfig.BOTS_CAN_USE_XMPP:
			self.xmppConnect( self.xmppName, self.xmppName, self )

		XMPPEventNotifier.broadcast( self.xmppName + " has logged on" )


	def getTeleportPoint( self ):
		return TeleportPoint.find( self.realm )


	def destroySelf( self ):
		self.destroy()


	def isBot( self ):
		return self.basePlayerName.startswith( "Bot_" )


	def associateAccount( self, accountMB ):
		self.account = accountMB


	def writeCreatedEntity( self, shouldDestroy ):
		print "Avatar.writeCreatedEntity"
		deferred = defer.Deferred()

		def callback( wasSuccessful ):
			if wasSuccessful:
				result = (self.databaseID, self.persistentAvatarModelData )
			else:
				result = defer.fail(
						CustomErrors.DBError( "Write to db failed" ) )

			if shouldDestroy:
				self.destroy()

			return result

		deferred.addCallback( callback )

		self.writeToDB(
			lambda wasSuccessful, avatarMB: deferred.callback( wasSuccessful ) )

		return deferred


	def checkTeleportPointForAccount( self ):
		if self.realm == '':
			print "Avatar: Defaulting to %s" % \
					FantasyDemoData.DEFAULT_REALM_NAME
			self.realm = FantasyDemoData.DEFAULT_REALM_NAME

		# Test that the teleport point is valid.
		if self.getTeleportPoint() is None:
			print "Avatar: Initial teleport point in '%s' not available yet." % \
					self.realm
			self.account.onAvatarTeleportPointCheck( False )
			return

		self.account.onAvatarTeleportPointCheck( True )


	# ---------------------------------------------------------------------
	# Section: Exposed XMPP related methods
	# ---------------------------------------------------------------------
	def xmppTransportAccountRegister( self, transport, username, password ):

		if transport == "xmpp":
			self.onXmppConnectionError( "XMPP is not a valid legacy transport" )
			return

		if not self.xmppConnection:
			self.onXmppConnectionError( "Not connected to XMPP Server" )
			return

		if not transport or not username or not password:
			self.onXmppConnectionError( "Invalid credentials provided" )
			return

		for transportDetails in self.xmppTransportDetails:
			if transport == transportDetails[ "transport" ]:
				self.onXmppConnectionError( "Already registered with %s " \
						"using username '%s'." % \
							(transport, transportDetails[ "username" ]) )
				return

		# Should now be safe to register via the connection
		self.xmppConnection.transportAccountRegister(
												transport, username, password )


	def xmppTransportAccountDeregister( self, transport ):

		if not transport or transport == "xmpp":
			self.onXmppConnectionError( "Invalid legacy transport" )
			return

		if not self.xmppConnection:
			self.onXmppConnectionError( "Not connected to XMPP Server" )
			return

		# Should now be safe to de-register via the connection
		self.xmppConnection.transportAccountDeregister( transport )


	####
	# XMPP messages from the ejabber server
	# ---------------------------------------------------------------------
	# Section: XMPPConnectionHandler Methods
	# ---------------------------------------------------------------------

	def onXmppConnectionStateChange( self, newState, oldState ):

		if newState == XMPPConnection.STATE_ONLINE and \
			oldState != XMPPConnection.STATE_ONLINE:

			# Request the roster now we have gone online.
			self.xmppConnection.requestRoster()

			# Register with any transports we have previously registered with
			for transportDetails in self.xmppTransportDetails:
				transport = transportDetails[ "transport" ]
				username = transportDetails[ "username" ]
				password = transportDetails[ "password" ]

				self.xmppConnection.transportAccountRegister(
												transport, username, password )


	def onXmppConnectionTransportAccountRegistered( self, transport,
			username, password ):

		# Check if we have a previously registered with this transport
		hasTransport = bool( [ td for td in self.xmppTransportDetails
								if td[ "transport" ] == transport ] )

		# If we don't, add it and notify the client
		if not hasTransport:
			# Add the details to our persistent property
			self.xmppTransportDetails.append( { "transport": transport,
								"username": username, "password": password } )

			self.client.onXmppRegisterWithTransport( transport )


	def onXmppConnectionTransportAccountDeregistered( self, transport ):

		hasTransport = False
		for transportDetails in self.xmppTransportDetails:
			if transportDetails[ "transport" ] == transport:
				self.xmppTransportDetails.remove( transportDetails )

				hasTransport = True

		if hasTransport:
			self.client.onXmppDeregisterWithTransport( transport )


	def onXmppConnectionError( self, message ):
		self.client.onXmppError( message )


	def onXmppConnectionMessage( self, friendID, transport, message ):

		# XMPP will be providing us with a UTF-8 encoded string.
		if isinstance( message, str ):
			message = message.decode( "utf8" )

		# Pass the message through to the client
		self.client.onXmppMessage( friendID, transport, message )


	def onXmppConnectionRoster( self, roster ):
		self.client.onXmppRoster( roster )


	def onXmppConnectionRosterItemAdd( self, friendID, transport ):
		self.client.onXmppRosterItemAdd( friendID, transport )


	def onXmppConnectionRosterItemDelete( self, friendID, transport ):
		self.client.onXmppRosterItemDelete( friendID, transport )


	def onXmppConnectionPresence( self, friendID, transport, presence ):

		# We only want to notify the client about generalised friend events.
		# The resource name is not important from the client perspective.
		generalFriendID = friendID.split( "/", 1 )[0]

		shouldForwardPresence = True

		# Now perform any other actions we need to.

		if presence == "subscribe":
			# Request being made to become a friend of us

			# Auto-authorise any requests for the time being
			self.xmppConnection.friendAuthorise( friendID, transport )

			# The addition of the friend is performed in the client.
			# See client/Avatar.py onXmppPresence( "subscribe" )

		elif presence == "subscribed":
			self.client.onXmppRosterItemAdd( generalFriendID, transport )
			shouldForwardPresence = False

		elif presence == "unsubscribed":
			self.client.onXmppRosterItemDelete( generalFriendID, transport )
			shouldForwardPresence = False

		else:
			pass


		# Notify the client of the presence change.
		if shouldForwardPresence:
			# NB: The presence is encoded as a utf8 string as the contents are
			#     dictated by the XMPP server presence which is only ascii.
			self.client.onXmppPresence( generalFriendID, transport,
										presence.encode( "utf8" ) )



	# ---------------------------------------------------------------------
	# Section: Avatar Fault Tolerance / Recovery Methods
	# ---------------------------------------------------------------------

	def onDestroy( self ):
		# Ensure that the XMPP connection has been destroyed so we don't leave
		# a lingering socket open.
		self.xmppDisconnect()


	def onRestore( self ):
		self.initInventory()

		# xmppConnection will normally not be backed as it is an undefined
		# property. We do not see warning messages about it, because it is
		# listed in Avatar.def <TempProperties>.
		self.xmppConnection = None

		if hasattr( self, "cell" ):
			if not self.isBot() or FDConfig.BOTS_CAN_USE_XMPP:

				self.xmppConnect( self.basePlayerName,
									self.basePlayerName, self )


	def onCreateCellFailure( self ):
		print "onCreateCellFailure", self.id
		if self.account != None:
			self.account.onAvatarDeath( self.databaseID, self.cellData['avatarModel'] )
		self.client.clientOnCreateCellFailure()


	def onLoseCell( self ):
		self.notifyAdmirers( False )
		if self.account != None:
			self.account.onAvatarDeath( self.databaseID,
				self.cellData['avatarModel'] )

		if not self.haveWebClient: 	# wait for keep alive to expire if we have a
									# web session holding onto us
			self.destroy()


	def onClientDeath( self ):
		print "Avatar(%d).onClientDeath" % self.id
		if hasattr( self, "basePlayerName" ):
			XMPPEventNotifier.broadcast(
					self.basePlayerName + " has logged off" )

		if hasattr(self, "cell" ):
			self.destroyCellEntity()
		else:
			if not self.haveWebClient:
				self.destroy()


	def onAddNote( self, id ):
		print "Telling the client about note:", id
		self.client.onAddNote( id )


	def onGetNotes( self, notes ):
		self.client.onGetNotes( notes )


	def teleportTo( self, space, label ):
		dst = TeleportPoint.find( self.realm, space, label )

		if dst:
			self.teleport( dst )

			XMPPEventNotifier.broadcast(
				"%s teleported to %s" % (self.basePlayerName, label) )
		else:
			self.client.addInfoMsg( u"Invalid teleport destination %s %s" %
					(space, label) )


	def tryToTeleport( self, spaceName, pointName, spaceID ):
		if spaceName:
			dst = TeleportPoint.find( self.realm, spaceName, pointName )
			if dst:
				# teleport player to location
				self.client.addInfoMsg(
					u"Player teleporting to %s in %s:" % (pointName, spaceName) )
				self.client.teleportTo( spaceName, pointName )
			else:
				self.client.addInfoMsg(
					u"TeleportSource has incorrect destination. Options are:" )
				for match in TeleportPoint.match( realm = self.realm ):
					self.client.addInfoMsg( u"%s %s" % (match[2], match[3]) )
		else:
			self.matchTeleportLabel( pointName, spaceID )

	def matchTeleportLabel( self, pointName, spaceID ):
		matches = TeleportPoint.match( realm = self.realm,
				pointName = pointName )

		for key in matches:
			BigWorld.globalBases[ key ].cell.tryToTeleport(
				key[2], key[3], self, spaceID )


	# -------------------------------------------------------------------------
	# Friends list
	# -------------------------------------------------------------------------
	MAX_FRIENDS = 30

	def initFriendsList( self ):
		# Send list of friend names to client.
		if not FDConfig.UNSCRIPTED_BOTS_MODE:
			self.client.newFriendsList( [ x[0] for x in self.friendsList ] )

		# Set friend base mailboxes to None (i.e. assume they are offline)
		# Note: Client also assumes friends are offline during initialisation.
		self.friendBases =  [ None for x in self.friendsList ]
		for i in range( len(self.friendsList) ):
			BigWorld.lookUpBaseByDBID( "Avatar", self.friendsList[i][1], \
				partial( self.onInitDBLookUpCb, i ) )

		self.notifyAdmirers( True )

	def onInitDBLookUpCb( self, idx, friendBase ):
		if type(friendBase) is not bool:
			# Friend is online
			self.friendBases[idx] = friendBase
			self.client.setFriendStatus( idx, True )

	def notifyAdmirers( self, online ):
		if online:
			ourBase = self
		else:
			ourBase = None
		for admirerDBID in self.admirersList:
			BigWorld.lookUpBaseByDBID( "Avatar", admirerDBID, \
				partial( Avatar_onNotifyAdmirersDBLookUpCb, self.databaseID, \
				ourBase ) )


	def addFriend( self, friendName ):

		if friendName == self.basePlayerName:
			self.messageToClient( "Adding yourself as a friend is not allowed." )
			return

		if len( self.friendsList ) >= self.MAX_FRIENDS:
			self.messageToClient( 
				"You already have the maximum number of friends allowed: " 
					+ str( self.MAX_FRIENDS ) )
			return

		BigWorld.createBaseFromDB( "Avatar", friendName,
			partial( self.onAddFriendCreateBaseCb, friendName ) )


	def onAddFriendCreateBaseCb( self, friendName, friendBase, dbID,
								wasActive ):
		if friendBase != None:
			if wasActive:
				friendBase.addAdmirer( self.databaseID, self, True )
			else:
				# addAdmirer() needs playerName to be set.
				friendBase.basePlayerName = friendBase.cellData[ "playerName" ]
				friendBase.addAdmirer( self.databaseID, self, False )
				# Should destroy the base that we've created temporarily
				friendBase.destroy()
		else:
			self.messageToClient( "Cannot add unknown player: " + friendName )

	def onAddedAdmirerToFriend( self, friendName, friendDBID, friendBase ):
		# Double check here due to race condition of multiple addFriends
		# when we have MAX_FRIENDS - 1 friends
		if len(self.friendsList) >= self.MAX_FRIENDS:
			self.messageToClient( "You already have the maximum number of friends allowed: " \
				+ str(self.MAX_FRIENDS) )
		else:
			self.friendsList.append( ( friendName, friendDBID ) )
			self.friendBases.append( friendBase )
			online = friendBase != None
			self.client.onAddedFriend( friendName, online )

	def delFriend( self, friendIdx ):
		friendBase = self.friendBases.pop(friendIdx)
		if friendBase != None:
			friendBase.delAdmirer( self.databaseID )
		else:
			BigWorld.createBaseFromDBID( "Avatar", \
				self.friendsList[friendIdx][1], self.onDelFriendCreateBaseCb )
		del self.friendsList[ friendIdx ]

	def onDelFriendCreateBaseCb( self, friendBase, dbID, wasActive ):
		if friendBase != None:
			friendBase.delAdmirer( self.databaseID )
			# Should destroy the base that we've created temporarily
			friendBase.destroy()

	def addAdmirer( self, admirerDBID, admirerBase, online ):
		self.admirersList.append( admirerDBID )
		if online:
			onlineBase = self
		else:
			onlineBase = None
		admirerBase.onAddedAdmirerToFriend( self.basePlayerName,
											self.databaseID, onlineBase )

	def delAdmirer( self, admirerDBID ):
		self.admirersList.remove( admirerDBID )

	# friendBase is None if friend is going offline.
	# friendBase is friend's base mailbox if they are coming online
	def onFriendStatusChange( self, friendDBID, friendBase ):
		for i in range( len (self.friendsList ) ):
			if self.friendsList[i][1] == friendDBID:
				self.friendBases[i] = friendBase
				online = friendBase != None
				self.client.setFriendStatus( i, online )
				break

	def sendMessageToFriend( self, friendIdx, message ):
		friendBase = self.friendBases[friendIdx]
		if friendBase != None:
			friendBase.client.onReceiveMessageFromAdmirer( self.basePlayerName,
															 message )
		else:
			self.messageToClient( "Cannot send message to offline player." )

	def getFriendInfo( self, friendIdx ):
		friendBase = self.friendBases[friendIdx]
		if friendBase != None:
			friendBase.getInfoForAdmirer( self )
		else:
			self.messageToClient( "Cannot get information on offline player." )

	def getInfoForAdmirer( self, admirerBase ):
		friendNames = [ name for (name, dbid) in self.friendsList ]
		self.cell.getInfoForAdmirer( \
			"[Friends: " + unicode(friendNames)[1:-1] + "]", admirerBase )

	#make so that system can talk to client
	def messageToClient( self, mesg ):
		self.client.showMessage( 3, 'System', unicode( mesg ) )

	def setBandwidthPerSecond( self, bps ):
		self.bandwidthPerSecond = bps

	# -------------------------------------------------------------------------
	# Section: Items trading
	# -------------------------------------------------------------------------

	def tradeCommitActive( self, outItemsLock ):
		"""Cell is requesting base to commit an items trade (actively).
		Params:
			outItemsLock		lock handle to item being traded out
		"""
		self.outItemsLock = outItemsLock
		# now wait for tradeSyncRequest


	def tradeSyncFail( self ):
		"""The passive base is notifying us that it could not
		initiate the trade (by calling tradeSyncRequest).
		"""
		self.tradeCommitNotify( False, self.outItemsLock, [], 0, [], [], 0 )


	def tradeCommitPassive( self, outItemsLock, activeBase ):
		"""Cell is requesting base to commit an items trade (passively).
		Params:
			outItemsLock		lock handle to item being traded out
			activeBase			base of active partner
		"""
		try:
			itemsSerials, itemsTypes, goldPieces = \
					self.inventoryMgr.itemsLockedRetrieve( outItemsLock )

			tradeParams = { "dbID": self.databaseID, \
							"tradeID": self.lastTradeID+1, \
							"lockHandle": outItemsLock, \
							"itemsSerials": itemsSerials, \
							"itemsTypes": itemsTypes, \
							"goldPieces": goldPieces	}

			activeBase.tradeSyncRequest( self, tradeParams )

		except Inventory.LockError:
			activeBase.tradeSyncFail()
			self.tradeCommitNotify( False, outItemsLock, [], 0, [], [], 0 )
			errorMsg = "Avatar.tradeCommitPassive: couldn't retrieve locked "\
				"items "
			parameters = '(lock=%d)' % outItemsLock
			print errorMsg + parameters


	def tradeSyncRequest( self, partnerBase, partnerTradeParams ):
		"""The meeting of the active and passive trading info collections.
		Will request TradingSupervisor to commence a trading operation.
		Params:
			partnerBase			base of partner
			partnerDBID			BDID of partner
			partnerTradeID		tradeID of partner
			inItemsLock			lock handle to items being traded in
			inItemsSerials		serial of items being traded in
			inItemsTypes	   types of items being traded in
			inGoldPieces      ammount of gold being traded in
		"""
		try:
			outItemsSerials, outItemsTypes, outGoldPieces = \
					self.inventoryMgr.itemsLockedRetrieve( self.outItemsLock )
			supervisor = BigWorld.globalBases[ "TradingSupervisor" ]

			selfTradeParams = { "dbID": self.databaseID, \
								"tradeID": self.lastTradeID+1, \
								"lockHandle": self.outItemsLock, \
								"itemsSerials": outItemsSerials, \
								"itemsTypes": outItemsTypes, \
								"goldPieces": outGoldPieces	}

			supervisor.commenceTrade( self, selfTradeParams,
				partnerBase, partnerTradeParams )

		except Inventory.LockError:
			errorMsg  = 'Avatar.tradeSyncRequest: lock error (lock=%d)'
			print errorMsg % ( self.outItemsLock )


	def tradeSyncReject( self ):
		self.tradeCommitNotify( False, self.outItemsLock, [], 0, [], [], 0 )
		partnerBase.tradeCommitNotify( False, partnerTradeParams[
			"lockHandle" ], [], 0, [], [], 0 )


	def tradeCommit(
			self, supervisor, tradeID, outItemsLock,
			outItemsSerials, outGoldPieces,
			inItemsTypes, inGoldPieces, withWhom):
		"""Performs the trade for this entity.
		Params:
			supervisor			mailbox of trading supervisor
			tradeID				ID of this trade
			outItemsLock		lock handle to items being traded out
			outItemsSerials	serial of items being traded out
			outGoldPieces		ammount of gold being traded out
			inItemsTypes	   types of items being traded in
			inGoldPieces      ammount of gold being traded in
		"""
		TradeHelper.tradeCommit(
			self, supervisor, tradeID, outItemsLock,
			outItemsSerials, outGoldPieces,
			inItemsTypes, inGoldPieces )


	def tradeCommitNotify( self, success,
			outItemsLock, outItemsSerials,
			outGoldPieces, inItemsTypes,
			inItemsSerials, inGoldPieces ):
		"""The active party (either us our our partner) is informing us the
		result of the trade sync. Forward this information to the cell.
		Params:
			success:				True is trade was successful. False is it failed
			outItemsLock		lock handle to items being traded out
			outItemsSerials	serial of items being traded out
			outGoldPieces		ammount of gold being traded out
			inItemsTypes	   types of items being traded in
			inGoldPieces      ammount of gold being traded in
		"""
		if not success and outItemsLock != 0:
			try:
				self.inventoryMgr.itemsUnlock( outItemsLock )
			except Inventory.LockError:
				errorMsg = "Avatar.tradeCommitNotify: couldn't unlock items (lock=%d)"
				print errorMsg % outItemsLock

		if hasattr(self, 'cell'):
			self.cell.tradeCommitNotify( success, outItemsLock,
					outItemsSerials, outGoldPieces, inItemsTypes,
					inItemsSerials, inGoldPieces )

	# -------------------------------------------------------------------------
	# Section: Items locking
	# -------------------------------------------------------------------------

	def itemsLockRequest( self, lockHandle, itemsSerials, goldPieces ):
		"""The cell is requesting us to lock inventory items.
		Params:
			lockHandle			lock handle to be reused
			itemsSerials		serials of items to be locked
			goldPieces			ammount of gold to be locked
		"""
		try:
			inventoryMgr = self.inventoryMgr

			if lockHandle == Inventory.NOLOCK:
				lockHandle = inventoryMgr.itemsLock(itemsSerials, goldPieces)
			else:
				inventoryMgr.itemsRelock( lockHandle, itemsSerials, goldPieces )
			itemsSerials, itemsTypes, goldPieces = \
					inventoryMgr.itemsLockedRetrieve( lockHandle )

			if hasattr( self, 'cell' ):
				self.cell.itemsLockNotify( True, lockHandle,
						itemsSerials, itemsTypes, goldPieces )

		except (Inventory.LockError, ValueError), e:
			print "Lock error: %s: %s" % ( e.__class__, e )
			if hasattr(self, 'cell'):
				self.cell.itemsLockNotify( False, lockHandle, [], [], 0 )
			errorMsg  = 'Avatar.itemsLockRequest: lock error '
			arguments = '(lock=%d, items=%s, gold=%d)'
			print errorMsg + arguments % ( lockHandle, itemsSerials, goldPieces )

		return lockHandle

	def itemsUnlockRequest( self, lockHandle ):
		"""the client (via the cell) is requesting us to unlock inventory items.
		Params:
			lockHandle			handle to the previously locked items.
		"""
		success = False
		try:
			supervisor = BigWorld.globalBases[ "TradingSupervisor" ]
			if not supervisor.isAPendingTrade( self.id, lockHandle ):
				self.inventoryMgr.itemsUnlock( lockHandle )
				success = True
		except KeyError:
			self.inventoryMgr.itemsUnlock( lockHandle )
		except Inventory.LockError:
			pass

		if hasattr(self, 'cell'):
			self.cell.itemsUnlockNotify( success, lockHandle )

		return success

	# -------------------------------------------------------------------------
	# Section: Web interface methods
	# -------------------------------------------------------------------------

	def remoteTakeDamage( self, damage ):
		"""
		Causes the cell entity to lose health, and retrieves the updated health
		and maxHealth.

		Return values:	health::INT32
						maxHealth::INT32
		"""

		isOnline = hasattr( self, 'cell' )
		if not isOnline:
			return defer.fail( CustomErrors.DBError( "Avatar is not online" ) )

		deferred = self.cell.takeDamage( damage )
		deferred.addCallback( partial( self.onDamageTaken, damage ) )
		return deferred

	def onDamageTaken( self, damage, healthArgs ):
		health, maxHealth = healthArgs[ 0 ], healthArgs[ 1 ]
		print "Avatar '%s' took %d damage, reducing its health to %d/%d" % \
			(self.basePlayerName, damage, health, maxHealth)
		return (health,)

	def webGetPlayerInfo( self ):
		"""
		Retrieves the player name and other player info.

		Return values: 	databaseID::DBID
						charClass::STRING
						online::BOOL
						playerName::UNICODE_STRING
						position:ARRAY of FLOAT
						direction:ARRAY of FLOAT
						health::INT32
						maxHealth::INT32
						frags::INT32
		"""

		charClass = PlayerModel.modelListToCharacterClassString(
					self.persistentAvatarModelData['models'] )

		isOnline = hasattr( self, 'cell' )
		baseResults = (self.databaseID, charClass, isOnline)

		if not isOnline:
			return baseResults + (self.cellData['playerName'],
					(0., 0., 0.), # position
					(0., 0., 0.), # direction
					self.cellData['health'],
					self.cellData['maxHealth'],
					self.cellData['frags'])
		else:
			deferred = self.cell.getPlayerInfo()
			deferred.addCallback(
					lambda cellResults: baseResults + cellResults )
			return deferred


	def webGetGoldAndInventory( self ):
		"""
		Retrieves the available gold pieces and the inventory state.

		Response return values:

		goldPieces::GOLDPIECES
			The Avatar's available gold pieces.

		inventoryItems::PYTHON
			List of item descriptions as dictionaries with keys:
				'serial':		the serial number of the item
				'itemType':		the item type
				'lockHandle':	lock handle associated with this item

		lockedItems::PYTHON
			List of locked item descriptions as dictionaries with keys:
				'serials':		a list of serial numbers of locked items
				'goldPieces':	the gold pieces locked

		"""

		goldPieces = self.inventoryMgr.availableGoldPieces()

		inventoryItems = []
		lockedItems = {}

		for lockedEntry in self.inventoryLocks:
			lockedItems[ lockedEntry["lockHandle"] ] = {
				'serials'		: [],
				'goldPieces'	: lockedEntry[ "goldPieces" ]
			}

		for inventoryEntry in self.inventoryItems:
			inventoryItems.append( {
				'serial'		: inventoryEntry['serial'],
				'itemType'		: inventoryEntry['itemType'],
				'lockHandle'	: inventoryEntry['lockHandle']
			} )

			if inventoryEntry['lockHandle'] != -1:
				lockedItems[inventoryEntry['lockHandle']]['serials'].\
					append( inventoryEntry['serial'] )

		return (goldPieces, inventoryItems, lockedItems)


	def webCreateAuction( self, itemSerial, expiry, startBid, buyout ):
		"""
		Web method to create an auction.

		Response return values:
		auctionID::AUCTIONID
			The auction ID of the new auction.
		"""

		#print "Avatar(dbid=%d).webCreateAuction( " \
		#	"itemSerial=%s, expiry=%.01f, startBid=%d, buyout=%s )" % \
		#	(self.databaseID, itemSerial, expiry, startBid, str( buyout ))

		itemType = None

		# find the item type of the item pointed to by the item serial
		for itemDesc in self.inventoryItems:
			if itemDesc['serial'] == itemSerial:
				itemType = itemDesc['itemType']
				break

		# Lock the item.
		itemLock = self.itemsLockRequest( -1, [ itemSerial ], 0 )
		if itemLock == -1:
			return defer.fail( CustomErrors.InvalidItemError(
						"Could not lock item with serial: %s" %	(itemSerial) ) )

		if itemType is None:
			return defer.fail( CustomErrors.InvalidItemError(
						"Could not retrieve item type for itemSerial=%d" %\
				   	(itemLock) ) )

		try:
			auctionHouse = BigWorld.globalBases['AuctionHouse']
		except KeyError:
			self.itemsUnlockRequest( itemLock )
			return defer.fail( CustomErrors.AuctionHouseError(
						'Auction House entity does not exist '
						'or is not globally registered.' ) )

		deferred = auctionHouse.createAuction( self.databaseID, itemLock,
				itemType, itemSerial, startBid, expiry, buyout )

		deferred.addErrback( partial( self.onCreateAuctionFailure, itemLock ) )

		return deferred

	def onCreateAuctionFailure( self, itemLock, failure ):
		# unlock serial
		print "Avatar.onCreateAuctionFailure: Unlocking itemLock=%s because" \
			"of failure to create auction: %s: " % \
			(str( itemLock ), str( failure ))

		self.itemsUnlockRequest( itemLock )

		return failure

	def webBidOnAuction( self, auctionID, buyingOut, bidAmount ):
		"""
		Web method to bid on, or to buyout, an auction. Buyouts are indicated
		by asserting the buyingOut boolean value, in which case the bidAmount
		value is ignored.

		@param	auctionID 	The auction ID.
		@param	buyingOut	Whether to bid or buyout the auction.
		@param	bidAmount	This represents the maximum bid amount by the
							calling entity.

		Response return values:
			Empty tuple
		"""

		#print "Avatar(dbid=%d).webBidOnAuction( " \
		#	"auctionID=%s, buyingOut=%s, bidAmount=%d" % \
		#	(self.databaseID, auctionID, str( buyingOut ), bidAmount)

		try:
			auctionHouse = BigWorld.globalBases['AuctionHouse']
		except KeyError:
			print "Avatar(dbid=%d).webBidOnAuction: "\
				"Couldn't find AuctionHouse entity!" %\
				(self.databaseID)
			return defer.fail( CustomErrors.AuctionHouseError(
						"Could not find AuctionHouse entity." ) )

		if buyingOut:
			return auctionHouse.buyoutAuction( self,
					self.databaseID, auctionID )

		# lock away the bidAmount
		if self.inventoryMgr.availableGoldPieces() < bidAmount:
			return defer.fail( CustomErrors.InsufficientGoldError(
				"You do not have sufficient available gold to make this bid" ) )

		lockHandle = self.itemsLockRequest( Inventory.NOLOCK, [], bidAmount )
		if lockHandle == -1:
			print "Avatar(dbid=%d).webBidOnAuction: Could not lock gold" %\
				(self.databaseID)
			return defer.fail( CustomErrors.ItemLockError(
					"Could not lock %d gold" % bidAmount ) )


		deferred = auctionHouse.bidOnAuction( self, self.databaseID, auctionID, bidAmount,
			lockHandle )

		def onFailure( failure ):
			self.itemsUnlockRequest( lockHandle )
			return failure

		deferred.addErrback( onFailure )

		return deferred


	def lockAuctionGold( self, auctionID, goldAmount, existingLock ):
		"""
		A request method for the AuctionHouse to (re)lock an amount of gold
		to complete an auction.

		If there is an existing lock that needs to be unlocked prior to the new
		lock, it can be provided, and it is unlocked before relocking the given
		gold amount.

		Calls back on AuctionHouse.onLockGoldAmount when complete.

		@param	auctionID		the auction ID
		@param	goldAmount		the gold amount to lock
		@param	existingLock	any existing lock to be unlocked prior to
								locking the goldAmount
		"""

		auctionHouse = BigWorld.globalBases['AuctionHouse']
		if existingLock != -1:
			# check whether we have enough gold before we unlock the old lock

			(lockedItemsSerials, lockedItemsTypes, lockedGoldPieces) = \
				self.inventoryMgr.itemsLockedRetrieve( existingLock )

			if lockedGoldPieces + self.inventoryMgr.availableGoldPieces() \
					< goldAmount:
				auctionHouse.onLockGoldAmount( False,
					"Insufficient gold pieces",
					auctionID, self, Inventory.NOLOCK )
				return

			self.itemsUnlockRequest( existingLock )

		lockHandle = self.itemsLockRequest( Inventory.NOLOCK,
				[], goldAmount )

		if lockHandle == Inventory.NOLOCK:
			return defer.fail(
					CustomErrors.ItemLockError( "Could not lock gold" ) )

		return (lockHandle,)


	def onAuctionExpired( self, auctionID, itemLock ):
		"""
		Callback from the AuctionHouse when an auction sold by this player
		expires without a bid having been placed.
		"""

		#print "Avatar.onExpireAuction: auctionID=%s, itemLock=%s" %\
		#	(str( auctionID ), str( itemLock ))

		self.itemsUnlockRequest( itemLock )


	def onAuctionWon( self, auctionID, itemLock, bidPrice ):
		"""
		Callback method from the AuctionHouse when this Avatar has won an
		auction. Calls back on the AuctionHouse.completeAuction to complete
		the trade with the new lock handle for the auction bid amount at
		expiry (which may be different from the maximum bid amount made by
		this player).

		@param	auctionID	the auction ID
		@param	itemLock	the lock handle for the maximum bid used when this
							player bid
		@param	bidPrice	the actual amount of gold that the auction was bid
							at when it expired
		"""

		#print "Avatar.onWinAuction: "\
		#	"auctionID = %s, itemLock = %d, bidPrice = %d" \
		#	% (auctionID, itemLock, bidPrice)

		# unlock my maximum bid, and relock the auction bid amount at expiry
		self.itemsUnlockRequest( itemLock )
		newLockHandle = self.itemsLockRequest( Inventory.NOLOCK, [], bidPrice )

		# notify the AuctionHouse to do the trade
		BigWorld.globalBases['AuctionHouse'].completeAuction(
			auctionID, self, newLockHandle )


	def onAuctionOutbid( self, auctionID, itemLock ):
		"""
		Callback method from the AuctionHouse when this Avatar has been outbid
		by another bidder for the specified auction that this player has bid on.

		@param	auctionID	the auction ID
		@param	itemLock	the lock handle for the maximum bid used when this
							player bid
		"""

		#print "Avatar.onAuctionOutbid: "\
		#	"databaseID=%d, auctionID=%s, itemLock=%d" % \
		#	(self.databaseID, auctionID, itemLock)

		# give me my money back!
		self.itemsUnlockRequest( itemLock )

	def setAvatarModel( self, encodedAvatarModel ):
		self.persistentAvatarModelData = AvatarModel.unpack( encodedAvatarModel )
		self.cell.setAvatarModel( encodedAvatarModel )

	# -------------------------------------------------------------------------
	# Section: Items pick-up and drop
	# -------------------------------------------------------------------------

	def pickUpResponse( self, success, droppedItemID, itemType ):
		"""DroppedItem is responding to a pickup request (by the avatar's cell).
		Params:
			success			True is pickup request was granted. False otherwise
			droppedItemID	id of item entity being picked up
			itemType			type of item being picked up
		"""
		if success:
			itemsSerial = self.inventoryMgr.addItem( itemType )
			self.cell.pickUpResponse( True, droppedItemID, itemType, itemsSerial )

		else:
			self.cell.pickUpResponse( False, droppedItemID, 0, 0 )

	def dropRequest( self, itemSerial ):
		"""Client is requesting to drop an item from the inventory.
		Params:
			itemSerial			serial of item to be dropped
		"""
		try:
			itemType = self.inventoryMgr.removeItem( itemSerial )
			self.cell.dropNotify( itemSerial, itemType )
		except ValueError:
			self.client.dropDeny()
			errorMsg = 'Avatar.dropNotify: No such item in inventory: %d'
			print errorMsg % itemSerial
		except Inventory.LockError:
			self.client.dropDeny()
			errorMsg = 'Avatar.dropNotify: Item is locked: %d'
			print errorMsg % itemSerial

	# -------------------------------------------------------------------------
	# Section: Items commerce
	# -------------------------------------------------------------------------

	def commerceSellRequest( self, itemsLock, itemSerial, merchantBase ):
		"""Cell is requesting to sell an item to a merchant.
		Lock item and request merchant to buy the item from use.
		Params:
			itemLock				handle to locked item in client
			itemSerial			serial of item in inventory
			merchantBase		base mailbox of the buyer merchant
		"""
		try:
			inventoryMgr = self.inventoryMgr
			inventoryMgr.itemsRelock( itemsLock, [itemSerial], 0 )
			self.outItemsLock = itemsLock
			itemsSerials, itemTypes, gold = \
					inventoryMgr.itemsLockedRetrieve( self.outItemsLock )
			merchantBase.commerceBuyRequest(
					self.outItemsLock, itemsSerials, itemTypes, self )
			# now wait for tradeSyncRequest (called by the merchant)
		except (Inventory.LockError, ValueError):
			self.tradeCommitNotify( False, itemsLock, [], 0, [], [], 0 )
			errorMsg  = 'Avatar.commerceSellRequest: lock error (item=%d)'
			print errorMsg % ( itemSerial )


	def commerceBuyRequest( self, avatarLock,
			merchantBase, merchantDBID, merchantTradeID,
			merchantLock, itemsSerials, itemsTypes ):
		"""A merchant is requesting up to buy an item from him.
		Delegates processing to the trade helper class.
		Params:
			avatarLock			handle to locked item in client.
			merchantBase		base mailbox of the seller merchant.
			merchantDBID		DBID of seller merchant
			merchantTradeID	tradeID of seller merchant
			merchantLock		handle of locke item in seller's inventory
			itemsSerials		serials of items being bought
			itemsTypes			types of items being bought
		"""
		try:
			itemPrice = ItemBase.price( itemsTypes[0] )
			self.inventoryMgr.itemsRelock( avatarLock, [], itemPrice )
			self.outItemsLock = avatarLock

			merchantParams = { "dbID": merchantDBID, \
								"tradeID": merchantTradeID, \
								"lockHandle": merchantLock, \
								"itemsSerials": itemsSerials, \
								"itemsTypes": itemsTypes, \
								"goldPieces": 0	}

			self.tradeSyncRequest( merchantBase, merchantParams )

		except Inventory.LockError:
			self.tradeCommitNotify( False, avatarLock, [], 0, [], [], 0 )
			merchantBase.tradeCommitNotify( False, merchantLock, [], 0, [], [], 0 )
			errorMsg  = 'Avatar.commerceBuyRequest: lock error (gold=%d)'
			print errorMsg % ( itemPrice )


	def onLogOnAttempt( self, ip, port, logOnData ):
		# Allow log on to this entity if there is no client, ie from the web.
		if self.clientAddr == (0, 0):
			return BigWorld.LOG_ON_ACCEPT
		else:
			if ALLOW_NEW_LOG_ONS:
				# Log this entity off and let the new log on to then proceed
				# normally.
				self.logOff()
				return BigWorld.LOG_ON_WAIT_FOR_DESTROY
			else:
				# Do not allow the log on attempt.
				return BigWorld.LOG_ON_REJECT

	def webLogout( self ):
		print "Avatar(%d).webLogout" % self.id
		if not hasattr( self, "cell" ):
			if self.account != None:
				self.account.onAvatarDeath( self.databaseID, self.cellData['avatarModel'] )
			self.destroy()

	def spawnGuardsInSpace( self, spaceID, numberOfGuards, maxGuards, spawnDuration, timeToLive ):
		if not GuardSpawner.isGuardSpawnerReady( spaceID ):
			self.messageToClient( "Guard spawner is not ready yet, please try again later." )
		else:
			GuardSpawner.spawnGuardsInSpace( spaceID, numberOfGuards, maxGuards, spawnDuration, timeToLive )


	def removeGuardsFromSpace( self, spaceID, numberOfGuards ):
		if not GuardSpawner.isGuardSpawnerReady( spaceID ):
			self.messageToClient( "Guard spawner is not ready yet, please try again later." )
		else:
			GuardSpawner.removeGuardsFromSpace( spaceID, numberOfGuards )

	def summonEntity( self, typeName, position, direction, spaceID,
		properties ):

		propertyDict = {}
		propertyDict['position'] = position
		propertyDict['direction'] = direction
		propertyDict['spaceID'] = spaceID
		propertyDict['creatureType'] = properties['creatureType']
		propertyDict['creatureName'] = properties['creatureName']
		propertyDict['creatureState'] = properties['creatureState']
		propertyDict['seatType'] = properties['seatType']
		
		try:
			entity = BigWorld.createBaseAnywhere( typeName, propertyDict )
			if entity:
				self.client.entitySummoned( entity.id, typeName )
				return
		except:
			pass

		self.client.entitySummoned( 0, typeName )

	def onTimer( self, id, userArg ):
		KeepAlive.onTimer( self, id, userArg )


	@ThrottledMethods.hardThresholdBase( 2.0, 0.5 )
	def testThrottlingBase( self ):
		print "testThrottlingCellBase() called!\n"


	# -------------------------------------------------------------------------
	# Section: Map streaming
	# -------------------------------------------------------------------------

	def mapStreamRequest( self, geometry, depth ):
		dirName = '%s/space_viewer/tileset' % ( geometry, )
		tilesetDir = ResMgr.openSection( dirName )
		if tilesetDir is None:
			WARNING_MSG( "Request to set map for %s which has no tileset" % ( geometry, ) )
			return
		tilesetInfo = json.loads( tilesetDir[ "tileset.json" ].asBinary )
		# input depth 0 means 1 tile for the space
		# input depth 1 means 2x2 tiles for the space
		# input depth 2 means 4x4 times for the space
		depth = min( depth, tilesetInfo[ "depth" ] )
		span = pow( 2, depth )
		minX = tilesetInfo[ "worldBoundsOfRootTile" ][ "minX" ]
		minY = tilesetInfo[ "worldBoundsOfRootTile" ][ "minY" ]
		maxX = tilesetInfo[ "worldBoundsOfRootTile" ][ "maxX" ]
		maxY = tilesetInfo[ "worldBoundsOfRootTile" ][ "maxY" ]
		tileSizeX = (maxX - minX) / span
		tileSizeY = (maxY - minY) / span
		for x in range( span ):
			for y in range( span ):
				fileName = '%s/%d/%d/%d.jpg' % ( dirName, depth, x, y )
				if not ResMgr.isFile( fileName ):
					WARNING_MSG( "Tile (%d, %d) at depth %d for %s tileset not found" %
						( x, y, depth, geometry, ) )
					continue
				streamID = self.streamFileToClient( fileName, geometry )
				self.client.mapStreamResponse( streamID,
					minX + (x * tileSizeX),
					maxY - (y * tileSizeY) - tileSizeY,
					minX + (x * tileSizeX) + tileSizeX, 
					maxY - (y * tileSizeY) )

	def onSpaceLoaderDestroyed( self ):
		pass


# end of class Avatar

# this callback needs to be a global instead of a method of Avatar because we
# notify our admirers when the Avatar is being destroyed.
def Avatar_onNotifyAdmirersDBLookUpCb( ourDBID, ourBase, admirerBase ):
	if type(admirerBase) is not bool:
		# Admirer is online
		admirerBase.onFriendStatusChange( ourDBID, ourBase )

# Avatar.py

