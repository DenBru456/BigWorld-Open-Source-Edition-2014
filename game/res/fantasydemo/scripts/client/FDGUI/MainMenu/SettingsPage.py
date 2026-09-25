import BigWorld
import FantasyDemo

from GraphicsPresets import GraphicsPresets

import Util

from TextListPage import TextListPage

from VideoSettingsPage import VideoSettingsPage
from GraphicsSettingsPage import GraphicsSettingsPage

def getGraphicDetailStatus():
	presets = GraphicsPresets()
	if presets.selectedOption >= 0:
		return "[" + presets.entryNames[ presets.selectedOption ] + "]"
	else:
		return "[Custom]"

class SettingsPage( TextListPage ):
	caption = "Settings"
	
	def populate( self ):
		self.addItem( 'Video...', self.selectVideo )
		self.addItem( 'Graphics detail...', self.selectGraphicsDetail, getGraphicDetailStatus() )
		self.addItem( 'Auto-Detect Graphics Detail', self.selectAutoGraphicsDetail )
		
	def selectVideo( self ):
		self.menu.push( VideoSettingsPage(self.menu) )
		
	def selectGraphicsDetail( self ):
		self.menu.push( GraphicsSettingsPage(self.menu) )
		
	def selectAutoGraphicsDetail( self ):
		presets = GraphicsPresets()
		optionIndex = BigWorld.autoDetectGraphicsSettings()
		presets.selectGraphicsOptions( optionIndex )
		FantasyDemo.rds.console.script.addMsg( "The most optimal settings have been selected for your video card to balance performance and fidelity.", 0 )
		Util.applyGraphicsSettingsOrRestart( self.menu )
		self.repopulate()
		
		
