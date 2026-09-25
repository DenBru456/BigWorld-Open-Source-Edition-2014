import BigWorld
import math
import random
import Math


class RandomNavigator( BigWorld.Entity ):

	TIMER_WAITING_FOR_NAVMESH = 1
	
	#-------------------------------------------------------------------------
	# Constructor.
	#-------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity .__init__( self )
		self.destination = self.position
		self.addTimer( 5.0, 0, RandomNavigator.TIMER_WAITING_FOR_NAVMESH )

	#-------------------------------------------------------------------------
	# This method is called when a timer expires.
	#-------------------------------------------------------------------------
	def onTimer(self, timerId, userId):
		if userId == RandomNavigator.TIMER_WAITING_FOR_NAVMESH:
			if self.canNavigateTo( self.position ) == None:
				self.addTimer( 5.0, 0, RandomNavigator.TIMER_WAITING_FOR_NAVMESH )
			else:
				self.navigateStep( self.destination, 5.0, 10.0 )


	#-------------------------------------------------------------------------
	# This method is called when we've finished moving to a point.
	#-------------------------------------------------------------------------
	def onMove(self, controllerId, userId):
		if ( self.position - self.destination ).length > 0.1:
			self.navigateStep( self.destination, 5.0, 10.0 )
		else:
			self.destination = None
			while self.destination == None:
				randomDestination = ( 
					self.position.x + random.randrange(-400, 400, 1.0),
					self.position.y,
					self.position.z + random.randrange(-400, 400, 1.0) )
				self.destination = self.canNavigateTo( randomDestination )

			self.navigateStep( self.destination, 5.0, 10.0 )

# RandomNavigator.py
