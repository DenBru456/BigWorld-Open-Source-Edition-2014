import BigWorld
import FantasyDemo

import Util

from Helpers.BWCoroutine import *

from GraphicsPresets import GraphicsPresets

from TextListPage import TextListPage
from RestartClientPage import RestartClientPage
from AdvancedSettingsPage import AdvancedSettingsPage
from functools import partial


class GraphicsSettingsPage( TextListPage ):
	caption = "Graphics Settings"

	def populate( self ):
		presets = GraphicsPresets()
		advancedMsg = 'Advanced Settings...'
		if presets.selectedOption == -1:
			advancedMsg += ' *'
			
		for i in range( len(presets.entryNames) ):
			presetMsg = presets.entryNames[i]
			if i == presets.selectedOption:
				presetMsg += ' *'
				
			self.addItem( presetMsg, partial( self.togglePresets, presets, i ) )
				
		self.addItem( advancedMsg, self.showAdvancedSettingsMenu )
				
	def togglePresets( self, presets, optionIndex ):
		presets.selectGraphicsOptions( optionIndex )
		Util.applyGraphicsSettingsOrRestart( self.menu, self.repopulate )
		
			
	def showAdvancedSettingsMenu( self ):
		self.menu.push( AdvancedSettingsPage( self.menu ) )
			
	
	def pageDeactivated( self, reason, incoming ):
		BigWorld.savePreferences()
		TextListPage.pageDeactivated( self, reason, incoming )
	
	