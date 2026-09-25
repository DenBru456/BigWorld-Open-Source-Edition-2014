import BigWorld
import FantasyDemo

from TextInputPage import TextInputPage
from functools import partial

class CharacterCreatePage( TextInputPage ):
	caption = "Enter Character Name:"

	def __init__( self, menu ):
		TextInputPage.__init__( self, menu )
		
	def onEnter( self, value ):
		characterName = value.strip()
		if characterName == "":
			return
			
		self.menu.showProgressStatus( 'Creating Character...' )
		BigWorld.player().createNewCharacter( str(characterName), self.finishCharacterCreate )
	
	def finishCharacterCreate( self, succeded, msg ):
		if succeded:
			self.menu.showStatus( 'Character Created' )			
			BigWorld.callback( 1.5, lambda:self.menu.pop() )
		else:
			# TODO: Make error status's
			self.menu.showPromptStatus( msg, lambda:self.menu.pop() )

		
	
	
		