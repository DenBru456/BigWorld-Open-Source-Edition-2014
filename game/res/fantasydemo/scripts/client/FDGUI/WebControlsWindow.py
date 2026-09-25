# -*- coding: utf-8 -*-

import FantasyDemo
import BigWorld
import Helpers.PyGUI as PyGUI
from functools import partial
from bwdebug import ERROR_MSG
import types
import Cursor
import GUI
from Helpers.PyGUI import InternalBrowser
import Avatar
from Helpers.PyGUI import PyGUIEvent
from Helpers.PyGUI import EditField
from FDToolTip import ToolTipInfo
import FantasyDemo
import Avatar

class WebControlsWindow( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.WebControlsWindow"

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )
		player = BigWorld.player()
		if isinstance(player , Avatar.Avatar):
			player.removeWebScreenFocus()
		
	@PyGUIEvent( "backBox", "onClick" )
	def onBackBoxClick( self ):
		player = BigWorld.player()
		if isinstance(player , Avatar.Avatar):
			if player.currentWebScreen != None:
				player.currentWebScreen.navigateBack()

	@PyGUIEvent( "forwardBox", "onClick" )
	def onForwardBoxClick( self ):
		player = BigWorld.player()
		if isinstance(player , Avatar.Avatar):
			if player.currentWebScreen != None:
				player.currentWebScreen.navigateForward()

	def _getEditFieldScript(self):
		return self._getEditField().script


	def _getEditField(self):
		return self.component.editField

	def getKeyFocus(self):
		keyFocus = False
		keyFocus = keyFocus or self._getEditFieldScript().getKeyFocus()
		return keyFocus

	def setEditEventHandler(self):
		self._getEditFieldScript().eventHandler = self

	def onClick(self, text):
		player = BigWorld.player()
		if isinstance(player , Avatar.Avatar):
			if player.currentWebScreen != None:
				player.currentWebScreen.navigate(text)

	def addObserver(self):
		self._getEditFieldScript().addFocusObserver(self)


