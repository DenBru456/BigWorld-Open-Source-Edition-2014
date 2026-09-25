import BigWorld
from functools import partial
import AvatarModel
import PlayerModel
import CustomErrors

from KeepAlive import KeepAlive

from GameData import FantasyDemoData

from twisted.internet import defer

import logging

# ------------------------------------------------------------------------------
# Section: class Account
# ------------------------------------------------------------------------------

class Account( BigWorld.Proxy, KeepAlive ):

	def __init__( self ):
		BigWorld.Proxy.__init__( self )
		KeepAlive.__init__( self )
		self.isBot = False

		self.updateCharacterList()


	def onLoggedOn( self, logOnData ):
		"""Called after __init__ if we were created for a log on"""
		pass


	def onRestore( self ):
		self.updateCharacterList()


	def onEntitiesEnabled( self ):
		self.lastClientIpAddr = self.clientAddr[ 0 ]
		if self.activeCharacter == None:
			if self.accountName.startswith( 'Bot_' ):
				self.botLoggedOn()
			else:
				if self.databaseID == 0:
					self.writeToDB()
		else:
			# Re-login attempt, give client straight away
			self.activeCharacter.giveClientTo( None )
			self.giveClientTo( self.activeCharacter )

		self.cancelKeepAlive()


	def onLogOnAttempt( self, ip, port, logOnData ):
		if ip == 0:
			# from web login, let it come in regardless
			self.selectedRealm = "fantasy" # TODO: select realm from web page
			return BigWorld.LOG_ON_ACCEPT
		if self.activeCharacter != None:
			# already have a character logged on - reject
			return BigWorld.LOG_ON_REJECT
		if ip == self.lastClientIpAddr:
			return BigWorld.LOG_ON_ACCEPT
		if self.clientAddr[0] == 0:
			# if we only have a web session holding onto us, allow
			return BigWorld.LOG_ON_ACCEPT

		# default - reject re-logon
		return BigWorld.LOG_ON_REJECT

	def botLoggedOn( self ):
		self.isBot = True
		if len(self.characterList) == 0:
			self.createNewAvatar( self.accountName )
		else:
			self.characterBeginPlay( self.characterList[0]['name'] )


	def characterBeginPlay( self, characterName ):
		for character in self.persistentCharacterList:
			if character[ 'name' ] == characterName and \
				character[ 'realm' ] == self.selectedRealm:

				BigWorld.createBaseAnywhereFromDBID( character[ 'type' ],
												character[ 'databaseID' ],
												self.onLoadedAvatar )
				return

		print "Unknown character '%s' for realm '%s'." % \
				(characterName, self.selectedRealm)


	def selectRealm( self, realmID ):
		if realmID not in FantasyDemoData.REALMS:
			print "ERROR: Account.selectRealm: " \
				"received invalid realmID '%s'" % realmID
			return

		self.selectedRealm = realmID
		self.updateCharacterList()
		self.client.switchRealm( realmID, self.characterList )


	def createNewAvatar( self, avatarName ):
		deferred = self.createNewAvatarDeferred( avatarName )

		def onSuccess( values ):
			avatarMB, = values
			# Finish our work early if we are a bot
			if self.isBot:
				self.onAvatarReady( avatarMB )
				return

			self.client.createCharacterCallback( True, u'', self.characterList )

		def onFailure( failure ):
			print "Account.createNewAvatar.onFailure:", failure.value

		deferred.addCallbacks( onSuccess, onFailure )

	def createNewAvatarDeferred( self, avatarName ):
		deferred = defer.Deferred()

		def callback( newAvatarMB ):
			if newAvatarMB:
				newDeferred = newAvatarMB.writeCreatedEntity( not self.isBot )
				newDeferred.addCallbacks(
						partial( self.onCreatedNewAvatarSuccess, newAvatarMB,
							avatarName, self.selectedRealm ),
						partial( self.onCreatedNewAvatarFailure, avatarName ) )
				return newDeferred
			else:
				return self.onCreatedNewAvatarFailure( avatarName,
						CustomErrors.CreateEntityError(
							"Failed to create Avatar" ) )

		deferred.addCallback( callback )
		BigWorld.createBaseAnywhere( "Avatar",
				dict(
					playerName = avatarName,
					persistentAvatarModelData =
							PlayerModel.randomPlayerModel( self.selectedRealm ),
					realm = self.selectedRealm,
					xmppName = self.accountName ),
				deferred.callback )

		return deferred


	def onCreatedNewAvatarSuccess( self, avatarMB, avatarName, realm, returnValues ):
		print "Account.onCreatedNewAvatarSuccess:", returnValues
		(avatarDBID, avatarModelData) = returnValues

		self.persistentCharacterList.append(
			dict(
				name = avatarName,
				databaseID = avatarDBID,
				type = 'Avatar',
				realm = realm,
				characterModel = avatarModelData ) )
		self.updateCharacterList()

		print 'New character', avatarName, 'created, returning tuple'

		return (avatarMB,)


	def onCreatedNewAvatarFailure( self, avatarName, failure ):
		print 'Account: Failed to create new Avatar %s for player %s' % \
			(avatarName, self.accountName)

		if not self.isBot:
			errMsg = 'A character with name %s already exists.' %  avatarName	
			self.client.createCharacterCallback(
							False, unicode( errMsg ), self.characterList )

		return failure


	def updateCharacterList( self ):
		newCharacterList = []
		for character in self.persistentCharacterList:
			if character['realm'] == self.selectedRealm:
				newCharacter = {}
				newCharacter['name'] = character['name']
				newCharacter['characterModel'] = AvatarModel.pack(
												character['characterModel'] )
				newCharacter['realm'] = character['realm']
				newCharacterList.append( newCharacter )
		self.characterList = newCharacterList


	def onLoadedAvatar( self, avatar, dbID, wasActive ):
		if avatar != None:
			self.onAvatarReady( avatar )

		else:
			print "Account(%d).onLoadedAvatar: " \
					"Failed to load %s for player %s" % \
					(self.characterList[0]['type'], self.accountName)
			self.onAvatarReady( None )


	def onAvatarReady( self, avatarMB ):
		if not avatarMB:
			self.failLogon( "Failed to create your avatar."  )
			return

		self.activeCharacter = avatarMB
		avatarMB.associateAccount( self )

		# The Avatar will then callback onAvatarTeleportPointCheck()
		avatarMB.checkTeleportPointForAccount()


	def onAvatarTeleportPointCheck( self, isReady ):

		if not isReady:
			self.activeCharacter.destroySelf()
			self.failLogon( "Server is not yet ready for Avatars." )
			return

		self.giveClientTo( self.activeCharacter )
		if self.databaseID == 0:
			print "Writing Account to DB"
# TODO: callback for failing printing
			self.writeToDB()


	def onClientDeath( self ):
		print "Account(%d).onClientDeath" % self.id
		if not self.haveWebClient:
			self.destroy()


	def onAvatarDeath( self, avatarDBID, avatarModel ):
		if self.isDestroyed:
			# Avatar could be holding a reference to us while we're destroyed
			return

		print "Account(%d).onAvatarDeath" % self.id
		for character in self.persistentCharacterList:
			if character['databaseID'] == avatarDBID:
				character['characterModel'] = AvatarModel.unpack( avatarModel )
		self.activeCharacter = None

		if not self.haveWebClient:
			self.destroy()


	def failLogon( self, message ):
		self.client.failLogon( unicode( message ) )
		self.addTimer( 0.5 )


	def onTimer( self, id, userArg ):
		if id != self.keepAliveTimer:
			self.giveClientTo( None )
			self.destroy()
		else:
			KeepAlive.onTimer( self, id, userArg )


	#########################################
	# Web Integration methods

	def webGetCharacterList( self ):
		return ([dict(
					name       = character.name.encode( 'utf8' ),
					type       = character.type,
					realm      = character.realm,
					databaseID = character.databaseID,
					charClass  = PlayerModel.modelListToCharacterClassString(
							character.characterModel.models ) )
			for character in self.persistentCharacterList],)

	def webChooseCharacter( self, cName, cType ):
		cName = cName.decode( 'utf8' )
		found = False

		for c in self.persistentCharacterList:
			if c['name'] == cName and c['type'] == cType:
				found = True
				break

		if not found:
			return defer.fail( CustomErrors.DBError( "Cannot find character" ) )

		deferred = defer.Deferred()

		def onWebChooseCharacter( avatar, dbID, active ):
			if type( avatar ) == bool:
				deferred.errback(
						CustomErrors.DBError( "Could not load character" ) )

			print "Account(%d).webChooseCharacter: " \
					"got avatar entity: %d" % \
				(self.id, avatar.id)

			deferred.callback( (avatar, dbID) )

		BigWorld.createBaseAnywhereFromDBID( c['type'], c['databaseID'],
			onWebChooseCharacter )

		return deferred

	def webCreateCharacter( self, name ):
		self.selectedRealm = "fantasy"
		name = name.decode( 'utf8' )

		deferred = self.createNewAvatarDeferred( name )

		# Strip the tuple before passing back to the client, which is expecting
		# zero-length return values.
		deferred.addCallback( lambda x: () )

		return deferred

	# Override from KeepAlive base class
	def webLogout( self ):
		print "Account(%d).webLogout" % self.id
		if not self.hasClient and self.activeCharacter == None:
			self.destroy()

# Account.py
