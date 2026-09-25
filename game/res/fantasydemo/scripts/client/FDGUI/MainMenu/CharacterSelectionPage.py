import BigWorld
import FantasyDemo
import Account
import MenuScreenSpace
import AvatarModel

from TextListPage import TextListPage
from CharacterCreatePage import CharacterCreatePage

from MainMenuConstants import *
from Helpers.BWCoroutine import *

from functools import partial

class CharacterSelectionPage( TextListPage ):
	caption = "Character Select"

	def populate( self ):
		assert isinstance( BigWorld.player(), Account.Account )
		self.addItem( "<Create Character>", self.createCharacterSelected )
		for characterInfo in BigWorld.player().characterList:
			self.addItem( characterInfo['name'], self.coCharacterSelected( characterInfo['name'] ).run )
		
	def onSelectionChanged( self, index ):
		avatarModels = self.unpackedCharacterModels
		if index >= 1 and index <= len( avatarModels ):
			modelInfo = avatarModels[index - 1]
		else:
			modelInfo = AvatarModel.defaultModel()
		MenuScreenSpace.setRealmAvatarModel( BigWorld.player().selectedRealm, modelInfo )

	def createCharacterSelected( self ):
		self.menu.push( CharacterCreatePage( self.menu ) )
		
	@BWMemberCoroutine
	def coCharacterSelected( self, characterName ):
		if BigWorld.server() is None:
			FantasyDemo.disconnectFromServer()
			return
			
		self.menu.showProgressStatus( 'Retrieving Character...' )
		yield BWWaitForCoroutine( self.menu.coShowCharacterScreen( False ) )
		BigWorld.player().characterBeginPlay( str( characterName ) )
		FantasyDemo.coProceedToLevel().run()
		
	def pageActivated( self, reason, outgoing ):
		assert isinstance( BigWorld.player(), Account.Account )
		self.unpackedCharacterModels = []
		for character in BigWorld.player().characterList:
			unpackedModel = AvatarModel.unpack( character['characterModel'] )
			self.unpackedCharacterModels.append( unpackedModel )
						
		self.coPageActivated( reason, outgoing ).run()
			
	def pageDeactivated( self, reason, incoming ):
		if reason == REASON_POPPING:
			self.coPageDeactivated( reason, incoming ).run()
		else:
			TextListPage.pageDeactivated( self, reason, incoming )
			
	def onBack( self ):
		# Sometimes we can be the top level menu (when there's only one realm).
		# So we need to be able to disconnect back to the main menu.
		if len(self.menu.stack) == 1:
			FantasyDemo.disconnectFromServer()
			return False
		else:
			return TextListPage.onBack( self )
			
	@BWMemberCoroutine
	def coPageActivated( self, reason, outgoing ):
		yield BWWaitForCondition( lambda: MenuScreenSpace.g_loaded )
		MenuScreenSpace.setRealmCamera( BigWorld.player().selectedRealm )
		yield BWWaitForCoroutine( self.menu.coShowCharacterScreen( True ) )		
		TextListPage.pageActivated( self, reason, outgoing )
		self.menu.clearStatus()
				
	@BWMemberCoroutine
	def coPageDeactivated( self, reason, incoming ):		
		yield BWWaitForCoroutine( self.menu.coShowCharacterScreen( False ) )
		TextListPage.pageDeactivated( self, reason, incoming )
		
	
	