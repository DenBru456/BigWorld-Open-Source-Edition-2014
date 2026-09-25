import BigWorld

from bwdebug import *
from Helpers.BWCoroutine import *

from TextListPage import TextListPage
from ValueChooserPage import ValueChooserPage
from RestartClientPage import RestartClientPage

import Util

from functools import partial

def getStatusString( settingIndex ):
	graphicSetting = BigWorld.graphicsSettings()[settingIndex]
	activeIdx = graphicSetting[1]
	result = "Error"
	try:
		result = "[" + graphicSetting[2][activeIdx][3] + "]"
	
	except IndexError:
		ERROR_MSG( "Error getting status string for graphics setting %s"
			% (graphicSetting[0],) )

	return result
	

class AdvancedSettingsPage( TextListPage ):
	caption = "Advanced Settings"

	def populate( self ):
		graphicSettings = BigWorld.graphicsSettings()
		
		for index, (settingId, active, options, desc, advanced, needsRestart, delayed) in enumerate(graphicSettings):
			self.addItem( str(desc)+"...", 
					partial( self.settingSelected, index, settingId ),
					getStatusString( index ) )
		
	def settingSelected( self, settingIndex, settingId ):
		setting = BigWorld.graphicsSettings()[ settingIndex ]
		active  = setting[1]
		options = setting[2]
		desc = setting[3]
		
		items = [
			(desc, index if supported else None)
			for index, (option, supported, advanced, desc)
			in enumerate(options) ]
		
		page = ValueChooserPage( self.menu, 
					items, active, 
					partial( self.setGraphicsSetting, settingIndex, settingId ) )
		self.menu.push( page )
		
	def setGraphicsSetting( self, settingIndex, settingId, optionIndex ):
		BigWorld.setGraphicsSetting( settingId, optionIndex )
		self.repopulate()
		
	def onBack( self ):
		Util.applyGraphicsSettingsOrRestart( self.menu, self.menu.pop )
		

