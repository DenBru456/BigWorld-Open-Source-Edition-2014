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

from Helpers.PyGUI import PyGUIEvent
from Helpers.PyGUI import EditField
from FDToolTip import ToolTipInfo
import FantasyDemo


class WebWindow( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.WebWindow"

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.component.script = self
		self.timeCallback = None


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )

	@PyGUIEvent( "backBox", "onClick" )
	def onBackBoxClick( self ):
		self._getInternalBrowserScript().navigateBack()

	@PyGUIEvent( "forwardBox", "onClick" )
	def onForwardBoxClick( self ):
		self._getInternalBrowserScript().navigateForward()

	def _getInternalBrowserScript(self):
		return self._getInternalBrowser().script

	def _getEditFieldScript(self):
		return self._getEditField().script

	def _getInternalBrowser(self):
		for child in self.component.children:
			if isinstance(child[1].script, InternalBrowser):
				return child[1]

	def _getEditField(self):
		return self.component.editField

	def onClick(self, text):
		self._getInternalBrowserScript().navigate(text)

	def setEditEventHandler(self):
		self._getEditFieldScript().eventHandler = self

	def onChangeAddressBar( self, url ):
		if not PyGUI.isFocusedComponent( self._getEditFieldScript().component ):
			usedURL = url[0:self._getEditFieldScript().maxLength]
			if self._getEditField().text != usedURL:
				self._getEditFieldScript().setText(usedURL)
		return True

	def addObserver(self):
		self._getInternalBrowserScript().addObserver(self)

