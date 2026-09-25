import BigWorld
import chapters
import ThrottledMethods

class Avatar( BigWorld.Entity ):

	def __init__( self, nearbyEntity ):
		BigWorld.Entity.__init__( self )
		self.throttledOwnCell = 0
		self.throttledAllCells = 0


	def say( self, id, message ):
		if self.id == id:
			print "%d says: '%s'" % (self.id, message)
			self.otherClients.say( message )
			
	@ThrottledMethods.hardThresholdCell( 2.0, 0.5 )
	def testThrottlingOwnClient( self, callerID ):
		self.throttledOwnCell += 1


	@ThrottledMethods.hardThresholdCellAllClients( 2.0, 0.5 )
	def testThrottlingAllClients( self, callerID ):
		self.throttledAllCells += 1

# Avatar.py
