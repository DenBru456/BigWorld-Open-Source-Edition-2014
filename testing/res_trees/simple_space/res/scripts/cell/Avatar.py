import BigWorld
import chapters


class Avatar( BigWorld.Entity ):

	def __init__( self, nearbyEntity ):
		BigWorld.Entity.__init__( self )

	def chat( self, source, msg ):
		print "playerName is", self.playerName
		print 'Got message "' + msg + '"'
		self.otherClients.chat( msg )

	def say( self, id, message ):
		if self.id == id:
			print "%d says: '%s'" % (self.id, message)
			self.otherClients.say( message )

# Avatar.py
