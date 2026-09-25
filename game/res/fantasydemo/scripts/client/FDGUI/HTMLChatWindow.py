# -*- coding: utf-8 -*-

from HTMLWindow import HTMLWindow
from JavaScriptBridge import exposedToJavaScript
import BigWorld

class HTMLChatWindow( HTMLWindow ):
	def __init__( self, component ):
		HTMLWindow.__init__( self, component, "file:///gui/web/html/chat.html" )

	@exposedToJavaScript
	def sendMsg( self, msg ):
		BigWorld.player().handleConsoleInput( msg )

	def addChatMsg( self, msg ):
		self.js.addChatMsg( msg )


# HTMLChatWindow.py
