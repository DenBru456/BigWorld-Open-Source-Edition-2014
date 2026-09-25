import BigWorld
import FantasyDemo
import AvatarModel
from Helpers.CallbackHelpers import *


class Account( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.loadedModels = None
		self.selectedRealm = ""

	# --- Logon  ---
	def failLogon( self, message ):
		print "failLogon: %s" % message
		FantasyDemo.addMsg( message )
		BigWorld.disconnect()

	def logMessage( self, msg ):
		FantasyDemo.addLogMessage( msg )

	def characterBeginPlay( self, cName ):
		self.base.characterBeginPlay( unicode( cName ) )

	def createNewCharacter( self, characterName, callback ):
		self.base.createNewAvatar( unicode( characterName ) )
		self.createCharacterRequesterCallback = callback

	def createCharacterCallback( self, succeeded, msg, characterList ):
		self.setCharacterList( characterList )
		self.createCharacterRequesterCallback( succeeded, msg )

	def switchRealm( self, selectedRealm, characterList ):
		self.selectedRealm = selectedRealm
		self.setCharacterList( characterList )

	def setCharacterList( self, characterList ):
		self.characterList = characterList
		resources = []
		for character in self.characterList:
			unpackedAvatarModel = AvatarModel.unpack( character['characterModel'] )
			resources.extend( AvatarModel.getPrerequisites( unpackedAvatarModel ) )
		BigWorld.loadResourceListBG( tuple( resources ), self.onModelsLoaded )

	@IgnoreCallbackIfDestroyed
	def onModelsLoaded( self, resourceRefs ):
		self.loadedModels = resourceRefs

class PlayerAccount( Account ):
	def handleKeyEvent( self, event ):
		pass


# Account.py
