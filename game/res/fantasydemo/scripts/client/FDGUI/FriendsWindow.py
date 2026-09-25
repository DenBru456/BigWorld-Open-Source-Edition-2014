# -*- coding: utf-8 -*-

from HTMLWindow import HTMLWindow
from JavaScriptBridge import exposedToJavaScript
import BigWorld

class FriendsWindow( HTMLWindow ):
	def __init__( self, component ):
		HTMLWindow.__init__( self, component, "file:///gui/web/html/friends.html" )

	@exposedToJavaScript
	def addFriendClicked( self ):
		print "addFriendClicked"
		# self.addFriend( "paul.murph@gmail.com", "xmpp", "online" )

	@exposedToJavaScript
	def setAccountsClicked( self ):
		print "setAccountsClicked"
		# self.addFriend( "andred@bigworldtech.com", "msn", "offline" )

	def addFriend( self, name, transport, friendType ):
		self.js.addFriend( name, transport, friendType )

	def addEntity( self, name, isFriend ):
		self.js.addEntity( name, isFriend )

# FriendsWindow.py
