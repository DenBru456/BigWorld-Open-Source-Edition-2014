import BigWorld

class TeleportPoint( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def updatePosition( self, position ):
		self.position = position

	def tryToTeleport( self, spaceName, pointName, mailbox, spaceID ):
		if spaceID == self.spaceID:
			mailbox.teleportTo( spaceName, pointName )

# TeleportPoint.py
