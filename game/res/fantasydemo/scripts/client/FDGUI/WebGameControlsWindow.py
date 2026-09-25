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

class WebGameControlsWindow( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.WebGameControlsWindow"

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )

	def stopWebScreen( self ):
		self.active( False )
		player = BigWorld.player()
		if isinstance(player , Avatar.Avatar):
			player.removeWebScreenFocus()

	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.stopWebScreen()
		
	@PyGUIEvent( "quitButton", "onClick" )
	def onQuitClick( self ):
		self.stopWebScreen()


