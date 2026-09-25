import BigWorld
import chapters
import tutorial


class Avatar( BigWorld.Entity ):

	def __init__( self, nearbyEntity ):
		BigWorld.Entity.__init__( self )


	if tutorial.includes( chapters.CHAT_CONSOLE ):
		def say( self, id, message ):
			if self.id == id:
				print "%d says: '%s'" % (self.id, message)
				self.otherClients.say( message )

# Avatar.py
