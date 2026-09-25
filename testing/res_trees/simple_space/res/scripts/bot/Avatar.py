import logging

import BigWorld

class Avatar( BigWorld.Entity ):

	def onBecomePlayer( self ):
		self.__class__ = PlayerAvatar


class PlayerAvatar( BigWorld.Entity ):

	def __init__( self ):
		self.friendStatus = None

	def onBecomeNonPlayer( self ):
		self.__class__ = Avatar

	def chat( self, msg ):
		self.chatMsg = msg

	def setFriendStatus( self, idx, isOnline ):
		self.friendStatus = (idx, isOnline)

# Avatar.py
