# -*- coding: utf-8 -*-

from Helpers.PyGUI import DraggableWindow
from Helpers.PyGUI import InternalBrowser
from Helpers.PyGUI import PyGUIEvent
from functools import partial
from JavaScriptBridge import JavaScriptBridge
import BigWorld
import random
import FantasyDemo

class HTMLWindow( DraggableWindow, JavaScriptBridge ):
	def __init__( self, component, uri ):
		DraggableWindow.__init__( self, component )
		self.component.script = self
		self.uri = uri
		self.alreadyInit = False
		#get a callback upon resolution override change
		FantasyDemo.rds.fdgui.addResolutionOverrideHandler( self )
		self.fullyInitialised = True
		
	def init( self ):
		if not self.alreadyInit:
			self.addObserver()
		self.reload()
		self.alreadyInit = True

	def reload( self ):
		self._getInternalBrowserScript().navigate( self.uri )

	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )

	def _getInternalBrowserScript(self):
		return self._getInternalBrowser().script

	def _getInternalBrowser(self):
		return self.component.internalBrowser

	def onClick( self, uri ):
		self._getInternalBrowserScript().navigate( event.uri )

	def addObserver(self):
		self._getInternalBrowserScript().addObserver( self )
		self._getInternalBrowserScript().addFocusObserver( self )

	# Called by child who takes the focus
	# so we can inform other child of losing key focus
	def focus( self, state ):
		pass

	def updateResolutionOverride(self):
		pass

	def invokeCallback( self ):
		pass
		
# HTMLWindow.py
